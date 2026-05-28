# C330 — Swap Space & LVM Demo Guide (RHEL 9)

**For lecturer demonstration in a blank RHEL 9 lab.**
Covers Lesson 11 (Manage Swap Space) and Lesson 12 (Logical Volume Management).

> Every command below is meant to be typed live. After each block there is a short
> *"Tell the students"* note explaining **why** the command matters and a
> **real-world** scenario so the content makes sense beyond the lab.

---

## 0. Before You Start — Prepare the Lab

Confirm you are `root` and that you have a clean second disk to play with.

```bash
whoami                 # should print: root
lsblk                  # list all block devices and their layout
free -h                # current RAM + swap summary
```

**Tell the students:** `lsblk` is the single most important "where am I" command in
storage work. `sda` is normally the OS disk — **never touch it**. We will only work
on the *second* disk (`sdb`) and, for LVM, a third (`sdc`) if available.

> ⚠️ **Safety rule for the whole session:** every destructive command we run targets
> `/dev/sdb` or `/dev/sdc`. If your `lsblk` shows the OS living on `sdb`, STOP and
> attach a fresh disk. In production a wrong device name destroys live data.

If you need a clean disk during the demo:

```bash
wipefs -a /dev/sdb*    # erases partition-table/filesystem signatures on sdb
wipefs -a /dev/sdc*    # (if you have a third disk)
lsblk                  # verify the disks are now empty
```

---

# PART 1 — SWAP SPACE (Lesson 11)

## 1.1 What problem are we solving?

**Tell the students:** RAM is fast but limited. Swap is disk space the kernel uses to
park *inactive* memory pages when RAM gets tight. **Virtual memory = RAM + swap.**

> **Real world:** A web server with 8 GB RAM gets a sudden traffic spike. Instead of
> the kernel's OOM-killer terminating your database, idle pages spill into swap and the
> server limps through the spike. Swap is a *safety cushion*, **not** a substitute for
> buying more RAM — disk is ~1000× slower than RAM.

Recommended swap sizing (from the Red Hat guide):

| RAM in system | Recommended swap | With hibernation |
|---|---|---|
| ≤ 2 GB | 2× RAM | 3× RAM |
| 2–8 GB | = RAM | 2× RAM |
| 8–64 GB | ≥ 4 GB | 1.5× RAM |
| > 64 GB | ≥ 4 GB | not recommended |

Check what you have now:

```bash
free -h                # look at the Swap: row
swapon -s              # show currently active swap devices/files
swapon --show          # newer, friendlier output (same info)
cat /proc/swaps        # the raw source swapon reads from
```

---

## 1.2 Two ways to add swap

There are two flavours of swap: a **swap partition** (carved out of a disk) and a
**swap file** (an ordinary file). We'll demo **both**.

---

### 1.2a Swap using a PARTITION

**Step 1 — Create a small partition on the spare disk.**

```bash
fdisk /dev/sdb
```

Inside `fdisk` type, in order:
```
n        # new partition
p        # primary
1        # partition number 1
<Enter>  # accept default first sector
+512M    # make it 512 MB
w        # write changes to disk and quit
```

Refresh the kernel's view of the partition table:

```bash
partprobe /dev/sdb     # tell the kernel to re-read the partition table
lsblk /dev/sdb         # confirm sdb1 now exists
```

**Tell the students:** type code `82` flags the partition's *intended* purpose. The
disk doesn't actually become swap until we write a swap signature in the next step.

**Step 2 — Write the swap signature.**

```bash
mkswap /dev/sdb1       # formats the partition as swap (writes a UUID + header)
```

**Step 3 — Activate and verify.**

```bash
swapon /dev/sdb1       # turn the swap on NOW (this boot only)
swapon -s              # sdb1 should appear in the list
free -h                # Swap total should have grown
```

**Step 4 — Turn it off again (so we can reuse the disk for LVM later).**

```bash
swapoff /dev/sdb1
swapon -s              # sdb1 is gone
```

> **Real world:** Swap partitions are the classic approach — created at install time,
> fixed in size, slightly faster because the blocks are contiguous. The downside is you
> can't easily resize a partition later, which is exactly why swap *files* exist.

---

### 1.2b Swap using a FILE

This is more flexible — you can create/resize swap any time without repartitioning.

**Step 1 — Create the empty file (256 MB).**

```bash
dd if=/dev/zero of=/var/local/swapfile bs=1M count=256
```

