# Lesson 11 – Swap Space Management

## WHY THIS MATTERS
Swap prevents crashes when RAM is full.

---

## MEMORY FLOW
RAM → Swap (disk backup)

---

## VISUAL
imageturn1search3†image_I29NurwgiQq3MQYnUoPw7Q==
(Image: swap concept diagram)

---

## PROCESS FLOW
Create → mkswap → swapon → persist

---

## HANDS-ON LAB

### Step 1
free -h

### Step 2
dd if=/dev/zero of=/swapfile bs=1M count=256

### Step 3
chmod 600 /swapfile

### Step 4
mkswap /swapfile

### Step 5
swapon /swapfile

---

## VERIFY
swapon -s

---

## QUESTIONS
- What is swap?
- Why slower than RAM?
- Create swap file
