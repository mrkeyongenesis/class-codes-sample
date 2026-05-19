# Lesson 10 — Manage Linux Partitions

> **Module outcome:** Create and manage storage devices, partitions and file systems using CLI; demonstrate manual and persistent mounting.

This lesson is hands-on. Every step has commands you can run in your VM terminal. Read the **safety reminder** before each block — the wrong device name in `parted` or `mkfs` destroys data without asking.

---

## Class activity recap (Slide 3)

The slide shows this `lsblk` output:

```
sda    30G  disk
├─sda1  600M part /boot/efi
├─sda2    1G part /boot
└─sda3 28.4G part
  ├─rhel_c330-root  26.4G lvm  /
  └─rhel_c330-swap     2G lvm  [SWAP]
sdb     2G disk
├─sdb1  128M part
├─sdb2    1K part
├─sdb5  256M part
│ └─my_first_vg-my_first_lv 700M lvm /lv_mount
└─sdb6  512M part
  └─my_first_vg-my_first_lv 700M lvm /lv_mount
sdc     2G disk
sr0     8G rom /media/disc
```

**Answers:**

- **How many hard disks?** Three — `sda`, `sdb`, `sdc`. (`sr0` is a CD-ROM, not a hard disk.)
- **Full path of the 2nd hard disk:** `/dev/sdb`
- **How to interpret `sdb6`:** the sixth partition on the second SATA/SCSI disk. Since it's numbered ≥ 5, it's a **logical** partition inside an extended container (`sdb2` here, which is 1 K — a typical extended-partition placeholder).
- **What is `sr0`?** An optical drive (CD/DVD-ROM). The `rom` type and the fact that it's mounted on `/media/disc` give it away.

---

## The 8-step workflow for adding new storage

Every time you add a new file system, you follow the same eight steps:

```
1. Identify the device         (lsblk)
2. Back up the partition table (sfdisk -d, optional but recommended)
3. Write a disk label          (parted mklabel)
4. Create partition(s)         (parted mkpart)
5. Update the kernel           (udevadm settle)
6. Create the file system      (mkfs.ext4 / mkfs.xfs)
7. Label the file system       (mkfs -L … or e2label, optional)
8. Mount it                    (mount, manually or via /etc/fstab)
```

We'll walk through each step. The corresponding commands are in `commands/02_create_partition_manual.sh` and `commands/03_create_partition_persistent.sh`.

---

## Step 1 — Identify the device

A new disk of size 2 GB should already be attached to your VM. Verify with any of these:

```bash
lsblk
sudo fdisk -l
sudo parted --list
```

Look for a disk like `sdb` showing `0 disk` and **no partitions**. Confirm the size matches what you attached (2 GB). If you see partitions on it already, you're looking at the wrong disk — stop and recheck.

> **Don't go further** until you can point at the new disk on screen and say its full path out loud (`/dev/sdb`). Most disasters at this stage happen because someone typed `/dev/sda` by reflex.

---

## Step 2 — Back up the partition table (best practice, optional)

This is your safety net. If you wreck the partition table, you can restore it from the backup.

```bash
sudo sfdisk -d /dev/sda > /tmp/partition.sda
ls -l /tmp/partition.sda
```

You'll see something like:

```
-rw-r--r--. 1 root root 577 Nov 4 17:58 /tmp/partition.sda
```

**To restore later** (only if disaster strikes):

```bash
sudo sfdisk /dev/sda < /tmp/partition.sda
```

> For beginners, always back up the partition table of your **OS disk** (`/dev/sda`) before working on **any** disk. A typo can hit the wrong device.

---

## Step 3 — Write a disk label

A new disk has no partition table at all. You need to write one — either MBR or GPT.

```bash
# MBR (older, max 2 TB, max 4 primaries, supports extended/logical)
sudo parted /dev/sdb mklabel msdos

# OR GPT (modern, up to 128 partitions, with backup table)
sudo parted /dev/sdb mklabel gpt
```

You'll see a warning:

```
Warning: The existing disk label on /dev/sdb will be destroyed
and all data on this disk will be lost. Do you want to continue?
Yes/No?
```

Type `Yes`.

