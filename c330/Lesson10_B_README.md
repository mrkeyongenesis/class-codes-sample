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
# Lesson 10 – Linux Disk Partitioning (Using PARTED)

---

## 🎯 Learning Objectives
By the end of this lab, you will be able to:
- Identify storage devices
- Create partitions using `parted`
- Format partitions with file systems
- Mount and access storage
- Configure persistent mounting

---

## 🧠 WHY THIS IS IMPORTANT

A disk is **not usable until it is prepared**.

Real-world:
- Separate partitions for apps, logs, backups
- Prevent system failure when disk fills up

---

## 🔁 BIG PICTURE FLOW

Disk → Partition → File System → Mount → Use

---

## 🧩 VISUAL OVERVIEW



---

## 🪜 STEP-BY-STEP PROCESS (MENTAL MODEL)

| Step | Action | Purpose |
|------|--------|--------|
| 1 | Identify disk | Know target |
| 2 | Create partition table | Prepare disk |
| 3 | Create partitions | Allocate space |
| 4 | Format filesystem | Make usable |
| 5 | Mount | Attach to Linux |
| 6 | Persist | Survive reboot |

---

## ⚙️ LAB SCENARIO

You are a system administrator.

A new disk `/dev/sdb` (2GB) is added.

You must:
- Create **256MB partition → App storage**
- Create **512MB partition → Backup storage**
- Mount and make persistent

---

## 🧪 STEP 1 — Identify Disk

```bash
lsblk

``
parted /dev/sdb mklabel msdos

---

## QUESTIONS
- Explain partitioning workflow
- Why filesystem is needed?
- Create partition and mount
