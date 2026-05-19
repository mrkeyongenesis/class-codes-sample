# Lesson 9 — Access Linux File Systems

> **Module outcome:** Identify the storage devices for a file/directory.

## 1. The Linux storage stack

Every file you save in Linux passes through five layers. Understanding this stack is the foundation of everything else in this lesson.

```
┌─────────────────────────────────────┐
│  File / Directory                   │  ← /home/student/notes.txt
├─────────────────────────────────────┤
│  Mount point        (/mnt/data)     │  ← directory that connects FS to tree
├─────────────────────────────────────┤
│  File system        (xfs, ext4)     │  ← how data is organised on a partition
├─────────────────────────────────────┤
│  Partition          (/dev/sdb1)     │  ← a slice of a disk
├─────────────────────────────────────┤
│  Block device       (/dev/sdb)      │  ← the physical or virtual disk
└─────────────────────────────────────┘
```

To make new storage usable, you build from the **bottom up**:
1. Attach a disk (block device)
2. Carve it into partitions
3. Format each partition with a file system
4. Mount the file system to a directory
5. Read and write files there

---

## 2. Disk partitions (prior knowledge)

A disk drive can be divided into **partitions**. You can:
- allocate the whole disk to a single partition, or
- create several partitions on the same disk.

Each partition can be formatted with a different **block size** depending on what kind of data lives on it. If your data is mostly small files (< 1 KB) and your partition uses 4 KB blocks, you waste up to 3 KB per file. Match the block size to the workload.

---

## 3. Block devices

A **block device** is a special file in `/dev` that gives Linux low-level, random access to a storage device. "Block" means data is read and written in fixed-size chunks (blocks), not as a stream.

Block devices are **non-volatile** mass storage: SSDs, hard disks, SD cards, USB drives, CD-ROMs, floppy disks, and virtual disks in VMs.

### Naming patterns

| Type of device | Naming pattern |
|---|---|
| SATA / SAS / USB-attached storage | `/dev/sda`, `/dev/sdb`, `/dev/sdc`, … |
| `virtio-blk` paravirtualised storage (VMs) | `/dev/vda`, `/dev/vdb`, … |
| NVMe-attached storage (most SSDs) | `/dev/nvme0n1`, `/dev/nvme1n1`, … |
| SD / MMC / eMMC | `/dev/mmcblk0`, `/dev/mmcblk1`, … |

**Reading a name:** `/dev/sdb1` = "second SATA disk (`b` = 2nd letter), first partition (`1`)". `/dev/sdc5` = "third disk, fifth partition" (and 5 is significant — see § 5).

### Block vs character

Devices in `/dev` are either **block** (random access, like a hard drive) or **character** (serial stream, like a keyboard or mouse). You can tell them apart by the first character of the permission string in `ls -l /dev`:

- `b` → block device (e.g., `brw-rw----`)
- `c` → character device (e.g., `crw-rw----`)

### Notable entries in `/dev`

| File | Description |
|---|---|
| `/dev/sda` | First SATA / SCSI disk |
| `/dev/sda1` | First partition on the first SATA / SCSI disk |
| `/dev/hda` | Master device on the primary IDE channel (legacy) |
| `/dev/hdb` | Slave device on the primary IDE channel (legacy) |
| `/dev/tty0` | First virtual console |
| `/dev/pts/1` | Pseudo terminal 1 |
| `/dev/lp0` | First parallel port |
| `/dev/ttyS0` | First serial port |
| `/dev/sr0` | First optical drive (CD/DVD) |

---

## 4. Partitioning schemes: MBR vs GPT

Linux supports two main partitioning schemes.

### Master Boot Record (MBR)

- Stored in the **first sector** of the disk.
- Supports up to **4 primary partitions**.
- Maximum partition size **2 TB**.
- Uses **32-bit** logical block addresses.
- Typically holds `/boot` (the Linux kernel) in a primary partition.
- In `parted`, MBR is called `msdos`.

### GUID Partition Table (GPT)

- Supports up to **128 partitions**.
- Keeps a **backup partition table** at the end of the disk.
- Used with **UEFI** firmware.
- The standard for laying out modern x64 disks.
- Uses **64-bit** logical block addresses.
- In `parted`, GPT is called `gpt`.

### How to tell which scheme a disk uses

```bash
sudo fdisk -l /dev/sda | grep -i "disklabel"
```

Output is either `Disklabel type: dos` (MBR) or `Disklabel type: gpt` (GPT).

### Side-by-side

| Feature | MBR | GPT |
|---|---|---|
| Max primary partitions | 4 | 128 |
| Max partition size | 2 TB | 9.4 ZB (effectively unlimited) |
| Backup partition table | No | Yes (end of disk) |
| Logical block address size | 32-bit | 64-bit |
| Boot firmware | BIOS | UEFI |
| `parted` label name | `msdos` | `gpt` |

---

## 5. Extended and logical partitions (MBR workaround)

MBR's 4-primary limit is restrictive. The workaround: one of the primary slots can be an **extended partition**, which acts as a container holding **logical partitions** (up to 15 total on a SCSI disk).