> **Two warnings here:**
> 1. A mistake with `parted` can cause data loss. Always check the device name twice.
> 2. `mklabel` **wipes the existing partition table.** Any existing partitions on that disk are gone.

---

## Step 4 — Create partitions

Two equivalent ways: one-liner or interactive.

### One-liner

```bash
sudo parted /dev/sdb mkpart primary ext4 2048s 128MB
```

Translation: *make a partition, type=primary, intended for ext4, start at sector 2048, end at 128 MB.*

> Why start at sector 2048? Alignment. Sectors 0–2047 are reserved for the MBR boot code and partition table. Starting at 2048 (= 1 MiB offset) gives proper alignment for SSDs and modern drives.

### Interactive (more transparent for learning)

```bash
sudo parted /dev/sdb
```

At the `(parted)` prompt:

```
(parted) mkpart
Partition type?  primary/extended? p
File system type?  [ext2]? ext4
Start? 2048s
End? 128MB
(parted) p           ← print the table to verify
(parted) q           ← quit
```

Output of `p`:

```
Number  Start   End    Size   Type     File system  Flags
 1      1049kB  128MB  127MB  primary  ext4         lba
```

`parted` notes "Information: You may need to update /etc/fstab." — that's a hint for Step 8.

### Getting help inside `parted`

```bash
sudo parted /dev/sdb
(parted) help            ← list all commands
(parted) help mkpart     ← help for one command
```

Useful `parted` commands beyond `mkpart`:

| Command | Effect |
|---|---|
| `print` (or `p`) | Show the partition table |
| `mkpart` | Make a partition |
| `rm N` | Remove partition number N |
| `name N NAME` | Name a partition (GPT only) |
| `resizepart N END` | Resize partition N to a new end |
| `mklabel TYPE` | Write a new disk label (wipes existing!) |
| `quit` (or `q`) | Exit `parted` |

---

## Step 5 — Update the kernel

The partition now exists on disk, but the kernel may not have noticed yet. Force a refresh:

```bash
sudo udevadm settle
```

Verify the new partition is visible to the kernel:

```bash
lsblk /dev/sdb
cat /proc/partitions
```

You should now see `sdb1` listed (or `sdb1` and its size in 1 KiB blocks in `/proc/partitions`).

If it still doesn't appear, try:

```bash
sudo partprobe /dev/sdb
```

And as a last resort, reboot.

---

## Step 6 — Create the file system

This formats the partition — writes the empty file system structure onto it.

```bash
# ext4 (most common)
sudo mkfs.ext4 /dev/sdb1
# equivalent:
sudo mkfs -t ext4 /dev/sdb1

# XFS (RHEL default)
sudo mkfs.xfs /dev/sdb1
```

Sample output:

```
mke2fs 1.46.5 (30-Dec-2021)
Discarding device blocks: done
Creating filesystem with 123904 1k blocks and 30976 inodes
Filesystem UUID: f46ccd6d-4319-42e0-8d89-9eb041bc2da0
Superblock backups stored on blocks: 8193, 24577, 40961, 57345, 73729
Allocating group tables: done
Writing inode tables: done
Creating journal (4096 blocks): done
Writing superblocks and filesystem accounting information: done
```

The UUID printed at the top is what you'll use in `/etc/fstab` later.

---

## Step 7 — Label the file system (optional)

A label is a friendly short name for the file system. Useful for `mount LABEL=…` and for quick identification in `blkid` output.

```bash
# During creation (-L sets the label)
sudo mkfs.ext4 -L misc /dev/sdb1

# After creation (ext family)
sudo e2label /dev/sdb1 misc

# Verify
sudo blkid -s LABEL /dev/sdb1
sudo findfs LABEL=misc
```

Output of `blkid`:

```
/dev/sdb1: LABEL="misc"
```

Output of `findfs`:

```
/dev/sdb1
```

---

## Step 8 — Mount it

### Manual (temporary) mount

```bash
# Create the mount point — the directory must exist before you mount on it
sudo mkdir -p /misc

# Mount by device name
sudo mount /dev/sdb1 /misc

# Or mount by label
sudo mount LABEL=misc /misc

# Or mount by UUID (the most robust)
sudo mount UUID="f46ccd6d-4319-42e0-8d89-9eb041bc2da0" /misc

# Verify the mount took effect
mount | grep sdb1
df -h | grep sdb1
lsblk
```

