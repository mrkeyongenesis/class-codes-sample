# Lesson 10: RHEL 9 Disk Partitioning with `parted`

This lesson is written for students working in a RHEL 9 virtual machine. It shows the exact commands, expected outputs, and beginner-friendly explanations for partitioning a disk with `parted` instead of `fdisk`.

> Important: Only partition the disk you intend to use. If you are using a VM with only one disk, create a loopback disk image for practice instead of repartitioning the boot disk.

## Why `parted`?

- `parted` is the modern Linux partitioning tool for GPT and large disks.
- We cover `fdisk` in earlier lessons, so this lesson focuses on the newer workflow.
- `parted` can be used interactively or with one-line commands.
- It works well with RHEL 9 default filesystems like `xfs` and boots on modern UEFI systems.

## Prerequisites

- A RHEL 9 VM with `sudo` access.
- A terminal window in the VM.
- At least one spare disk or a loopback disk image for practice.
- Internet access only if you need to install `parted`.

## Step 0: Install `parted` and supporting tools

Run these commands first:

```bash
sudo dnf install -y parted dosfstools xfsprogs
```

Expected:
- `parted` is installed.
- `mkfs.fat` is available from `dosfstools`.
- `mkfs.xfs` is available from `xfsprogs`.

## Step 1: Discover available disks

Check your disks and partitions before changing anything.

```bash
sudo lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT,MODEL
sudo parted -l
```

Expected:
- A list of disk devices such as `/dev/sda`, `/dev/sdb`, or `/dev/loop0`.
- Any mounted partitions appear with a mount point.

For a safe practice disk in a VM without extra physical disks, create a loopback disk image:

```bash
cd /tmp
sudo truncate -s 3G disk.img
sudo losetup --find --show disk.img
```

Example output:

```text
/dev/loop0
```

Use the path shown by `losetup`, for example `/dev/loop0`, in the next steps.

## Step 2: Choose the target disk and confirm it

Use only the disk you want to partition. For example:

- real spare disk: `/dev/sdb`
- loopback disk: `/dev/loop0`

Confirm one more time:

```bash
sudo lsblk /dev/sdb
```

or

```bash
sudo lsblk /dev/loop0
```

If the target disk already contains partitions and you are reusing it, you can view them with:

```bash
sudo parted /dev/sdb print
```

## Step 3: Create a new GPT label on the disk

This command erases existing partition metadata and creates a GPT table.

```bash
sudo parted /dev/sdb --script mklabel gpt
```

If you are using a loop device, replace `/dev/sdb` with `/dev/loop0`.

Expected:
- No output or a short confirmation.
- The disk now has a GPT label.

## Step 4: Create the first partition — EFI system or boot partition

This example creates a 512 MiB EFI partition at the start of the disk.

```bash
sudo parted /dev/sdb --script mkpart primary fat32 1MiB 513MiB
sudo parted /dev/sdb --script set 1 esp on
```

What this does:
- `mkpart primary fat32 1MiB 513MiB` creates partition 1 from 1 MiB to 513 MiB.
- `set 1 esp on` marks partition 1 as an EFI system partition.

Verify it:

```bash
sudo parted /dev/sdb print
```

Expected output includes:
- `Number  Start   End     Size    File system  Name  Flags`
- Partition 1 set to `fat32` with the `esp` flag.

## Step 5: Create the second partition — root filesystem

Create a root partition using XFS, which is the default filesystem on RHEL 9.

```bash
sudo parted /dev/sdb --script mkpart primary xfs 513MiB 20GiB
```

Use `20GiB` only as an example. If you want a larger root partition, extend this number.

Verify it again:

```bash
sudo parted /dev/sdb print
```

Expected:
- Partition 2 appears with the correct start and end.
- The filesystem column may show `xfs` or be blank until formatting.

## Step 6: Create the third partition — home filesystem

Create a home partition that uses the remaining disk space.

```bash
sudo parted /dev/sdb --script mkpart primary xfs 20GiB 100%
```

This uses all remaining space after the root partition.

Verify the final partition table:

```bash
sudo parted /dev/sdb print
```

Expected:
- Partition 1: EFI, 512 MiB
- Partition 2: root, 19.5 GiB (approx)
- Partition 3: home, remaining space

## Step 7: Format the partitions

Now format each partition with the correct filesystem.

### Format EFI partition

```bash
sudo mkfs.fat -F32 /dev/sdb1
```

### Format root partition

```bash
sudo mkfs.xfs /dev/sdb2
```

### Format home partition

```bash
sudo mkfs.xfs /dev/sdb3
```

If you created a swap partition instead of a home partition, use:

```bash
sudo mkswap /dev/sdb3
```

Expected:
- `mkfs.fat` prints the label and file system creation steps.
- `mkfs.xfs` prints a metadata summary and exits successfully.

