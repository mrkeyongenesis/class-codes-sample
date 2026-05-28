# C330 — Swap Space & LVM Demo Guide (RHEL 9)

**For lecturer demonstration in a RHEL 9 lab.**
Covers Lesson 11 (Manage Swap Space) and Lesson 12 (Logical Volume Management).

> Every command below is meant to be typed live. After each block there is a short
> *"Tell the students"* note explaining **why** the command matters and a
> **real-world** scenario so the content makes sense beyond the lab.

> **This guide matches the lab disk layout:**
> `sdb1` = 128M **Linux (83)**, `sdb5` = 125M **Linux LVM (8e)**, `sdb6` = 50M **Linux LVM (8e)**,
> with `sdc` (2G) available as a spare disk to extend the VG.

---

## 0. Before You Start — Check the Lab

Confirm you are `root` and look at the disk layout.

```bash
whoami                 # should print: root
lsblk                  # list all block devices and their layout
free -h                # current RAM + swap summary
```

**Expected `lsblk` (your lab):**
```
sda                    20G   disk
├─sda1     600M  part  /boot/efi
├─sda2       1G  part  /boot
└─sda3    18.4G  part
  ├─rhel-root  16.4G lvm  /
  └─rhel-swap     2G lvm  [SWAP]
sdb                     2G   disk
├─sdb1     128M  part        <- will be Linux (83)
├─sdb2       1K  part        <- extended container
├─sdb5     125M  part        <- will be Linux LVM (8e)
└─sdb6      50M  part        <- will be Linux LVM (8e)
sdc                     2G   disk        <- spare, used later to extend the VG
```

**Tell the students:** `lsblk` is the "where am I" command in storage work. `sda` is the
OS disk — **never touch it**. We work only on `sdb` and `sdc`.

> ⚠️ **Safety rule for the whole session:** every command targets `/dev/sdb` or
> `/dev/sdc`. If your OS ever lives on `sdb`, STOP. A wrong device name destroys live data.

---

# PART 1 — SWAP SPACE (Lesson 11)

## 1.1 What problem are we solving?

**Tell the students:** RAM is fast but limited. Swap is disk space the kernel uses to
park *inactive* memory pages when RAM gets tight. **Virtual memory = RAM + swap.**

> **Real world:** A web server with 8 GB RAM hits a traffic spike. Instead of the
> OOM-killer terminating your database, idle pages spill into swap and the server
> survives. Swap is a *safety cushion*, **not** a replacement for more RAM — disk is
> ~1000× slower than RAM.

Recommended swap sizing (Red Hat guide):

| RAM in system | Recommended swap | With hibernation |
|---|---|---|
| <= 2 GB | 2x RAM | 3x RAM |
| 2-8 GB | = RAM | 2x RAM |
| 8-64 GB | >= 4 GB | 1.5x RAM |
| > 64 GB | >= 4 GB | not recommended |

Check what you have now:

```bash
free -h                # look at the Swap: row
swapon -s              # show active swap devices/files
swapon --show          # newer friendlier output
cat /proc/swaps        # raw source swapon reads from
```

---

## 1.2 Swap using a FILE

We'll demo the **swap file** method (flexible, no repartitioning needed).

**Step 1 — Create the empty file (256 MB).**

```bash
dd if=/dev/zero of=/var/local/swapfile bs=1M count=256
ls -lh /var/local/swapfile
```

**Tell the students:** `dd` copies blocks. `if` = input (`/dev/zero` = endless zeros),
`of` = output. We grow the file to 256 MB.

> ⚠️ `dd` is nicknamed **"Disk Destroyer"** — swapping `if` and `of` overwrites a real
> disk. Read the line twice before Enter.

**Step 2 — Write the swap signature.**

```bash
mkswap /var/local/swapfile
chmod 600 /var/local/swapfile     # a swap file holds memory contents -> root only
ls -l /var/local/swapfile         # should show -rw-------
```

**Step 3 — Activate with a priority and verify.**

```bash
free -h                              # BEFORE
swapon -p 2 /var/local/swapfile      # activate with priority 2
swapon -s                            # file now listed, Priority 2
free -h                              # AFTER -- Swap total grew
```

**Step 4 — Watch swap get used (live demo).**

In one terminal:

```bash
watch swapon -s
```