**Tell the students:** `dd` copies blocks. `if` = input file (`/dev/zero` = endless
zeros), `of` = output file. We grow the file to 256 MB (256 × 1 MB blocks).

> ⚠️ `dd` is nicknamed **"Disk Destroyer"** — mixing up `if` and `of` overwrites a real
> disk. Always read the line twice before pressing Enter.

Verify size:

```bash
ls -lh /var/local/swapfile
```

**Step 2 — Write the swap signature.**

```bash
mkswap /var/local/swapfile
```

It will warn about insecure permissions. Fix them — a swap file holds memory contents,
so only root may read it:

```bash
chmod 600 /var/local/swapfile
ls -l /var/local/swapfile      # should now show -rw-------
```

**Step 3 — Activate with a priority.**

```bash
free -h                              # BEFORE
swapon -p 2 /var/local/swapfile      # activate with priority 2
swapon -s                            # file now listed, Priority 2
free -h                              # AFTER — Swap total grew
```

**Step 4 — See swap actually get used (optional, fun demo).**

In one terminal start a live watch:

```bash
watch swapon -s
```

In a second terminal, stress memory (adjust `4G` to your VM's RAM):

```bash
head -c 4G /dev/zero | tail
```

**Tell the students:** Watch the **Used** column climb on the watch screen as the kernel
pushes pages into swap. This is virtual memory working in real time.

---

## 1.3 Swap priority

```bash
swapon -p 1 /var/local/swapfile   # re-prioritise (must swapoff/swapon, or set on activate)
swapon -s                         # check Priority column
```

**Tell the students:** **Higher number = used first.** So `3 > 1 > -1 > -3`. If you have
fast SSD swap and slow HDD swap, give the SSD the higher priority so the kernel reaches
for it first.

> **Real world:** Spread swap across several fast disks with equal priority and the
> kernel stripes across them (like RAID-0 for swap) for better throughput.

---

## 1.4 Make swap survive a reboot (persistent)

Active swap disappears on reboot unless it's in `/etc/fstab`.

```bash
# View current fstab first
cat /etc/fstab

# Append a swap-file entry (priority 2)
echo "/var/local/swapfile  swap  swap  defaults,pri=2  0 0" >> /etc/fstab

# Re-read fstab so systemd knows about the change
systemctl daemon-reload

# Test fstab WITHOUT rebooting: turn all swap off then on from fstab
swapoff -a
swapon -a
swapon -s        # the file should come back automatically
```

**Tell the students:** The six fields are *device, mountpoint, type, options, dump,
fsck-pass*. For swap the mountpoint is literally the word `swap`.

> ⚠️ A typo in `/etc/fstab` can stop a server from booting. Always run `swapon -a`
> (or `mount -a`) to validate the line *before* you reboot for real.

**Step — Deactivate cleanly.**

```bash
swapoff /var/local/swapfile
swapon -s
free -h
```

**Cleanup so the disk is free for Part 2:**

```bash
# Remove the persistent line (edit it out)
vi /etc/fstab          # delete the /var/local/swapfile line, save (:wq)
rm -f /var/local/swapfile
swapoff /dev/sdb1 2>/dev/null
wipefs -a /dev/sdb*    # clear sdb so LVM starts clean
lsblk
```

---

# PART 2 — LOGICAL VOLUME MANAGEMENT (Lesson 12)

## 2.1 Why LVM exists

**Tell the students:** Plain partitions are rigid — once `/data` is 100 GB it's stuck at
100 GB unless you back up, repartition and restore. **LVM adds a flexible layer** so you
can grow, shrink, pool disks, and snapshot *while the system stays online*.

The LVM stack, bottom to top:

```
Hard drive / partition  ─►  PV (Physical Volume)
                                 │
        one or more PVs pooled into ─►  VG (Volume Group)
                                              │
              VG carved into virtual partitions ─►  LV (Logical Volume)
                                                          │
                                  filesystem + mountpoint ─►  /mnt/...
```

| Term | Meaning |
|---|---|
| **PV** | Physical Volume — a disk/partition labelled for LVM |
| **VG** | Volume Group — a pool made of one or more PVs |
| **LV** | Logical Volume — a flexible "partition" cut from a VG |
| **PE / LE** | Physical / Logical Extents — the fixed-size blocks LVM allocates in (default 4 MiB) |

> **Real world:** A database LV is filling up. With LVM you add a new disk to the VG and
> grow the LV + filesystem live — zero downtime. With classic partitions that's an outage.

---

## 2.2 Step 1 — Prepare the physical device (partitions)

We'll create three partitions on `/dev/sdb` and tag them as **Linux LVM**.

```bash
fdisk /dev/sdb
```

Inside `fdisk`, create **1 primary (128M)** and an **extended** containing **two logical
(256M, 512M)** partitions:

```
n  p  1  <Enter>  +128M     # sdb1 primary 128M
n  e  2  <Enter>  +1G       # sdb2 extended container (~1G)
n     <Enter>     +256M     # sdb5 logical 256M
n     <Enter>     +512M     # sdb6 logical 512M
```

Now flag every data partition as type **8e (Linux LVM)**:

```
t  1  8e        # set sdb1 -> Linux LVM
t  5  8e        # set sdb5 -> Linux LVM
t  6  8e        # set sdb6 -> Linux LVM
p               # print the table to review
w               # write and quit
```

Refresh the kernel and check:

```bash
partprobe /dev/sdb
lsblk /dev/sdb
fdisk -l /dev/sdb        # Type column should read "Linux LVM" for 1,5,6
```

**Tell the students:** the `8e` type isn't strictly required for LVM to work, but it
*documents intent* and protects the partition from being grabbed by other tools.

> **Alternative with `parted`** (does the same job, scriptable):
> ```bash
> parted /dev/sdb mkpart primary xfs 2048s 128MB
> parted /dev/sdb set 1 lvm on
> udevadm settle          # wait for device nodes to appear
> ```

---

## 2.3 Step 2 — Create Physical Volumes (PV)

```bash
pvcreate /dev/sdb1 /dev/sdb5 /dev/sdb6     # label all three as PVs
pvs                                        # short summary
pvdisplay /dev/sdb6                        # full detail of one PV
```

**Tell the students:** `pvcreate` writes an LVM label + metadata area to each partition.
`pvs` is the quick view; `pvdisplay` is the verbose view. Note PSize/PFree.

---

## 2.4 Step 3 — Create a Volume Group (VG)

Pool two of the PVs into a group called `my_first_vg`:

```bash
vgs                                        # what VGs already exist (rhel is the OS one)
vgcreate my_first_vg /dev/sdb1 /dev/sdb5   # pool sdb1 + sdb5
vgs                                        # my_first_vg now listed
vgdisplay my_first_vg                      # note VG Size, PE Size (4 MiB), Total PE
```

**Tell the students:** The VG is now a single storage *pool*. Its size = sum of its PVs.
The **PE Size** (4 MiB default) is the smallest unit LVM allocates in — important when we
size LVs by *extents* later.

> **Real world:** Think of the VG as a tank of water filled from several taps (disks).
> You no longer care which physical disk a logical volume sits on.

---

## 2.5 Step 4 — Create a Logical Volume (LV)

Cut a 200 MB LV from the pool:

```bash
lvs                                                       # existing LVs
lvcreate -L 200M -n my_first_lv my_first_vg               # -L size, -n name
lvdisplay /dev/my_first_vg/my_first_lv                    # full detail
```

**Tell the students:** `-L 200M` sizes by capacity; you can also size by extents with
`-l` (e.g. `-l 50` = 50 × 4 MiB = 200 MiB). The LV appears as a device under both
`/dev/my_first_vg/` and `/dev/mapper/`.

---

## 2.6 Step 5 — Put a filesystem on it and mount

```bash
mkfs -t xfs /dev/my_first_vg/my_first_lv   # format as XFS (RHEL 9 default)
mkdir /lv_mount                            # create a mountpoint
mount /dev/my_first_vg/my_first_lv /lv_mount
df -h | grep lv_mount                      # confirm it's mounted & sized
mount | grep my_first                      # see mount options + type
```

**Tell the students:** Notice the mounted name shows as `/dev/mapper/my_first_vg-my_first_lv`.
That's the **Device Mapper** — the kernel framework LVM uses; every LV gets a node under
`/dev/mapper`.

Write some data to prove it's a real filesystem:

```bash
cd /lv_mount
touch file{1..10}
cp /etc/passwd .
ls -l
cd ~
```

---

## 2.7 Step 6 — Persistent mount

```bash
echo "/dev/mapper/my_first_vg-my_first_lv /lv_mount xfs defaults 0 0" >> /etc/fstab
systemctl daemon-reload
umount /lv_mount && mount -a       # test the fstab line without rebooting
df -h | grep lv_mount              # back, mounted from fstab
```

> **Best practice:** in production use `UUID=...` (from `blkid`) instead of the device
> path, so the mount survives device-name changes.

---

## 2.8 The headline feature — GROW the volume online

This is the moment that sells LVM. We'll add a disk, grow the VG, grow the LV, then grow
the filesystem — **all while it stays mounted and in use.**

**Step A — Add the third PV into the VG.**

```bash
pvs ; vgs ; lvs                    # snapshot the "before" state
vgextend my_first_vg /dev/sdb6     # add the 512M PV to the pool
vgs                                # VFree has grown
```

**Step B — Extend the LV (add 500 MB).**

```bash
df -h | grep my_first_lv                                   # size BEFORE
lvextend -L +500M /dev/my_first_vg/my_first_lv             # or:  -l +125  (125 extents)
lvs                                                        # LSize grew, but...
df -h | grep my_first_lv                                   # ...df still shows OLD size!
```

**Tell the students:** the *container* (LV) is bigger, but the *filesystem* inside
doesn't know yet. We must grow the filesystem too.

**Step C — Grow the filesystem on the fly.**

```bash
# XFS: grow by MOUNTPOINT, online only
xfs_growfs /lv_mount
df -h | grep my_first_lv     # NOW df shows the new larger size
```

| Filesystem | Grow command | Argument | Notes |
|---|---|---|---|
| XFS (RHEL default) | `xfs_growfs` | the **mountpoint** | online only, **grow only** |
| ext2/3/4 | `resize2fs` | the **LV device** | online **and** offline, can shrink |

> 💡 Shortcut: `lvextend -r -L +500M <lv>` resizes the LV **and** the filesystem in one
> step (`-r` = resize fs automatically).

> **Real world:** "Our `/var/lib/mysql` is at 95%." With LVM: add disk → `vgextend` →
> `lvextend -r`. Done in under a minute, no maintenance window, no restart.

---

## 2.9 Tear-down (clean up in the correct order)

Order matters: **unmount → remove LV → remove VG → remove PV labels.**

```bash
# 1. Remove the fstab line first (avoid a broken boot)
vi /etc/fstab        # delete the my_first_vg line, save

# 2. Unmount
umount /lv_mount

# 3. Remove the logical volume
lvremove /dev/my_first_vg/my_first_lv      # answer y

# 4. Remove the volume group
vgremove my_first_vg                       # answer y

# 5. Wipe the PV labels
pvremove /dev/sdb1 /dev/sdb5 /dev/sdb6

# 6. (Optional) shrink an existing VG by removing a PV
#    vgreduce <vg> /dev/sdbX

# 7. Nuke the whole disk back to blank
wipefs -a /dev/sdb*
lsblk                # sdb should be empty again
```

**Tell the students:** if you remove things out of order (e.g. `pvremove` a disk still in
a VG) LVM refuses — it's protecting your data. The teardown is the create steps in reverse.

---

## 2.10 (Info only) Stratis — the modern alternative

**Tell the students:** Red Hat also ships **Stratis**, which layers pools + filesystems
with snapshots on top of LVM/XFS but with simpler commands. *Mention it exists, but this
module's focus is LVM* — Stratis is for awareness only.

---

# Quick Command Cheat-Sheet

**Swap**
```
mkswap <dev|file>          # write swap signature
swapon  -p N <dev|file>    # activate (priority N)
swapoff <dev|file>         # deactivate
swapon -s  /  free -h      # verify
```

**LVM (bottom → top)**
```
pvcreate  pvs  pvdisplay        # Physical Volume
vgcreate  vgextend  vgreduce    # Volume Group
vgs  vgdisplay  vgremove
lvcreate  lvextend  lvs         # Logical Volume
lvdisplay  lvremove
mkfs -t xfs <lv> ; mount        # filesystem
xfs_growfs <mountpoint>         # grow XFS
resize2fs <lv>                  # grow/shrink ext4
```

**Always**
```
lsblk          # see the layout
partprobe      # re-read partition table
wipefs -a      # blank a disk (DANGER)
```

---

### One-line summary to leave on the board
> **Swap** = extra (slow) memory cushion on disk. **LVM** = a flexible storage layer
> (PV → VG → LV) that lets you grow, pool, and snapshot disks live — the reason every
> serious Linux server uses it.
