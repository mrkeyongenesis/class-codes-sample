# C330 Storage — Quick Reference Cheat Sheet

One-page lookup. For the why-and-how, see `01_lesson9_notes.md` and `02_lesson10_notes.md`.

## Inspect

```bash
lsblk                              # tree of block devices
lsblk -fp                          # tree + FSTYPE, UUID, full paths
lsblk -d                           # disks only
sudo blkid                         # UUIDs of all formatted partitions
sudo blkid /dev/sdb1               # one device
sudo blkid -s UUID -o value /dev/sdb1   # raw UUID for scripts
df -h                              # disk free, human-readable (1024-base)
df -H                              # disk free, 1000-base
du -sh /home                       # total size of a directory
sudo fdisk -l                      # detailed partition table
sudo parted /dev/sdb print         # parted's view of one disk
sudo parted --list                 # parted's view of all disks
cat /proc/partitions               # kernel's view of partitions
findmnt /mnt/data                  # who is mounted there?
```

## Partition (parted)

```bash
sudo parted /dev/sdb mklabel msdos                          # MBR
sudo parted /dev/sdb mklabel gpt                            # GPT
sudo parted /dev/sdb mkpart primary ext4 2048s 128MB        # primary
sudo parted /dev/sdb mkpart extended 2048s 100%             # extended container (MBR)
sudo parted /dev/sdb mkpart logical ext4 4096s 512MB        # logical (inside extended)
sudo parted /dev/sdb rm 1                                   # delete partition 1
sudo parted /dev/sdb print                                  # show table

# Interactive mode
sudo parted /dev/sdb
(parted) help
(parted) mkpart
(parted) p
(parted) rm 1
(parted) q
```

## Refresh kernel

```bash
sudo udevadm settle           # wait for device events to finish
sudo partprobe /dev/sdb       # tell kernel to reread partition table
```

## Format (mkfs)

```bash
sudo mkfs.ext4 /dev/sdb1                # ext4
sudo mkfs.ext4 -L misc /dev/sdb1        # ext4 with label
sudo mkfs.xfs  /dev/sdb1                # XFS (RHEL default)
sudo mkfs.xfs  -L misc /dev/sdb1        # XFS with label
sudo mkfs -t ext4 /dev/sdb1             # alternative syntax

# Relabel after creation
sudo e2label  /dev/sdb1 misc            # ext family
sudo xfs_admin -L misc /dev/sdb1        # XFS
```

## Mount / unmount

```bash
sudo mkdir -p /mnt/data
sudo mount /dev/sdb1 /mnt/data
sudo mount UUID="<uuid>" /mnt/data
sudo mount LABEL=misc /mnt/data
sudo mount -a                            # mount everything in /etc/fstab

sudo umount /mnt/data                    # by mount point
sudo umount /dev/sdb1                    # by device
sudo umount -l /mnt/data                 # lazy (use only if busy)

# Diagnose "target is busy"
sudo lsof /mnt/data
sudo fuser -m /mnt/data
```

## Persistent mounts (/etc/fstab)

```bash
# 1. Get UUID
UUID=$(sudo blkid -s UUID -o value /dev/sdb1)

# 2. Append (unprotect first if chattr +a is set)
sudo chattr -a /etc/fstab 2>/dev/null
echo "UUID=$UUID  /mnt/data  ext4  defaults  0  2" | sudo tee -a /etc/fstab

# 3. Reload systemd and test
sudo systemctl daemon-reload
sudo mount -a

# 4. (Optional) Reprotect
sudo chattr +a /etc/fstab
sudo lsattr /etc/fstab
```

## /etc/fstab line format

```
#device           mount_point   filesystem  mount_options  dump  fsck
UUID=abcd-1234    /mnt/data     ext4        defaults       0     2
```

| # | Field | Common values |
|---|---|---|
| 1 | Device | `UUID=…`, `LABEL=…`, `/dev/sdb1` |
| 2 | Mount point | `/mnt/data` (must exist) |
| 3 | Filesystem | `ext4`, `xfs`, `swap`, `iso9660`, `vfat`, `auto` |
| 4 | Options | `defaults`, `rw`, `ro`, `noauto`, `user`, `noatime` |
| 5 | Dump | `0` (skip), `1` (back up) |
| 6 | fsck | `0` (skip), `1` (root only), `2` (after root) |

## Back up & restore partition table

```bash
sudo sfdisk -d /dev/sda > /tmp/partition.sda     # back up
sudo sfdisk /dev/sda < /tmp/partition.sda        # restore
```

## Find files

```bash
sudo updatedb                          # refresh locate's index
locate -n 5 passwd                     # first 5 matches
find /etc -name "pas*"                 # by name
find / -name "*.conf" -size +1M        # configs > 1 MB
find /home -mtime -7                   # modified in last 7 days
find / -user student -type f           # owned by user "student"
```

## Disk naming patterns

| Pattern | Type |
|---|---|
| `/dev/sd[a-z]` | SATA / SAS / USB |
| `/dev/vd[a-z]` | virtio (some VMs) |
| `/dev/nvme[0-9]n[0-9]` | NVMe SSD |
| `/dev/mmcblk[0-9]` | SD / MMC / eMMC |
| `/dev/sd[a-z][1-9]+` | Partition (number ≥ 5 ⇒ logical on MBR) |
| `/dev/sr[0-9]` | Optical (CD/DVD) |

## MBR vs GPT at a glance

| | MBR (`msdos`) | GPT (`gpt`) |
|---|---|---|
| Max primary partitions | 4 | 128 |
| Max partition size | 2 TB | ~9.4 ZB |
| Backup table | No | Yes (end of disk) |
| Firmware | BIOS | UEFI |
| Address size | 32-bit | 64-bit |
| Logical partitions | Yes (start at 5) | N/A |

## chattr flags

| Flag | Meaning | Effect |
|---|---|---|
| `+a` | Append-only | Can append (`>>`), can't modify or delete (even root) |
| `+i` | Immutable | Can't modify, delete, rename, or link at all |
| `-a` / `-i` | Remove flag | Allows normal modification |
| `lsattr <file>` | Show flags | — |

## Most-used file system options

| Option | Meaning |
|---|---|
| `defaults` | rw, suid, dev, exec, auto, nouser, async |
| `rw` / `ro` | Read-write / read-only |
| `noauto` | Don't mount automatically with `mount -a` |
| `user` | Any user can mount (not just root) |
| `noatime` | Don't update access times (faster) |
| `noexec` | Don't allow executables on this FS |
| `nosuid` | Ignore setuid/setgid bits |

## Common file systems

| FS | Used for |
|---|---|
| `xfs` | RHEL default, high-performance journaling |
| `ext4` | Linux general-purpose, mature |
| `swap` | Virtual memory (not files) |
| `vfat` / `FAT32` | EFI system partition, USB sticks |
| `iso9660` | CD-ROMs |
| `exfat` | Large removable media (RHEL 9+) |
| `gfs2` | Cluster shared storage |

## Safety reminders

- Run `lsblk` before every destructive command. Confirm the device name.
- Never run `parted`, `mkfs`, or `dd` on `/dev/sda` (your OS disk) without backups.
- After editing `/etc/fstab`, always test with `sudo mount -a` **before** rebooting.
- Step out of a mount point (`cd ~`) before trying to unmount it.