> **To EXIT the `watch` screen, press `Ctrl + C`.** (If Ctrl+C does nothing, press `q`,
> or `Ctrl+Z` then `kill %1`.) Stopping `watch` does NOT touch your swap.

In a second terminal, stress memory with **500M** (small enough for the lab VM):

```bash
head -c 500M /dev/zero | tail
```

**Tell the students:** Watch the **Used** column on the swapfile line climb as the kernel
pushes pages into swap. That is virtual memory working in real time.

---

## 1.3 Swap priority

**Tell the students:** **Higher number = used first.** So `3 > 1 > -1 > -3`. Give fast
(SSD) swap a higher priority so the kernel reaches for it before slow disks.

> **Real world:** Spread swap across several fast disks with *equal* priority and the
> kernel stripes across them (like RAID-0 for swap) for better throughput.

---

## 1.4 Make swap survive a reboot (persistent)

```bash
cat /etc/fstab
echo "/var/local/swapfile  swap  swap  defaults,pri=2  0 0" >> /etc/fstab
systemctl daemon-reload

# Test fstab WITHOUT rebooting:
swapoff -a
swapon -a
swapon -s        # the file comes back automatically
```

**Tell the students:** fstab fields are *device, mountpoint, type, options, dump, fsck*.
For swap the mountpoint is literally the word `swap`.

> ⚠️ A typo in `/etc/fstab` can stop a server booting. Always validate with `swapon -a`
> (or `mount -a`) BEFORE a real reboot.

**Deactivate and clean up.**

> If you ever get **"text file busy"** when removing the swapfile, it's still active.
> Run `swapoff` first — you cannot modify a file that is in use as live swap.

```bash
swapoff /var/local/swapfile          # MUST do this before removing the file
swapon -s
vi /etc/fstab                        # delete the /var/local/swapfile line, save (:wq)
rm -f /var/local/swapfile
free -h
```

---

# PART 2 — LOGICAL VOLUME MANAGEMENT (Lesson 12)

## 2.1 Why LVM exists

**Tell the students:** Plain partitions are rigid — once `/data` is 100 GB it's stuck
unless you back up, repartition and restore. **LVM adds a flexible layer** so you can
grow, shrink, pool disks, and snapshot *while the system stays online*.

```
Hard drive / partition  ->  PV (Physical Volume)
                                 |
        one or more PVs pooled into ->  VG (Volume Group)
                                              |
              VG carved into virtual partitions ->  LV (Logical Volume)
                                                          |
                                  filesystem + mountpoint ->  /lv_mount
```

| Term | Meaning |
|---|---|
| **PV** | Physical Volume — a disk/partition labelled for LVM |
| **VG** | Volume Group — a pool made of one or more PVs |
| **LV** | Logical Volume — a flexible "partition" cut from a VG |
| **PE / LE** | Physical / Logical Extents — fixed-size blocks LVM allocates in (default 4 MiB) |

> **Real world:** A database LV is filling up. With LVM you add a disk to the VG and grow
> the LV + filesystem live — zero downtime. With classic partitions that's an outage.

---

## 2.2 Step 1 — Set the partition types on /dev/sdb

In this lab the partitions already exist. We only need to set their **types**:
`sdb1` -> **Linux (83)**, `sdb5` and `sdb6` -> **Linux LVM (8e)**.

```bash
fdisk /dev/sdb
```

Inside `fdisk`, type:

```
t        # change type
1        # partition 1
83       # 83 = Linux        (sdb1 stays a plain Linux partition)

t        # change type
5        # partition 5
8e       # 8e = Linux LVM    (sdb5 -> LVM)

t        # change type
6        # partition 6
8e       # 8e = Linux LVM    (sdb6 -> LVM)

p        # print to review
w        # write and quit
```

Refresh the kernel and check:

```bash
partprobe /dev/sdb
lsblk /dev/sdb
fdisk -l /dev/sdb
```

**Expected types:** `sdb1` = `Linux`, `sdb5` = `Linux LVM`, `sdb6` = `Linux LVM`.

**Tell the students:** `sdb1` is deliberately left as **Linux (83)** — it is NOT going
into LVM, so it is a good contrast. Only `sdb5` and `sdb6` are flagged `8e` for LVM. The
type tag documents intent; LVM will only build on the partitions we choose.