Output of `mount | grep sdb1`:

```
/dev/sdb1 on /misc type ext4 (rw,relatime,seclabel)
```

Manual mounts disappear on reboot.

### Use the mounted file system

```bash
cd /misc
sudo touch file.txt
sudo cp /etc/passwd .
ls -l
```

You'll always see a `lost+found` directory in ext4 file systems — that's where `fsck` puts orphaned files it recovers. Leave it alone.

---

## Unmounting

```bash
# Step OUT of the mount point first — you can't unmount a busy FS
cd ~

sudo umount /misc
# or
sudo umount /dev/sdb1
```

### When `umount` says "target is busy"

```bash
sudo umount /misc
# umount: /misc: target is busy.
```

Something inside the mount point has open files. Find it:

```bash
sudo lsof /misc        # list open files under /misc
sudo fuser -m /misc    # list PIDs using /misc
```

Then either close those programs or, as a last resort:

```bash
sudo umount -l /misc   # lazy unmount — detaches now, frees when last reference closes
```

After unmounting, `ls /misc` shows an empty directory. The files are still on `sdb1` — `/misc` just isn't connected to it any more.

---

## Persistent mounting via `/etc/fstab`

A manual mount is forgotten on reboot. For permanent mounts, add a line to `/etc/fstab`.

### Step A — Create the mount point

```bash
sudo mkdir -p /mnt/primary_mount
```

### Step B — Get the UUID

```bash
sudo blkid /dev/sdb1
# /dev/sdb1: UUID="28942970-928d-4d7c-bac5-e24e04b2d444" BLOCK_SIZE="1024" TYPE="ext4" ...
```

### Step C — Edit `/etc/fstab`

If the file is protected with `chattr +a` (append-only), unprotect first:

```bash
sudo lsattr /etc/fstab        # see current attributes
sudo chattr -a /etc/fstab     # remove append-only if present
```

Open the file:

```bash
sudo vi /etc/fstab
```

Add a line at the bottom (use **your** UUID):

```
UUID=28942970-928d-4d7c-bac5-e24e04b2d444  /mnt/primary_mount  ext4  defaults  0  2
```

A device-path version is also acceptable (less robust):

```
/dev/sdb1  /mnt/primary_mount  ext4  rw,seclabel,relatime  0  0
```

### Step D — Quick alternative: append from `/etc/mtab`

If the partition is already mounted, you can copy its current mount line straight into fstab:

```bash
cat /etc/mtab | grep /mnt/primary_mount | sudo tee -a /etc/fstab
```

### Step E — Test before rebooting

This is the **critical safety step**. A broken `/etc/fstab` can prevent the system from booting.

```bash
sudo systemctl daemon-reload
sudo mount -a                 # mount everything in fstab; fails loudly if anything is wrong
df -h | grep primary_mount
mount | grep sdb1
```

If `mount -a` returns no errors, your fstab is safe to reboot with.

### Step F — Re-protect fstab (optional best practice)

```bash
sudo chattr +a /etc/fstab     # append-only: even root can't delete or overwrite
sudo lsattr /etc/fstab        # should show -----a---...
```

`chattr +a` sets the append-only flag. The file can be added to with `>>` but not modified or deleted, even by root. To make a real edit later, you must `chattr -a` first.

---

## Verifying mounted partitions

Several ways to check what's mounted:

```bash
df -h                              # disk free for all mounted file systems
mount                              # full list with options
mount | grep sdb                   # filter for your disk
findmnt                            # tree view of mounts
findmnt /mnt/primary_mount         # who's mounted there?
lsblk --fs                         # tree with file system info
```

---

## Deleting a partition

When you're done experimenting, clean up.

```bash
# Unmount first
sudo umount /dev/sdb1

# Remove the fstab line if you added one (chattr -a if protected)
sudo chattr -a /etc/fstab
sudo vi /etc/fstab     # delete the line for /dev/sdb1

# Remove the partition
sudo parted /dev/sdb
(parted) p             ← see the partition numbers
(parted) rm 1          ← remove partition 1
(parted) p             ← confirm it's gone
(parted) q

# Refresh kernel
sudo udevadm settle

# Verify
cat /proc/partitions
lsblk /dev/sdb
```

