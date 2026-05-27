# Lesson 12 – LVM (Logical Volume Management)

## WHY THIS MATTERS
LVM allows flexible storage (resize without downtime).

---

## STORAGE FLOW
Disk → PV → VG → LV → FS → Mount

---

## VISUAL
(Image: LVM architecture diagram)

---

## PROCESS
Partition → pvcreate → vgcreate → lvcreate → mkfs → mount

---

## HANDS-ON LAB

### Step 1
parted /dev/sdb mklabel msdos

### Step 2
parted /dev/sdb mkpart primary 1MiB 300MB
parted /dev/sdb set 1 lvm on

### Step 3
pvcreate /dev/sdb1

### Step 4
vgcreate vg_data /dev/sdb1

### Step 5
lvcreate -L 200M -n lv_app vg_data

### Step 6
mkfs.xfs /dev/vg_data/lv_app

### Step 7
mount /dev/vg_data/lv_app /lv_data

---

## EXTEND
lvextend -L +100M /dev/vg_data/lv_app
xfs_growfs /lv_data

---

##  QUESTIONS
- Explain PV VG LV
- Why LVM?
- Extend LV
