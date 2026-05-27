# Linux Administration Combined Lab (Lesson 10, 11, 12)

==================================================

# 🎯 OVERALL CONCEPT

Disk → Partition → Filesystem → Mount → Use
             ↓
           Swap
             ↓
            LVM

==================================================

# 🧩 LESSON 10 (B) – PARTITIONING (PARTED)

## Visual

## Commands (FULL FLOW)

lsblk

parted /dev/sdb mklabel msdos

parted /dev/sdb mkpart primary ext4 1MiB 256MB
parted /dev/sdb mkpart primary ext4 256MB 768MB

udevadm settle
lsblk

mkfs.ext4 -L app_data /dev/sdb1
mkfs.ext4 -L backup_data /dev/sdb2

mkdir -p /mnt/app_data /mnt/backup_data

mount /dev/sdb1 /mnt/app_data
mount /dev/sdb2 /mnt/backup_data

# test
touch /mnt/app_data/file.txt
cp /etc/passwd /mnt/backup_data/

# verify
df -h
mount | grep sdb

# persistent
echo "/dev/sdb1 /mnt/app_data ext4 defaults 0 0" >> /etc/fstab
echo "/dev/sdb2 /mnt/backup_data ext4 defaults 0 0" >> /etc/fstab
systemctl daemon-reexec

==================================================

# 🧠 LESSON 11 – SWAP

## Visual
## Commands (FULL FLOW)

free -h

# create swap
dd if=/dev/zero of=/swapfile bs=1M count=256
chmod 600 /swapfile
mkswap /swapfile

# activate
swapon /swapfile

# verify
swapon -s
free -h

# persistent
echo "/swapfile swap swap defaults 0 0" >> /etc/fstab
systemctl daemon-reload

# monitor
watch swapon -s

# disable
swapoff /swapfile

==================================================

# 🧠 LESSON 12 – LVM

## Visual

## Commands (FULL FLOW)

# prepare disk
parted /dev/sdb mklabel msdos
parted /dev/sdb mkpart primary 1MiB 300MB
parted /dev/sdb set 1 lvm on

# create PV
pvcreate /dev/sdb1
pvs

# create VG
vgcreate vg_data /dev/sdb1
vgs

# create LV
lvcreate -L 200M -n lv_app vg_data
lvs

# filesystem
mkfs.xfs /dev/vg_data/lv_app

# mount
mkdir /lv_data
mount /dev/vg_data/lv_app /lv_data

# persist
echo "/dev/vg_data/lv_app /lv_data xfs defaults 0 0" >> /etc/fstab
systemctl daemon-reload

# extend
lvextend -L +100M /dev/vg_data/lv_app
xfs_growfs /lv_data

# verify
df -h
lvs

# cleanup
umount /lv_data
lvremove /dev/vg_data/lv_app -y
vgremove vg_data -y
pvremove /dev/sdb1

==================================================

# 🎓  QUICK CHECK

Lesson 10 → Create and mount partition
Lesson 11 → Create and activate swap
Lesson 12 → Create and extend LVM

==================================================

# ✅ FINAL TIP

ALWAYS REMEMBER:
- Partition → mkfs → mount
- Swap → mkswap → swapon
- LVM → pv → vg → lv

==================================================