Key rules:
- Extended partitions are **not** formatted with a file system. They are containers only.
- **Logical** partitions inside an extended partition **are** formatted with file systems.
- Logical partitions are **always numbered starting at 5**, regardless of how many primaries exist.

### Example MBR layout

```
┌──────┬──────┬──────┬─────────────────────────────────┐
│ sdb1 │ sdb2 │ sdb3 │ sdb4  (extended container)      │
│ pri  │ pri  │ pri  │  ┌──────┬──────┬──────┐         │
│      │      │      │  │ sdb5 │ sdb6 │ sdb7 │ ...     │
│      │      │      │  │ log  │ log  │ log  │         │
│      │      │      │  └──────┴──────┴──────┘         │
└──────┴──────┴──────┴─────────────────────────────────┘
```

On GPT disks there is no extended/logical distinction — every partition is treated equally and numbered sequentially (`sdb1, sdb2, sdb3, …`).

---

## 6. File systems

A **file system** is the data structure used by the operating system to control how data is stored and retrieved on block devices. It indexes everything — file size, attributes, location, directory hierarchy — and gives each file a path.

### File systems by OS

| OS | File systems |
|---|---|
| Windows | FAT, NTFS, exFAT |
| macOS | HFS, HFS+, APFS |
| Linux | xfs, ext2, ext3, ext4, JFS, Btrfs |

### Linux file systems in detail

| File system | Description |
|---|---|
| **XFS** (Extents File System) | **Default for RHEL.** Highly scalable, high-performance, 64-bit journaling file system. Supports very large files and very large file systems. |
| **ext4** (Fourth Extended File System) | For managing local files. Improved read/write performance compared to ext2 and ext3. |
| **exFAT** (RHEL 9+) | Used for removable media (cross-platform with Windows and macOS). |
| **GFS2** (Global File System 2) | Used in enterprise server clusters for shared disks with concurrent multi-node access. |
| **swap** | Not for files — used for virtual memory. Data is written here when RAM is exhausted. |

---

## 7. Inspecting block devices — the daily commands

### `lsblk` — list block devices in a tree

```bash
lsblk                # basic tree
lsblk -f             # with file system info (FSTYPE, UUID, MOUNTPOINT)
lsblk -fp            # with full paths (/dev/sda not just sda)
lsblk -d             # disks only (no partitions)
lsblk /dev/sdb       # only this disk
```

Example output of `lsblk`:

```
NAME             MAJ:MIN  RM   SIZE RO TYPE MOUNTPOINTS
sda                8:0     0    30G  0 disk
├─sda1             8:1     0   600M  0 part /boot/efi
├─sda2             8:2     0     1G  0 part /boot
└─sda3             8:3     0  28.4G  0 part
  ├─rhel-root    253:0     0  26.4G  0 lvm  /
  └─rhel-swap    253:1     0     2G  0 lvm  [SWAP]
sdb                8:16    0     2G  0 disk
sr0               11:0     1     8G  0 rom  /media/disc
```

How to read it:
- `sda` is a 30 GB disk with three partitions; `sda3` is an LVM physical volume split into two logical volumes (`rhel-root` mounted on `/`, `rhel-swap` used for swap).
- `sdb` is a 2 GB unpartitioned disk — perfect playground.
- `sr0` is the optical drive (`rom` type).

### `blkid` — show UUIDs, labels, and types

```bash
sudo blkid                    # everything
sudo blkid /dev/sda1          # one device
sudo blkid -s UUID /dev/sda1  # just the UUID
sudo blkid -s LABEL           # all labels
```

Why this matters: every formatted file system has a permanent **UUID** burned into it. If you move the disk to another machine where it becomes `sdf` instead of `sdb`, the UUID stays the same. `/etc/fstab` uses UUIDs for this reason.

### `df` — disk free (only mounted file systems)

```bash
df                # raw bytes
df -h             # human-readable, 1024 divisor (1 KiB = 1024 B)
df -H             # human-readable, 1000 divisor (1 KB = 1000 B, like disk manufacturers)
df -h /home       # one mount point
```

### `du` — disk usage (any directory)

```bash
du -sh /home               # total size of /home (summary, human-readable)
du -sh /home /var /usr     # multiple directories at once
du -h /var/log | tail      # breakdown of a directory tree
du -sh /var/log/*          # size of each item in a directory
```

### `fdisk` and `parted` — detailed partition info

```bash
sudo fdisk -l /dev/sda           # one disk
sudo fdisk -l                    # all disks
sudo parted /dev/sda print       # parted's view of one disk
sudo parted --list               # parted's view of every disk
```

---

## 8. Mount points and `/etc/fstab`

### Mount points

A **mount point** is just an empty directory where you attach a file system. After mounting, anything inside that directory actually reads from / writes to the underlying device.

```bash
sudo mount /dev/sdb1 /mnt/data
# Now /mnt/data/file.txt is stored on sdb1
```

If you mount a file system onto a directory that already contains files, those files are hidden until you unmount.

### `/etc/fstab` — the file system table

`/etc/fstab` is a plain-text configuration file listing the major file systems on a computer. It's read by `mount`, `fsck`, and other commands at boot to mount everything automatically.

