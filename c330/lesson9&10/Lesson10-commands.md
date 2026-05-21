# Lesson 10 – Creating and Managing Partitions (RHEL 9)

A step-by-step lab guide for creating, mounting, and managing partitions and
filesystems from the command line, **with sample output at every step** so you
can confirm your results look correct.

> **Before you begin**
> - All commands need root privileges. Either prefix each with `sudo`, or
>   become root once with `sudo -i`.
> - Replace every `<yourname>` and `<student_id>` with your real name and ID.
> - Identify your disks first — never run `fdisk` against the wrong device.
> - Capture screenshots of `lsblk`, `df -h`, `blkid`, and `ls -l` outputs as proof.
> - Sample outputs below assume the username `john` and student ID `2401234`.
>   Yours will differ — that is expected.

```bash
lsblk                    # list all block devices
sudo fdisk -l /dev/sdb   # inspect the target disk
```

**Sample output of `lsblk` (before you start):**

```
NAME   MAJ:MIN RM  SIZE RO TYPE MOUNTPOINTS
sda      8:0    0   20G  0 disk
├─sda1   8:1    0    1G  0 part /boot
└─sda2   8:2    0   19G  0 part /
sdb      8:16   0    1G  0 disk
sr0     11:0    1 1024M  0 rom
```

> Notice `sdb` has **no partitions yet** — that is the clean starting state.

---

## Question 1 — Working with /dev/sdb

### a) Create a 256MB ext4 partition and mount on /mnt/&lt;yourname&gt;

Open the disk in `fdisk`:

```bash
sudo fdisk /dev/sdb
```

Type the following inside `fdisk`, one entry per line:

```
n        # new partition
p        # primary
1        # partition number 1
<Enter>  # accept default first sector
+256M    # size
w        # write changes and exit
```

**Sample `fdisk` session (what you will actually see):**

```
Command (m for help): n
Partition type
   p   primary (0 primary, 0 extended, 4 free)
   e   extended (container for logical partitions)
Select (default p): p
Partition number (1-4, default 1): 1
First sector (2048-2097151, default 2048): <Enter>
Last sector, +/-sectors or +/-size{K,M,G,T,P} (2048-2097151, default 2097151): +256M

Created a new partition 1 of type 'Linux' and of size 256 MiB.

Command (m for help): w
The partition table has been altered.
Syncing disks.
```

Create the filesystem and mount it:

```bash
sudo mkfs.ext4 /dev/sdb1
sudo mkdir -p /mnt/<yourname>
sudo mount /dev/sdb1 /mnt/<yourname>
df -h /mnt/<yourname>          # verify the mount
```

**Sample output of `mkfs.ext4`:**

```
mke2fs 1.46.5 (30-Dec-2021)
Creating filesystem with 262144 1k blocks and 65536 inodes
Filesystem UUID: a1b2c3d4-5678-90ab-cdef-1234567890ab
...
Writing superblocks and filesystem accounting information: done
```

**Sample output of `df -h /mnt/john`:**

```
Filesystem      Size  Used Avail Use% Mounted on
/dev/sdb1       241M   14K  225M   1% /mnt/john
```

### b) Test access by creating a file

```bash
sudo touch /mnt/<yourname>/c330_<yourname>.txt
ls -l /mnt/<yourname>
```

**Sample output of `ls -l /mnt/john`:**

```
total 12
-rw-r--r--. 1 root root     0 May 21 10:14 c330_john.txt
drwx------. 2 root root 12288 May 21 10:12 lost+found
```

> `lost+found` is created automatically by ext4 — that is normal, not an error.

### c) Create a 512MB ext4 partition and mount on /mnt/&lt;student_id&gt;

```bash
sudo fdisk /dev/sdb
```

Inside `fdisk`:

```
n
p
2
<Enter>
+512M
w
```

Then:

```bash
sudo mkfs.ext4 /dev/sdb2
sudo mkdir -p /mnt/<student_id>
sudo mount /dev/sdb2 /mnt/<student_id>
df -h
```

**Sample output of `df -h` (relevant lines):**

```
Filesystem      Size  Used Avail Use% Mounted on
/dev/sdb1       241M   14K  225M   1% /mnt/john
/dev/sdb2       488M   24K  452M   1% /mnt/2401234
```

### d) Copy /etc/passwd and /etc/group, then verify

```bash
sudo cp /etc/passwd /etc/group /mnt/<student_id>/
ls -l /mnt/<student_id>
```

**Sample output of `ls -l /mnt/2401234`:**

```
total 28
drwx------. 2 root root 12288 May 21 10:18 lost+found
-rw-r--r--. 1 root root  1024 May 21 10:19 group
-rw-r--r--. 1 root root  2891 May 21 10:19 passwd
```

> Seeing both `group` and `passwd` confirms the copy succeeded.

### e) Show output to your lecturer

```bash
lsblk
df -h | grep sdb
ls -l /mnt/<yourname> /mnt/<student_id>
```

**Sample output of `lsblk` (now showing both partitions):**

