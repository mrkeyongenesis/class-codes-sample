# Troubleshooting Guide

When something goes wrong with partitions, file systems, or mounts, work through these checks in order.

## 1. "umount: target is busy"

**Cause:** A process has an open file inside the mount point, or your shell is `cd`-ed into it.

**Fix:**

```bash
# Step out of the mount point first
cd ~

# Find what's holding it open
sudo lsof /mnt/data          # list open files
sudo fuser -vm /mnt/data     # list PIDs and users

# Close the offending programs, then retry
sudo umount /mnt/data

# Last resort: lazy unmount (detaches now, frees when last reference closes)
sudo umount -l /mnt/data
```

## 2. New partition doesn't appear in `lsblk`

**Cause:** The kernel didn't refresh its in-memory partition table.

**Fix:**

```bash
sudo udevadm settle
lsblk /dev/sdb

# If still missing
sudo partprobe /dev/sdb
lsblk /dev/sdb

# Last resort
sudo reboot
```

## 3. `mount -a` fails after editing `/etc/fstab`

**Cause:** Syntax error, wrong UUID, missing mount point, or unknown file system.

**Fix:**

```bash
# Read the exact error message — it usually points to the failed line
sudo mount -a

# Check syntax: must be 6 whitespace-separated fields
awk 'NF != 6 && !/^#/ && NF > 0 {print NR": "$0}' /etc/fstab

# Verify the UUID actually exists
sudo blkid

# Verify the mount point directory exists
ls -ld /mnt/your_mount_point

# Fix the fstab line, then retry
sudo vi /etc/fstab
sudo systemctl daemon-reload
sudo mount -a
```

## 4. System won't boot after editing `/etc/fstab`

**Cause:** A bad fstab line blocked startup. The system drops into emergency mode.

**Recovery (at the emergency prompt):**

```bash
# Log in as root
mount -o remount,rw /              # make root writeable
vi /etc/fstab                      # comment out (#) or fix the bad line
mount -a                           # verify the fix
reboot
```

**Prevention:** always run `sudo mount -a` after editing `/etc/fstab`, **before** rebooting. If `mount -a` returns no errors, the file is safe.

## 5. `parted` opens but the partition table is empty

**Cause:** Disk has no disk label, or you're on the wrong disk.

**Fix:**

```bash
# First — confirm the disk
lsblk

# If sdb really is the new disk, write a label
sudo parted /dev/sdb mklabel msdos    # or gpt
```

## 6. `mkfs` refuses with "is mounted" or "is apparently in use"

**Cause:** You're trying to format a partition that's already mounted, or the kernel still thinks it's in use.

**Fix:**

```bash
# Find what's using it
mount | grep sdb1
sudo lsof /dev/sdb1

# Unmount
sudo umount /dev/sdb1

# Try again
sudo mkfs.ext4 /dev/sdb1
```

If `mkfs` insists the FS is in use even after unmount, the partition may be part of LVM or a swap pool:

```bash
sudo swapoff /dev/sdb1       # if it's swap
sudo lvremove ...            # if it's LVM (be careful!)
```

## 7. Logical partition jumps from 1 to 5

**Not a problem — this is expected behaviour.** MBR reserves numbers 1–4 for primary partition slots. Logical partitions (inside an extended container) always start at 5, even if you only have one primary.

Example: a disk with one primary and one logical will have `sdb1` (primary) and `sdb5` (logical), with `sdb2`, `sdb3`, `sdb4` unused.

## 8. `chattr -a` says "Operation not permitted"

**Cause:** You're not root, or the file system doesn't support the attribute.

**Fix:**

```bash
# Use sudo
sudo chattr -a /etc/fstab

# Confirm the file system is ext family or similar that supports attributes
sudo lsattr /etc/fstab
```

## 9. UUID changed unexpectedly

**Cause:** Someone reformatted the partition, or the file system was recreated.

**Fix:**

```bash
# Get the current UUID
sudo blkid /dev/sdb1

# Update /etc/fstab with the new value
sudo vi /etc/fstab
sudo systemctl daemon-reload
sudo mount -a
```

## 10. Disk shows wrong size or "unrecognised disk label"

**Cause:** Brand-new disk with no partition table, or corrupted partition table.

**Fix:**

```bash
# Confirm the actual size
sudo fdisk -l /dev/sdb

# Write a fresh label (destroys any existing partitions)
sudo parted /dev/sdb mklabel msdos    # or gpt
```

For a corrupted table where you do have a backup:

```bash
sudo sfdisk /dev/sdb < /tmp/partition.sdb
```

## 11. "No space left on device" but `df` shows free space

**Cause:** The file system is out of **inodes**, not bytes. Each file uses one inode.

**Fix:**

```bash
# Check inode usage
df -i

# Find directories with lots of small files
sudo find / -xdev -type f | awk -F/ '{print $2"/"$3}' | sort | uniq -c | sort -rn | head

# Either delete unneeded files, or
# Reformat with more inodes (mkfs.ext4 -N <count>) — requires backup/restore
```

## 12. `mount` says "wrong fs type, bad option, bad superblock"

**Cause:** Wrong filesystem in the mount command, corrupted FS, or missing kernel module.

**Fix:**

```bash
# Verify the actual file system type
sudo blkid /dev/sdb1

# Mount with the right type
sudo mount -t ext4 /dev/sdb1 /mnt/data

# Check for FS corruption (must be UNMOUNTED first)
sudo umount /dev/sdb1
sudo fsck.ext4 -f /dev/sdb1

# For XFS
sudo xfs_repair /dev/sdb1
```

## 13. Permission denied writing to a mounted FS

**Cause:** Mounted read-only, or the directory inside has restrictive permissions.

**Fix:**

```bash
# Check mount options
mount | grep /mnt/data
# If you see "(ro,...)", it's read-only

# Remount read-write
sudo mount -o remount,rw /mnt/data

# Or fix permissions
sudo chmod 755 /mnt/data
sudo chown student:student /mnt/data
```

## 14. fstab uses `/dev/sdX` but disk letters changed after a reboot

**Cause:** Linux assigns `sda`, `sdb`, … in detection order, which can change.

**Fix:** Switch to UUIDs in `/etc/fstab` — they never change unless you reformat.

```bash
sudo blkid /dev/sdb1
# Replace /dev/sdb1 in fstab with UUID=<value>
sudo systemctl daemon-reload
sudo mount -a
```

## 15. Verifying things are sane

When everything looks broken, run this checklist:

```bash
# What disks does the kernel see?
lsblk
cat /proc/partitions

# What file systems are formatted?
sudo blkid

# What's currently mounted?
mount
df -h
findmnt

# What does fstab say should be mounted?
cat /etc/fstab

# Test fstab without rebooting
sudo mount -a
echo $?    # 0 = OK, anything else = failure

# Recent kernel messages about storage
sudo dmesg | tail -50
sudo journalctl -b -k | grep -iE "sd|partition|mount" | tail
```

If `lsblk`, `blkid`, and `mount -a` all agree, the system is in a consistent state.