> **Alternative with `parted`** (scriptable, same result for an LVM partition):
> ```bash
> parted /dev/sdb set 5 lvm on
> parted /dev/sdb set 6 lvm on
> udevadm settle
> ```

---

## 2.3 Step 2 — Create Physical Volumes (PV)

Only the two LVM partitions become PVs:

```bash
pvcreate /dev/sdb5 /dev/sdb6     # label sdb5 + sdb6 as PVs (NOT sdb1)
pvs                              # short summary
pvdisplay /dev/sdb6             # full detail of one PV
```

**Tell the students:** `pvcreate` writes an LVM label + metadata to each partition. Note
that `/dev/sdb1` does **not** appear here — it's a plain Linux partition, not an LVM PV.

> ### ⚠️ Troubleshooting: `pvcreate` fails with "device has a signature"
>
> If you see errors like:
> ```
> Can't open /dev/sdb5 exclusively.  Mounted filesystem?
> Error opening device /dev/sdb5 for reading at 0 length 4096.
> Cannot use /dev/sdb5: device has a signature
> ```
> the partition still carries an **old signature** (leftover filesystem, swap, or LVM
> label from a previous run of this demo). LVM refuses to overwrite it — a safety check.
>
> **Fix — wipe the stale signatures, then retry:**
> ```bash
> wipefs -a /dev/sdb5         # erase old signature on sdb5
> wipefs -a /dev/sdb6         # erase old signature on sdb6
> wipefs /dev/sdb5            # verify -- should print nothing
> wipefs /dev/sdb6            # verify -- should print nothing
> reboot
> pvcreate /dev/sdb5 /dev/sdb6   # now succeeds
> pvs
> ```
>
> **If `wipefs` itself says the device is busy**, something is still actively using it.
> Find and stop it first:
> ```bash
> lsblk /dev/sdb        # is sdb5/sdb6 mounted, or showing an LVM child?
> swapon -s             # is one of them still active as swap?
> ```
> - Active swap:    `swapoff /dev/sdb5`
> - Mounted:        `umount /dev/sdb5`
> - Stale VG holds it: `vgchange -an my_first_vg` then `vgremove my_first_vg`
>
> Then re-run the `wipefs` + `pvcreate` commands above.
>
> **Tell the students:** this is the *same principle* as the teardown order — LVM will
> never silently clobber data it sees a signature on, and you can't reuse a partition
> that another layer is still using. The error is LVM protecting you.

---

## 2.4 Step 3 — Create a Volume Group (VG)

Pool both PVs into a group called `my_first_vg`:

```bash
vgs                                        # existing VGs (rhel is the OS one)
vgcreate my_first_vg /dev/sdb5 /dev/sdb6   # pool sdb5 (125M) + sdb6 (50M)
vgs                                        # my_first_vg now listed
vgdisplay my_first_vg                      # note VG Size, PE Size (4 MiB), Total PE
```

**Tell the students:** The VG is now a single pool of ~175M (125M + 50M, minus a little
metadata). **PE Size** (4 MiB default) is the smallest unit LVM allocates in.

> **Real world:** Think of the VG as a tank filled from several taps (disks). You stop
> caring which physical disk a logical volume sits on.

---

## 2.5 Step 4 — Create a Logical Volume (LV)

Our pool is small (~170M usable), so create a **100M** LV:

```bash
lvs                                                  # existing LVs
lvcreate -L 100M -n my_first_lv my_first_vg          # -L size, -n name
lvdisplay /dev/my_first_vg/my_first_lv               # full detail
```

**Tell the students:** `-L 100M` sizes by capacity; `-l 25` would size by extents
(25 x 4 MiB = 100 MiB). The LV appears under both `/dev/my_first_vg/` and `/dev/mapper/`.

---

## 2.6 Step 5 — Put a filesystem on it and mount

```bash
mkfs -t xfs /dev/my_first_vg/my_first_lv   # format as XFS (RHEL 9 default)
mkdir /lv_mount                            # mountpoint
mount /dev/my_first_vg/my_first_lv /lv_mount
df -h | grep lv_mount                      # confirm mounted & sized
mount | grep my_first                      # see options + type
```