```
NAME   MAJ:MIN RM  SIZE RO TYPE MOUNTPOINTS
sdb      8:16   0    1G  0 disk
├─sdb1   8:17   0  256M  0 part /mnt/john
└─sdb2   8:18   0  512M  0 part /mnt/2401234
```

### f) Unmount both partitions

```bash
sudo umount /mnt/<yourname>
sudo umount /mnt/<student_id>
```

> No output means success. If you see `target is busy`, run `cd ~` first
> (you may be standing inside the mount point), then try again.

**Verify they are unmounted with `lsblk`:**

```
sdb      8:16   0    1G  0 disk
├─sdb1   8:17   0  256M  0 part
└─sdb2   8:18   0  512M  0 part
```

> The `MOUNTPOINTS` column is now blank — confirming both are unmounted.

### g) Delete the partitions

```bash
sudo fdisk /dev/sdb
```

Inside `fdisk`:

```
d        # delete
1        # partition number 1
d        # delete
2        # partition number 2 (auto-selected if only one remains)
w        # write and exit
```

**Sample `fdisk` delete session:**

```
Command (m for help): d
Partition number (1,2, default 2): 1
Partition 1 has been deleted.

Command (m for help): d
Selected partition 2
Partition 2 has been deleted.

Command (m for help): w
The partition table has been altered.
Syncing disks.
```

Verify they are gone:

```bash
lsblk
sudo fdisk -l /dev/sdb
```

**Sample output — `sdb` is clean again:**

```
sdb      8:16   0    1G  0 disk
```

---

## Question 2 — New 2GB disk with persistent mounting

### a) Attach a new 2GB hard disk

Add the disk in your VM software (VirtualBox / VMware), not the CLI. After
attaching (and rebooting if needed), identify the new disk:

```bash
lsblk
```

**Sample output (new 2GB disk appears as `sdc`):**

```
NAME   MAJ:MIN RM  SIZE RO TYPE MOUNTPOINTS
sda      8:0    0   20G  0 disk
sdb      8:16   0    1G  0 disk
sdc      8:32   0    2G  0 disk
```

The new disk usually appears as `/dev/sdc` (since `sdb` already exists).
**The steps below use `/dev/sdc` — adjust if yours differs.**

### b) Create a 1GB ext4 partition and mount on /mnt/E62A

```bash
sudo fdisk /dev/sdc
```

Inside `fdisk`:

```
n
p
1
<Enter>
+1G
w
```

Then:

```bash
sudo mkfs.ext4 /dev/sdc1
sudo mkdir -p /mnt/E62A
sudo mount /dev/sdc1 /mnt/E62A
df -h /mnt/E62A
```

**Sample output of `df -h /mnt/E62A`:**

```
Filesystem      Size  Used Avail Use% Mounted on
/dev/sdc1       974M   24K  907M   1% /mnt/E62A
```

### c) Test access by creating a file

```bash
sudo touch /mnt/E62A/soi_c330.txt
ls -l /mnt/E62A
```

**Sample output:**

```
total 16
drwx------. 2 root root 16384 May 21 10:30 lost+found
-rw-r--r--. 1 root root     0 May 21 10:31 soi_c330.txt
```

### d) Copy /etc/hosts

```bash
sudo cp /etc/hosts /mnt/E62A/
ls -l /mnt/E62A
```

**Sample output:**

```
total 20
-rw-r--r--. 1 root root   158 May 21 10:32 hosts
drwx------. 2 root root 16384 May 21 10:30 lost+found
-rw-r--r--. 1 root root     0 May 21 10:31 soi_c330.txt
```

### e) Create a 512MB ext4 partition and mount persistently on /mnt/E62B

```bash
sudo fdisk /dev/sdc
```

Inside `fdisk`:

```
n
p
2
<Enter>
+512M
w
```

Create the filesystem and mountpoint:

```bash
sudo mkfs.ext4 /dev/sdc2
sudo mkdir -p /mnt/E62B
```

Get the partition UUID (recommended for persistent mounts):

```bash
sudo blkid /dev/sdc2
```

**Sample output of `blkid`:**

```
/dev/sdc2: UUID="f9e8d7c6-b5a4-3210-fedc-ba9876543210" TYPE="ext4" PARTUUID="1a2b3c4d-02"
```

> Copy the **UUID** value (the long string in quotes) — you will paste it into
> fstab next.

Edit `/etc/fstab`:

```bash
sudo vi /etc/fstab
```

Add one line at the bottom — using the UUID (preferred):

```
UUID=f9e8d7c6-b5a4-3210-fedc-ba9876543210   /mnt/E62B   ext4   defaults   0 0
```

Or the simpler device-name version:

```
/dev/sdc2   /mnt/E62B   ext4   defaults   0 0
```

Save and exit vi (`Esc`, then `:wq`), then mount everything from fstab:

```bash
sudo mount -a
df -h /mnt/E62B
```

**Sample output of `df -h /mnt/E62B`:**

```
Filesystem      Size  Used Avail Use% Mounted on
/dev/sdc2       488M   24K  452M   1% /mnt/E62B
```