If the partition still appears after `udevadm settle`, reboot the system and try again.

---

## Creating an extended + logical partition (MBR only)

To exceed 4 partitions on an MBR disk, sacrifice one primary slot to be an **extended** container, then put logical partitions inside it.

```bash
# 1. MBR label (extended/logical doesn't exist on GPT)
sudo parted /dev/sdc mklabel msdos

# 2. Make an extended partition that fills most of the disk
sudo parted /dev/sdc mkpart extended 2048s 100%

# 3. Make a logical partition inside it
#    Note: logical partition numbering always starts at 5
sudo parted /dev/sdc mkpart logical ext4 4096s 512MB

sudo udevadm settle
lsblk /dev/sdc

# 4. Format the LOGICAL partition (sdc5), not the extended one
sudo mkfs.ext4 -L logical_mount /dev/sdc5
```

Why `sdc5` and not `sdc4`? Because logical partitions are always numbered **5 and up**, regardless of how many primaries actually exist. The numbers 1–4 are permanently reserved for primary slots in MBR.

---

## Attaching a new disk to a VMware VM

The slides show this as a clickable GUI flow. The key choices:

1. **Power off** the VM (IDE/NVMe require this; SCSI can sometimes hot-add).
2. VM → Settings → Hardware → **Add…** → **Hard Disk**.
3. Disk type: **SCSI (recommended)** for most cases. (See the comparison below.)
4. **Create a new virtual disk**.
5. **Maximum disk size**: 2.0 GB (or whatever you need).
6. **Store virtual disk as a single file**.
7. Specify disk file name (e.g., `AY2023S2_C330.vmdk`).
8. Finish; power on the VM.

### Storage interface comparison

| Interface | Max transfer rate | Data transfer method | Power consumption |
|---|---|---|---|
| SATA | ~6 Gbps | Serial | Moderate |
| PATA | ~133 MB/s | Parallel | Moderate |
| NVMe | ~32 Gbps | PCIe | Low |
| SCSI | ~640 MB/s | Serial / parallel | Moderate |

Once the VM is back up:

```bash
lsblk    # the new disk appears as the next free letter (sdb, sdc, …)
```

If it doesn't appear without a reboot, force a rescan:

```bash
echo "- - -" | sudo tee /sys/class/scsi_host/host0/scan
```

---

## What happens to mounted files when you unmount?

The slides ask: *"What happened to the directory contents mounted on primary and secondary partitions?"*

**Answer:** The files are still on the underlying disk partition. They are not deleted. What changes is that the mount point directory (e.g., `/mnt/primary_mount`) is no longer linked to that partition. So `ls /mnt/primary_mount` shows whatever was originally in that directory before you mounted (usually nothing, if you created it fresh with `mkdir`).

To see the files again, just remount:

```bash
sudo mount /dev/sdb1 /mnt/primary_mount
ls /mnt/primary_mount    # files are back
```

This is also why **mounting on a non-empty directory hides the original contents** — they're still there, just shadowed until you unmount.

---

## Worksheet Q1 walkthrough (15 min, slide 16)

Replace `<yourname>` with `alice` and `<student_id>` with `e62a01` for this example. The full runnable script is in `commands/06_worksheet_q1.sh`.

```bash
# (a) Create a new ext4 partition of 256 MB on /dev/sdb, mount on /mnt/alice
sudo parted /dev/sdb mklabel msdos
sudo parted /dev/sdb mkpart primary ext4 2048s 256MB
sudo udevadm settle
sudo mkfs.ext4 /dev/sdb1
sudo mkdir -p /mnt/alice
sudo mount /dev/sdb1 /mnt/alice

# (b) Test by creating c330_alice.txt
sudo touch /mnt/alice/c330_alice.txt
ls -l /mnt/alice

# (c) Create another 512 MB ext4 partition, mount on /mnt/e62a01
sudo parted /dev/sdb mkpart primary ext4 256MB 768MB
sudo udevadm settle
sudo mkfs.ext4 /dev/sdb2
sudo mkdir -p /mnt/e62a01
sudo mount /dev/sdb2 /mnt/e62a01

# (d) Access mount points by copying files
sudo cp /etc/passwd /mnt/alice/
sudo cp /etc/group  /mnt/e62a01/
ls -l /mnt/alice /mnt/e62a01

# (e) Show proof to lecturer
df -h

# (f) Unmount
sudo umount /mnt/alice
sudo umount /mnt/e62a01

# (g) Delete partitions
sudo parted /dev/sdb rm 2
sudo parted /dev/sdb rm 1
sudo udevadm settle
lsblk /dev/sdb     # should now show no partitions
```