## Step 8: Mount and verify the partitions

Create mount points and mount the new partitions so you can inspect them.

```bash
sudo mkdir -p /mnt/rhel-root
sudo mount /dev/sdb2 /mnt/rhel-root
sudo mkdir -p /mnt/rhel-root/boot/efi
sudo mount /dev/sdb1 /mnt/rhel-root/boot/efi
sudo mkdir -p /mnt/rhel-root/home
sudo mount /dev/sdb3 /mnt/rhel-root/home
```

Check mounted filesystems:

```bash
findmnt -a | grep '/mnt/rhel-root'
```

Verify the disk layout clearly:

```bash
lsblk -f /dev/sdb
sudo blkid /dev/sdb1 /dev/sdb2 /dev/sdb3
```

Expected:
- `findmnt` shows `/dev/sdb2` mounted on `/mnt/rhel-root`.
- `lsblk -f` shows `vfat` on `/dev/sdb1` and `xfs` on `/dev/sdb2` and `/dev/sdb3`.
- `blkid` prints the filesystem types and UUIDs.

## Step 9: Confirm the filesystem contents

Make sure the mounted partitions are writable and accessible.

```bash
sudo touch /mnt/rhel-root/hello-root.txt
sudo touch /mnt/rhel-root/home/hello-home.txt
sudo ls -l /mnt/rhel-root /mnt/rhel-root/home /mnt/rhel-root/boot/efi
```

Expected:
- `hello-root.txt` appears in the root mount.
- `hello-home.txt` appears in the home mount.
- The `boot/efi` directory is mounted and visible.

## Step 10: Unmount cleanly when finished

When you are done practicing:

```bash
sudo umount /mnt/rhel-root/home
sudo umount /mnt/rhel-root/boot/efi
sudo umount /mnt/rhel-root
```

If an unmount fails because a shell is inside the mount point, exit that shell and retry.

## Step 11: Use interactive `parted` for classroom practice

This is useful for students who want to type commands step by step.

```bash
sudo parted /dev/sdb
```

Inside `parted`, use these commands:

- `unit MiB` — show sizes in MiB
- `print` — show the partition table
- `mklabel gpt` — create a new GPT label
- `mkpart primary fat32 1 513` — make partition 1
- `set 1 esp on` — mark partition 1 as bootable/EFI
- `mkpart primary xfs 513 20480` — make partition 2
- `mkpart primary xfs 20480 100%` — make partition 3
- `quit` — exit parted

Example interactive session:

```text
(parted) unit MiB
(parted) print
(parted) mklabel gpt
(parted) mkpart primary fat32 1 513
(parted) set 1 esp on
(parted) mkpart primary xfs 513 20480
(parted) mkpart primary xfs 20480 100%
(parted) print
(parted) quit
```

## Step 12: Common beginner mistakes and how to avoid them

- Do not partition `/dev/sda` unless you know it is the correct disk.
- Always confirm with `lsblk` before formatting.
- If `parted` reports a device is busy, unmount it first.
- Use `sudo parted -l` or `sudo lsblk -f` to verify the target device.
- If you want a smaller test disk, use `losetup` and a loopback file.

## Optional exercise: Remove and recreate a partition

If you want to start over on the same disk:

```bash
sudo parted /dev/sdb --script rm 3
sudo parted /dev/sdb --script rm 2
sudo parted /dev/sdb --script rm 1
sudo parted /dev/sdb --script print
```

Then recreate the partitions from Step 3 onward.

## Optional example: Create a swap partition

If you want a swap partition instead of `/home`, use:

```bash
sudo parted /dev/sdb --script mkpart primary linux-swap 20GiB 22GiB
sudo mkswap /dev/sdb4
sudo swapon /dev/sdb4
sudo swapon --show
```

## Review of the key commands

- `sudo parted /dev/sdb --script mklabel gpt`
- `sudo parted /dev/sdb --script mkpart primary fat32 1MiB 513MiB`
- `sudo parted /dev/sdb --script set 1 esp on`
- `sudo parted /dev/sdb --script mkpart primary xfs 513MiB 20GiB`
- `sudo parted /dev/sdb --script mkpart primary xfs 20GiB 100%`
- `sudo mkfs.fat -F32 /dev/sdb1`
- `sudo mkfs.xfs /dev/sdb2`
- `sudo mkfs.xfs /dev/sdb3`
- `sudo mount /dev/sdb2 /mnt/rhel-root`
- `findmnt -a | grep '/mnt/rhel-root'`

## What students should know after this lesson

- How to identify disks and partitions in RHEL 9.
- How to create a GPT partition table with `parted`.
- How to make boot, root, and home partitions.
- How to format partitions with `mkfs.xfs` and `mkfs.fat`.
- How to mount partitions and verify them.
- How to use `parted` both non-interactively and interactively.
- How to safely unmount and clean up after practice.