> If `mount -a` runs with **no errors**, the fstab entry is correct.
> An error means a typo — fix it now, before rebooting, or the system may
> fail to boot.

### f) Verify the fstab entry

```bash
cat /etc/fstab
findmnt /mnt/E62B          # confirms it is actually mounted
```

**Sample output of `cat /etc/fstab` (your new line at the bottom):**

```
#
# /etc/fstab
#
UUID=11111111-2222-3333-4444-555555555555  /      xfs   defaults  0 0
UUID=66666666-7777-8888-9999-000000000000  /boot  xfs   defaults  0 0
UUID=f9e8d7c6-b5a4-3210-fedc-ba9876543210  /mnt/E62B  ext4  defaults  0 0
```

**Sample output of `findmnt /mnt/E62B`:**

```
TARGET    SOURCE    FSTYPE OPTIONS
/mnt/E62B /dev/sdc2 ext4   rw,relatime
```

### g) Copy /var/log/messages to /mnt/E62B

> **Note:** RHEL 9 uses `journald` and may **not** have `/var/log/messages`
> by default unless `rsyslog` is installed and running. Check first.

```bash
ls -l /var/log/messages
```

**If it exists, you will see something like:**

```
-rw-------. 1 root root 48213 May 21 10:40 /var/log/messages
```

Then copy it:

```bash
sudo cp /var/log/messages /mnt/E62B/
```

**If it does NOT exist, you will instead see:**

```
ls: cannot access '/var/log/messages': No such file or directory
```

In that case, install and start rsyslog, or copy an existing log:

```bash
sudo dnf install -y rsyslog
sudo systemctl enable --now rsyslog
# wait a moment for logs to populate, then:
sudo cp /var/log/messages /mnt/E62B/

# Alternative — copy a log that already exists:
sudo cp /var/log/secure /mnt/E62B/
```

### h) Verify the files were copied

```bash
ls -l /mnt/E62B
```

**Sample output:**

```
total 64
drwx------. 2 root root 16384 May 21 10:35 lost+found
-rw-------. 1 root root 48213 May 21 10:41 messages
```

---

## Full worked example (Question 1, start to finish)

This is the exact sequence of commands for Q1 with `john` / `2401234`, with no
gaps — useful as a dry run before you do it for real.

```bash
# --- a) 256MB partition ---
sudo fdisk /dev/sdb        # n, p, 1, Enter, +256M, w
sudo mkfs.ext4 /dev/sdb1
sudo mkdir -p /mnt/john
sudo mount /dev/sdb1 /mnt/john
df -h /mnt/john

# --- b) test access ---
sudo touch /mnt/john/c330_john.txt
ls -l /mnt/john

# --- c) 512MB partition ---
sudo fdisk /dev/sdb        # n, p, 2, Enter, +512M, w
sudo mkfs.ext4 /dev/sdb2
sudo mkdir -p /mnt/2401234
sudo mount /dev/sdb2 /mnt/2401234
df -h

# --- d) copy and verify ---
sudo cp /etc/passwd /etc/group /mnt/2401234/
ls -l /mnt/2401234

# --- e) show output ---
lsblk
df -h | grep sdb

# --- f) unmount ---
sudo umount /mnt/john
sudo umount /mnt/2401234

# --- g) delete partitions ---
sudo fdisk /dev/sdb        # d, 1, d, 2, w
lsblk
```

---

## Quick reference / troubleshooting

| Task | Command |
|------|---------|
| List block devices | `lsblk` |
| Inspect a disk | `sudo fdisk -l /dev/sdX` |
| Re-read partition table without reboot | `sudo partprobe /dev/sdX` |
| Show UUIDs and filesystem types | `sudo blkid` |
| Show disk usage of mounts | `df -h` |
| Confirm a specific mount | `findmnt /mnt/<name>` |
| Test all fstab entries | `sudo mount -a` |
| See what is using a busy mount | `sudo lsof /mnt/<name>` or `sudo fuser -m /mnt/<name>` |

### Common pitfalls (with the error you will see)

- **Wrong device name.** Always run `lsblk` first. `sdb`, `sdc`, etc. depend
  on attach order.

- **`fdisk` shows nothing after writing.** Run `sudo partprobe /dev/sdX` or
  reboot so the kernel re-reads the partition table.

- **Cannot unmount — "target is busy".**
  ```
  umount: /mnt/john: target is busy.
  ```
  Run `cd ~` first (you may be inside the mount point), then `umount` again.

- **Wrong filesystem at mount time.**
  ```
  mount: /mnt/E62A: wrong fs type, bad option, bad superblock...
  ```
  You probably forgot `mkfs.ext4`, or pointed at the disk (`sdc`) instead of
  the partition (`sdc1`).

- **Broken fstab = unbootable system.** Test with `sudo mount -a` before
  rebooting. Using a UUID instead of `/dev/sdc2` avoids breakage if device
  names change.

---

*Reference guide for C330 Lesson 10. Run these on your own VM so partition
names and UUIDs match your system. Sample outputs are illustrative — your
UUIDs, sizes, and timestamps will differ.*