View yours:

```bash
cat /etc/fstab
```

To mount everything listed in `/etc/fstab` at once:

```bash
sudo mount -a
```

### `/etc/fstab` line format — six fields

```
#device           mount_point   filesystem  mount_options  dump  fsck
UUID=abcd-1234    /mnt/data     ext4        defaults       0     2
```

| # | Field | Purpose |
|---|---|---|
| 1 | Device | Partition reference — `/dev/sdb1`, `UUID=…`, or `LABEL=…` |
| 2 | Mount point | Directory where the FS is attached |
| 3 | Filesystem | `ext4`, `xfs`, `swap`, `iso9660`, `vfat`, `auto`, … |
| 4 | Options | `defaults`, `rw`, `ro`, `noauto`, `user`, … |
| 5 | Dump | `0` (don't back up — usual), `1` (back up with `dump`) |
| 6 | fsck order | `0` (don't check), `1` (check first — root only), `2` (check after root) |

### Why prefer UUIDs over `/dev/sdX` names?

Block device names (`/dev/sda`, `/dev/sdb`, …) are assigned in the order Linux detects them. If you add another disk, or your cloud provider changes the underlying storage, what used to be `sdb` may become `sdc`. The device file name changes, but **UUIDs stay constant** because they're part of the file system's superblock.

Get a UUID:

```bash
sudo blkid /dev/sdb1
# /dev/sdb1: UUID="f46ccd6d-4319-42e0-8d89-9eb041bc2da0" TYPE="ext4" ...
```

Then use it:

```bash
sudo mount UUID="f46ccd6d-4319-42e0-8d89-9eb041bc2da0" /mnt/data
```

Or with a label:

```bash
sudo blkid -s LABEL /dev/sdb1
sudo mount LABEL=misc /mnt/data
```

---

## 9. Locating files: `locate` vs `find`

Two ways to search for files.

### `locate` — fast, index-based

```bash
sudo updatedb                # refresh the index (otherwise results may be stale)
locate passwd                # find anything with "passwd" in the path
locate -n 5 passwd           # limit to 5 results
locate -i README             # case-insensitive
```

Reads a pre-built database. Returns results instantly. Requires `mlocate` package and a recent `updatedb` run.

### `find` — real-time, walks the tree

```bash
find /etc -name "pas*"                    # by name pattern
find / -name "*.conf" -size +1M           # configs bigger than 1 MB
find /home -mtime -7                      # modified in last 7 days
find / -user student -type f              # owned by user "student", files only
find /var/log -type f -name "*.log"       # log files in /var/log
find . -name "*.tmp" -delete              # find and delete (dangerous!)
```

Slower because it walks the directory tree on each call. Always current. Much more powerful filtering.

### Side-by-side

| | `locate` | `find` |
|---|---|---|
| Speed | Fast (index lookup) | Slower (walks tree) |
| Freshness | As old as last `updatedb` | Always current |
| Filters | Name only | Name, size, time, perms, owner, type, … |
| Best for | "Where is *some_file*?" | Anything else |

---

## 10. Reviewing the slide quizzes

### Quiz Slide 20

The screenshot listed `/dev` entries from `ls -l /dev | grep b`.

1. **Two block devices** (anything with `brw-` prefix): `dm-0`, `dm-1`, `sda`, `sda1`, `sda2`, `sda3`, `sdb`, `sr0`.
2. **What's stored in `/dev`?** Files representing every block device and character device attached to the system, plus virtual devices provided by the kernel.

### Quiz Slide 21

From the `fdisk` output of `/dev/sda`:

| Question | Answer |
|---|---|
| a. Block device name of the disk | `/dev/sda` |
| b. How many partitions, and their names | 3 partitions: `/dev/sda1`, `/dev/sda2`, `/dev/sda5`. Note `sda3` and `sda4` are skipped — `sda2` is the extended container, and logical partitions always start at 5. |
| c. Partition scheme | **MBR** (`Disklabel type: dos`) |
| d. Unit sector size | 512 bytes |
| e. Where is `/boot` stored? | `/dev/sda1` — it has the `*` (boot) flag |
| f. "Start" and "End" interpretation | Start and end **sector numbers**. The partition occupies all sectors from Start to End inclusive. Size in bytes = (End − Start + 1) × 512. |

---

## 11. Summary checklist

You should now be able to:

- [ ] Explain the storage stack from block device up to mount point
- [ ] Recognise block-device naming patterns (`sd*`, `vd*`, `nvme*n*`, `mmcblk*`)
- [ ] Tell MBR and GPT apart by their characteristics and by `fdisk -l` output
- [ ] Explain why MBR uses extended + logical partitions and why logicals start at 5
- [ ] Name the default RHEL file system (**XFS**) and at least three others
- [ ] Use `lsblk`, `blkid`, `df`, `du`, `fdisk -l`, `parted print` to inspect storage
- [ ] Read an `/etc/fstab` line and explain each of the six fields
- [ ] Choose between `locate` and `find` for a given task

Once you're confident here, move on to **Lesson 10**, where you'll actually create and manage partitions.
