# Lesson 10 – Linux Disk Partitioning (Using PARTED)

## WHY THIS MATTERS
A disk is raw and unusable until prepared. Partitioning allows isolation, organisation, and stability.

---

## BIG PICTURE
Disk → Partition → Filesystem → Mount → Use

---

## VISUAL OVERVIEW
(Image: partition workflow diagram)

---

## STEP FLOW
1. Identify disk → lsblk
2. Create label → parted mklabel
3. Create partition → parted mkpart
4. Create filesystem → mkfs.ext4
5. Mount → mount
6. Persist → /etc/fstab

---

## HANDS-ON LAB

### Step 1
lsblk

### Step 2
parted /dev/sdb mklabel msdos

### Step 3
parted /dev/sdb mkpart primary ext4 1MiB 256MB

### Step 4
mkfs.ext4 /dev/sdb1

### Step 5
mkdir /data
mount /dev/sdb1 /data

### Step 6
Touch test file

---

## EXAM QUESTIONS
- Explain partitioning workflow
- Why filesystem is needed?
- Create partition and mount