**Tell the students:** the mounted name shows as
`/dev/mapper/my_first_vg-my_first_lv`. That's the **Device Mapper** — the kernel
framework LVM uses; every LV gets a node under `/dev/mapper`.

Write some data to prove it's real:

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

Our VG is nearly full, so we'll add the spare disk **`sdc`** to the pool, then grow the
LV and the filesystem — **while it stays mounted.**

**Step A — Make sdc a PV and add it to the VG.**

```bash
pvs ; vgs ; lvs                    # snapshot the "before" state
pvcreate /dev/sdc                  # label the whole spare disk as a PV
vgextend my_first_vg /dev/sdc      # add the 2G disk to the pool
vgs                                # VFree jumps to ~2G
```

**Tell the students:** we can add a *whole disk* (`/dev/sdc`) as a PV without partitioning
it. The VG instantly gets bigger.

**Step B — Extend the LV by 500M.**

```bash
df -h | grep my_first_lv                            # size BEFORE
lvextend -L +500M /dev/my_first_vg/my_first_lv      # add 500M to the LV
lvs                                                 # LSize grew, but...
df -h | grep my_first_lv                            # ...df still shows the OLD size!
```

**Tell the students:** the *container* (LV) is bigger, but the *filesystem* inside doesn't
know yet. We must grow the filesystem too.

**Step C — Grow the filesystem on the fly.**

```bash
xfs_growfs /lv_mount               # XFS grows by MOUNTPOINT, online only
df -h | grep my_first_lv           # NOW df shows the new larger size
```

| Filesystem | Grow command | Argument | Notes |
|---|---|---|---|
| XFS (RHEL default) | `xfs_growfs` | the **mountpoint** | online only, **grow only** |
| ext2/3/4 | `resize2fs` | the **LV device** | online **and** offline, can shrink |

> Shortcut: `lvextend -r -L +500M <lv>` grows the LV **and** the filesystem in one step
> (`-r` = resize fs automatically).

> **Real world:** "Our `/var/lib/mysql` is at 95%." With LVM: add disk -> `vgextend` ->
> `lvextend -r`. Done in under a minute, no maintenance window, no restart.

---

## 2.9 Tear-down (correct order)

Order matters: **unmount -> remove LV -> remove VG -> remove PV labels.**

```bash
# 1. Remove the fstab line first (avoid a broken boot)
vi /etc/fstab        # delete the my_first_vg line, save

# 2. Unmount
umount /lv_mount

# 3. Remove the logical volume
lvremove /dev/my_first_vg/my_first_lv      # answer y

# 4. Remove the volume group
vgremove my_first_vg                       # answer y

# 5. Remove the PV labels
pvremove /dev/sdb5 /dev/sdb6 /dev/sdc

# 6. (Optional) blank the disks
wipefs -a /dev/sdb*
wipefs -a /dev/sdc*
lsblk
```

**Tell the students:** if you remove things out of order (e.g. `pvremove` a disk still in
a VG) LVM refuses — it protects your data. Teardown is the create steps in reverse.

---

## 2.10 (Info only) Stratis — the modern alternative

**Tell the students:** Red Hat also ships **Stratis**, which layers pools + filesystems
with snapshots on top of LVM/XFS but with simpler commands. *Awareness only — this
module's focus is LVM.*

---

# Quick Command Cheat-Sheet

**Swap**
```
mkswap <dev|file>          # write swap signature
chmod 600 <swapfile>       # secure a swap file
swapon  -p N <dev|file>    # activate (priority N)
swapoff <dev|file>         # deactivate (do this before deleting the file!)
swapon -s  /  free -h      # verify
```

**LVM (bottom -> top)**
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

### This lab's partition roles (quick reference)
| Partition | Size | Type | Role in demo |
|---|---|---|---|
| `sdb1` | 128M | Linux (83) | plain partition — NOT in LVM (contrast) |
| `sdb5` | 125M | Linux LVM (8e) | PV -> joins `my_first_vg` |
| `sdb6` | 50M  | Linux LVM (8e) | PV -> joins `my_first_vg` |
| `sdc`  | 2G   | whole disk | PV added later via `vgextend` to grow the LV |

### One-line summary for the board
> **Swap** = extra (slow) memory cushion on disk. **LVM** = a flexible storage layer
> (PV -> VG -> LV) that lets you grow, pool, and snapshot disks live.