---

## Worksheet Q2 walkthrough (15 min, slide 28)

This one practises **persistent** mounting.

```bash
# (a) Attach a new 2 GB hard disk via VMware Settings (see "Attaching a new disk").
#     Verify it appears as /dev/sdb (or sdc if sdb is taken).
lsblk

# (b) Create a 1 GB ext4 partition, manually mount on /mnt/E62A
sudo parted /dev/sdb mklabel msdos
sudo parted /dev/sdb mkpart primary ext4 2048s 1024MB
sudo udevadm settle
sudo mkfs.ext4 /dev/sdb1
sudo mkdir -p /mnt/E62A
sudo mount /dev/sdb1 /mnt/E62A

# (c) Test access
sudo touch /mnt/E62A/soi_c330.txt
ls -l /mnt/E62A

# (d) Create a 512 MB ext4 partition, mount PERSISTENTLY on /mnt/E62B
sudo parted /dev/sdb mkpart primary ext4 1024MB 1536MB
sudo udevadm settle
sudo mkfs.ext4 /dev/sdb2
sudo mkdir -p /mnt/E62B

# Get the UUID
UUID=$(sudo blkid -s UUID -o value /dev/sdb2)
echo "$UUID"

# Edit /etc/fstab safely
sudo chattr -a /etc/fstab 2>/dev/null   # remove append-only if set
echo "UUID=$UUID  /mnt/E62B  ext4  defaults  0  2" | sudo tee -a /etc/fstab

# Reload and test
sudo systemctl daemon-reload
sudo mount -a

# (e) Verify the fstab entry
tail -n 5 /etc/fstab

# (f) Copy log file to mount point
sudo cp /var/log/messages /mnt/E62B/

# (g) Verify
ls -l /mnt/E62B
df -h | grep E62B
```

---

## Common pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| `umount: target is busy` | A process or shell is inside the mount | `cd ~` first; check `sudo lsof /mnt/...`; kill the process or use `umount -l` |
| New partition not visible after `parted` | Kernel hasn't refreshed | `sudo udevadm settle` or `sudo partprobe /dev/sdb` |
| `mount -a` fails after editing fstab | Typo in fstab | Read the error; check column count (must be 6); check UUID matches `blkid` |
| System won't boot after fstab edit | Bad fstab line | Boot to rescue mode, mount root read-write, fix `/etc/fstab`, reboot |
| `parted` opens but partition table is empty | Wrong disk, or table was never written | Recheck `lsblk`; you may need `mklabel` first |
| `mkfs` refuses with "is mounted" | Trying to format an already-mounted FS | `umount` it first |
| Logical partition numbering jumps to 5 | Normal! MBR reserves 1–4 for primaries | Logical partitions inside extended always start at 5 |
| `chattr -a` says "Operation not permitted" | You're not root | Run with `sudo` |

For a fuller list, see `04_troubleshooting.md`.

---

## Summary checklist

You should now be able to:

- [ ] Run the 8-step workflow from identifying a disk to mounting it
- [ ] Choose between MBR (`msdos`) and GPT labels with `parted mklabel`
- [ ] Create primary, extended, and logical partitions with `parted mkpart`
- [ ] Format with `mkfs.ext4` and `mkfs.xfs`, with or without a label
- [ ] Mount manually with `mount` and persistently with `/etc/fstab`
- [ ] Get a UUID and use it in fstab
- [ ] Test `/etc/fstab` safely with `mount -a` before rebooting
- [ ] Unmount, recover from "target is busy", and delete partitions cleanly
- [ ] Protect `/etc/fstab` with `chattr +a`
