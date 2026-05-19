# C330 Storage — Process and Flow Charts

Visual diagrams for every workflow in Lessons 9 & 10. These render directly in GitHub, VS Code (with the Mermaid extension), and most modern Markdown viewers.

If your viewer doesn't render Mermaid, paste any diagram block at <https://mermaid.live/> to see it.

---

## 1. The Linux storage stack

How a file path resolves all the way down to physical sectors.

```mermaid
flowchart TB
    F["📄 File<br/>/home/student/notes.txt"]
    D["📁 Directory<br/>(part of file system tree)"]
    M["⛓️ Mount Point<br/>/mnt/data"]
    FS["🗂️ File System<br/>xfs / ext4 / vfat"]
    P["🧩 Partition<br/>/dev/sdb1"]
    B["💽 Block Device<br/>/dev/sdb"]
    H["🛠️ Physical / Virtual Disk<br/>SATA, NVMe, virtio"]

    F --> D --> M --> FS --> P --> B --> H

    classDef top fill:#dbeafe,stroke:#1e40af,color:#1e3a8a
    classDef mid fill:#fef3c7,stroke:#92400e,color:#78350f
    classDef bot fill:#dcfce7,stroke:#166534,color:#14532d
    class F,D top
    class M,FS mid
    class P,B,H bot
```

**Reading direction:** Top = what you (the user) see. Bottom = what the hardware sees. To create new storage, you build the layers **from the bottom up**.

---

## 2. The 8-step "add new storage" workflow

The master recipe in Lesson 10. Memorise this — every disk you ever add follows the same eight steps.

```mermaid
flowchart TD
    Start(["🆕 New disk attached"]) --> S1
    S1["1. IDENTIFY<br/><code>lsblk</code><br/><code>fdisk -l</code>"]
    S2["2. BACK UP partition table<br/><code>sfdisk -d /dev/sda &gt; /tmp/partition.sda</code><br/><i>(optional but recommended)</i>"]
    S3["3. WRITE DISK LABEL<br/><code>parted /dev/sdb mklabel msdos</code><br/><i>or</i> <code>mklabel gpt</code>"]
    S4["4. CREATE PARTITION<br/><code>parted /dev/sdb mkpart primary ext4 2048s 128MB</code>"]
    S5["5. REFRESH KERNEL<br/><code>udevadm settle</code><br/><code>cat /proc/partitions</code>"]
    S6["6. CREATE FILE SYSTEM<br/><code>mkfs.ext4 /dev/sdb1</code>"]
    S7["7. LABEL FILE SYSTEM<br/><code>mkfs.ext4 -L misc /dev/sdb1</code><br/><i>(optional)</i>"]
    S8{{"8. MOUNT — choose one"}}
    S8a["8a. MANUAL<br/><code>mount /dev/sdb1 /misc</code><br/><i>temporary — lost on reboot</i>"]
    S8b["8b. PERSISTENT<br/>Edit <code>/etc/fstab</code><br/><i>permanent — survives reboot</i>"]
    End(["✅ Storage ready"])

    S1 --> S2 --> S3 --> S4 --> S5 --> S6 --> S7 --> S8
    S8 --> S8a --> End
    S8 --> S8b --> End

    classDef warn fill:#fee2e2,stroke:#991b1b,color:#7f1d1d
    classDef safe fill:#dcfce7,stroke:#166534,color:#14532d
    classDef step fill:#dbeafe,stroke:#1e40af,color:#1e3a8a
    classDef opt fill:#f3f4f6,stroke:#6b7280,color:#374151
    class S3,S4,S6 warn
    class S2,S7 opt
    class S1,S5 step
    class S8a,S8b safe
```

**Colour key:** 🔴 destructive steps (data loss risk) — 🔵 read-only or kernel steps — ⚪ optional best-practice — 🟢 final activation.

---

## 3. Decision tree — which partition scheme should I use?

```mermaid
flowchart TD
    A{"What's the disk size?"} -->|"> 2 TB"| GPT["✅ Use GPT<br/><code>parted mklabel gpt</code>"]
    A -->|"≤ 2 TB"| B{"Modern UEFI system?"}
    B -->|Yes| GPT
    B -->|No, legacy BIOS| C{"Need > 4 partitions?"}
    C -->|Yes| GPT
    C -->|No| MBR["✅ Use MBR<br/><code>parted mklabel msdos</code>"]

    GPT --> X["📦 GPT features:<br/>• up to 128 partitions<br/>• backup table at end<br/>• 64-bit addresses<br/>• every partition equal"]
    MBR --> Y["📦 MBR features:<br/>• 4 primary partitions max<br/>• extended → up to 15 logical<br/>• 32-bit addresses<br/>• /boot in a primary"]

    classDef gpt fill:#dcfce7,stroke:#166534,color:#14532d
    classDef mbr fill:#fef3c7,stroke:#92400e,color:#78350f
    classDef q fill:#dbeafe,stroke:#1e40af,color:#1e3a8a
    class GPT,X gpt
    class MBR,Y mbr
    class A,B,C q
```

In modern environments **default to GPT** unless you have a specific reason (legacy bootloader, dual-boot with old Windows, etc.) to choose MBR.

---

## 4. MBR partition layout — extended + logical

How the 4-primary limit gets stretched to 15 partitions via extended/logical.

```mermaid
flowchart LR
    subgraph DISK["💽 /dev/sdb (MBR disk)"]
        direction LR
        MBR_BOOT["MBR<br/>boot record<br/>+ partition table<br/><i>(sector 0)</i>"]
        P1["sdb1<br/><b>primary</b><br/>ext4"]
        P2["sdb2<br/><b>primary</b><br/>ext4"]
        P3["sdb3<br/><b>primary</b><br/>ext4"]
        subgraph EXT["sdb4 (EXTENDED — container, not formatted)"]
            direction LR
            L5["sdb5<br/>logical<br/>ext4"]
            L6["sdb6<br/>logical<br/>ext4"]
            L7["sdb7<br/>logical<br/>ext4"]
            DOTS["..."]
        end
        MBR_BOOT --> P1 --> P2 --> P3 --> EXT
    end

    classDef pri fill:#dbeafe,stroke:#1e40af,color:#1e3a8a
    classDef ext fill:#fef9c3,stroke:#854d0e,color:#713f12
    classDef log fill:#dcfce7,stroke:#166534,color:#14532d
    classDef hdr fill:#e5e7eb,stroke:#374151,color:#1f2937
    class P1,P2,P3 pri
    class EXT ext
    class L5,L6,L7,DOTS log
    class MBR_BOOT hdr
```

**Three rules to remember:**
- Only one extended container per disk.
- Extended partitions hold no file system — they are containers only.
- Logical partition numbering **always starts at 5**, even if you only have 1 primary.

---

## 5. GPT partition layout — all equal

By contrast, GPT has no extended/logical distinction.

```mermaid
flowchart LR
    subgraph DISK["💽 /dev/sdb (GPT disk)"]
        direction LR
        PG["Primary GPT<br/>+ partition table<br/><i>(start of disk)</i>"]
        P1["sdb1<br/>any FS"]
        P2["sdb2<br/>any FS"]
        P3["sdb3<br/>any FS"]
        P4["sdb4<br/>any FS"]
        P5["sdb5<br/>any FS"]
        DOTS["... up to 128"]
        BG["Backup GPT<br/><i>(end of disk)</i>"]
        PG --> P1 --> P2 --> P3 --> P4 --> P5 --> DOTS --> BG
    end

    classDef part fill:#dbeafe,stroke:#1e40af,color:#1e3a8a
    classDef gpt fill:#e0e7ff,stroke:#3730a3,color:#312e81
    class P1,P2,P3,P4,P5,DOTS part
    class PG,BG gpt
```

The **backup GPT** at the end of the disk is GPT's safety net — if the primary header is corrupted, the system can recover from this copy.

---

## 6. Mount lifecycle — manual vs persistent

```mermaid
flowchart TD
    Need(["📌 I need /dev/sdb1 mounted"])
    Need --> Q{"Should it survive reboot?"}

    Q -->|"NO — one-off use"| Manual
    Q -->|"YES — every boot"| Persistent

    subgraph Manual["🟦 Manual / Temporary"]
        direction TB
        M1["<code>mkdir -p /mnt/data</code>"]
        M2["<code>mount /dev/sdb1 /mnt/data</code>"]
        M3["use the mount<br/>(read, write, copy)"]
        M4["<code>umount /mnt/data</code><br/><i>or wait for reboot</i>"]
        M1 --> M2 --> M3 --> M4
    end

    subgraph Persistent["🟩 Persistent / /etc/fstab"]
        direction TB
        P1["<code>mkdir -p /mnt/data</code>"]
        P2["<code>blkid /dev/sdb1</code><br/>→ get UUID"]
        P3["<code>chattr -a /etc/fstab</code><br/><i>(if append-only set)</i>"]
        P4["edit /etc/fstab<br/>add UUID line"]
        P5["<code>systemctl daemon-reload</code><br/><code>mount -a</code>"]
        P6{"mount -a clean?"}
        P7["<code>chattr +a /etc/fstab</code><br/><i>(optional)</i>"]
        P8["✅ safe to reboot"]
        P9["⚠️ fix syntax<br/>retry"]
        P1 --> P2 --> P3 --> P4 --> P5 --> P6
        P6 -->|Yes| P7 --> P8
        P6 -->|No| P9 --> P4
    end

    classDef ok fill:#dcfce7,stroke:#166534,color:#14532d
    classDef warn fill:#fee2e2,stroke:#991b1b,color:#7f1d1d
    classDef step fill:#dbeafe,stroke:#1e40af,color:#1e3a8a
    class P8 ok
    class P9 warn
    class M1,M2,M3,M4,P1,P2,P3,P4,P5,P7 step
```

**The critical gate is `P6` — never reboot until `mount -a` returns no errors.** A broken `/etc/fstab` can prevent the system from starting.

---

## 7. `umount` troubleshooting flow

```mermaid
flowchart TD
    Start(["🚪 want to unmount /mnt/data"])
    Start --> U1["<code>umount /mnt/data</code>"]
    U1 --> Q1{"error: target is busy?"}

    Q1 -->|No| Done["✅ unmounted"]
    Q1 -->|Yes| F1["<code>cd ~</code><br/>(step out of mount)"]
    F1 --> U2["<code>umount /mnt/data</code>"]
    U2 --> Q2{"still busy?"}

    Q2 -->|No| Done
    Q2 -->|Yes| F2["<code>lsof /mnt/data</code><br/><code>fuser -vm /mnt/data</code><br/>identify the process"]
    F2 --> Q3{"can you close it?"}

    Q3 -->|Yes| F3["close the program / kill PID"]
    F3 --> U3["<code>umount /mnt/data</code>"]
    U3 --> Done

    Q3 -->|"No — last resort"| F4["<code>umount -l /mnt/data</code><br/><i>lazy: detaches now, frees when last ref closes</i>"]
    F4 --> Done

    classDef ok fill:#dcfce7,stroke:#166534,color:#14532d
    classDef warn fill:#fef3c7,stroke:#92400e,color:#78350f
    classDef bad fill:#fee2e2,stroke:#991b1b,color:#7f1d1d
    class Done ok
    class F1,F2,F3 warn
    class F4 bad
```

---

## 8. Cleanup flow — reverse of creation

When tearing down storage, **reverse the build order**: unmount → remove fstab entry → delete partition → erase label.

```mermaid
flowchart TD
    A(["🧹 Want to remove storage"])
    A --> B["1. <code>cd ~</code><br/>(leave the mount point)"]
    B --> C["2. <code>umount /mnt/data</code>"]
    C --> D{"Did it have an fstab entry?"}
    D -->|Yes| E["3. <code>chattr -a /etc/fstab</code><br/>edit /etc/fstab — delete the line<br/><code>systemctl daemon-reload</code>"]
    D -->|No| F
    E --> F["4. <code>parted /dev/sdb rm N</code><br/>(N = partition number)"]
    F --> G["5. <code>udevadm settle</code><br/>verify with <code>lsblk</code>"]
    G --> H["6. <i>(optional)</i> <code>rmdir /mnt/data</code>"]
    H --> Z(["✅ clean"])

    classDef step fill:#dbeafe,stroke:#1e40af,color:#1e3a8a
    classDef warn fill:#fef3c7,stroke:#92400e,color:#78350f
    classDef ok fill:#dcfce7,stroke:#166534,color:#14532d
    class B,C,F,G,H step
    class E warn
    class Z ok
```

Doing this in the wrong order causes errors: deleting a partition while it's mounted breaks the mount; leaving an fstab entry for a deleted partition blocks the next boot.

---

## 9. Pre-flight safety check (mental model)

Before any destructive command, run this mental flowchart. Type the command only after every box says "✅".

```mermaid
flowchart TD
    Cmd(["💣 About to run<br/><code>parted /dev/sdX ...</code><br/><code>mkfs.ext4 /dev/sdX</code><br/><code>dd if=... of=/dev/sdX</code>"])
    Cmd --> C1{"Did I run<br/><code>lsblk</code> just now?"}
    C1 -->|No| F1["❌ STOP<br/>Run <code>lsblk</code> first"]
    C1 -->|Yes| C2{"Does the disk size match<br/>what I expect?"}
    C2 -->|No| F2["❌ STOP<br/>Wrong disk — check the name"]
    C2 -->|Yes| C3{"Is /dev/sdX the<br/>OS disk (usually sda)?"}
    C3 -->|"Yes — sda or root disk"| F3["❌ STOP<br/>This is your OS disk"]
    C3 -->|No| C4{"Are any partitions on it<br/>currently mounted?"}
    C4 -->|Yes| F4["❌ STOP<br/>Unmount first"]
    C4 -->|No| C5{"Did I back up<br/>important data?"}
    C5 -->|No, but disk is empty| Go["✅ Safe to proceed"]
    C5 -->|Yes| Go
    C5 -->|"No, has data I care about"| F5["❌ STOP<br/>Back up first"]

    F1 --> Cmd
    F2 --> Cmd
    F3 --> Cancel(["🛑 Cancel"])
    F4 --> Cmd
    F5 --> Cancel

    classDef ok fill:#dcfce7,stroke:#166534,color:#14532d
    classDef stop fill:#fee2e2,stroke:#991b1b,color:#7f1d1d
    classDef chk fill:#dbeafe,stroke:#1e40af,color:#1e3a8a
    class Go ok
    class F1,F2,F3,F4,F5,Cancel stop
    class C1,C2,C3,C4,C5 chk
```

---

## 10. Where things live — the artefact map

How the file system, mount metadata, and kernel state relate.

```mermaid
flowchart LR
    subgraph onDisk["💽 ON DISK (persistent)"]
        direction TB
        DISK["raw sectors on /dev/sdb"]
        TABLE["partition table<br/>(MBR or GPT)"]
        SUPER["file-system superblock<br/>(includes UUID, label)"]
        DATA["files, directories, metadata"]
        DISK --> TABLE
        DISK --> SUPER
        DISK --> DATA
    end

    subgraph inKernel["⚙️ IN KERNEL (volatile)"]
        direction TB
        PROC["/proc/partitions<br/>(kernel view)"]
        MOUNTS["/proc/mounts<br/>(active mounts)"]
        MTAB["/etc/mtab → /proc/self/mounts"]
        DEVF["/dev/sdb, /dev/sdb1<br/>(device files)"]
    end

    subgraph configs["📝 CONFIG FILES (persistent)"]
        direction TB
        FSTAB["/etc/fstab<br/>(boot-time mount plan)"]
    end

    TABLE -.->|"<code>udevadm settle</code>"| PROC
    TABLE -.-> DEVF
    SUPER -.->|"<code>blkid</code>"| FSTAB
    FSTAB -.->|"<code>mount -a</code> at boot"| MOUNTS
    MOUNTS -.-> MTAB

    classDef disk fill:#dbeafe,stroke:#1e40af,color:#1e3a8a
    classDef kern fill:#fef3c7,stroke:#92400e,color:#78350f
    classDef cfg fill:#dcfce7,stroke:#166534,color:#14532d
    class DISK,TABLE,SUPER,DATA disk
    class PROC,MOUNTS,MTAB,DEVF kern
    class FSTAB cfg
```

The blue boxes (disk) survive reboot. The yellow boxes (kernel state) are rebuilt on every boot from the blue and green sources. The green box (`/etc/fstab`) is the **link** that ties them together at startup.

---

## 11. Worksheet Q1 flow (Lesson 10)

End-to-end flow of the practical task.

```mermaid
flowchart TD
    A["(a) parted mklabel msdos<br/>parted mkpart primary ext4 2048s 256MB<br/>mkfs.ext4 /dev/sdb1<br/>mount on /mnt/&lt;yourname&gt;"]
    B["(b) touch c330_&lt;yourname&gt;.txt"]
    C["(c) parted mkpart primary ext4 256MB 768MB<br/>mkfs.ext4 /dev/sdb2<br/>mount on /mnt/&lt;student_id&gt;"]
    D["(d) cp /etc/passwd /mnt/&lt;yourname&gt;/<br/>cp /etc/group  /mnt/&lt;student_id&gt;/"]
    E["(e) df -h<br/>👀 show lecturer"]
    F["(f) umount /mnt/&lt;yourname&gt;<br/>umount /mnt/&lt;student_id&gt;"]
    G["(g) parted rm 2<br/>parted rm 1<br/>udevadm settle"]

    A --> B --> C --> D --> E --> F --> G

    classDef build fill:#dbeafe,stroke:#1e40af,color:#1e3a8a
    classDef test fill:#fef3c7,stroke:#92400e,color:#78350f
    classDef teardown fill:#fee2e2,stroke:#991b1b,color:#7f1d1d
    class A,C build
    class B,D,E test
    class F,G teardown
```

🔵 build phase → 🟡 test/use phase → 🔴 teardown phase. Notice the symmetry: every build step has a matching teardown step in reverse order.

---

## 12. Worksheet Q2 flow — persistent mount (Lesson 10)

```mermaid
flowchart TD
    A["(a) Attach 2 GB disk via VMware Settings"] --> B
    B["(b) parted /dev/sdb mklabel msdos<br/>parted mkpart primary ext4 2048s 1024MB<br/>mkfs.ext4 /dev/sdb1<br/>mount on /mnt/E62A (manual)"] --> C
    C["(c) touch soi_c330.txt in /mnt/E62A"] --> D
    D["(d) parted mkpart primary ext4 1024MB 1536MB<br/>mkfs.ext4 /dev/sdb2<br/>blkid -s UUID /dev/sdb2<br/>append UUID line to /etc/fstab<br/>systemctl daemon-reload && mount -a"] --> E
    E["(e) tail /etc/fstab<br/>verify UUID line is present"] --> F
    F["(f) cp /var/log/messages /mnt/E62B/"] --> G
    G["(g) ls -l /mnt/E62B<br/>df -h | grep E62B"]

    classDef manual fill:#dbeafe,stroke:#1e40af,color:#1e3a8a
    classDef persist fill:#fef3c7,stroke:#92400e,color:#78350f
    classDef verify fill:#dcfce7,stroke:#166534,color:#14532d
    class A,B,C manual
    class D persist
    class E,F,G verify
```

🔵 manual mount section → 🟡 the critical persistent-mount step → 🟢 verification.

---

## 13. Recovery from a broken /etc/fstab

If a bad fstab line stops the system from booting, this is the recovery path.

```mermaid
flowchart TD
    A(["💥 System won't boot after fstab edit"])
    A --> B["System drops to<br/>emergency / rescue prompt"]
    B --> C["Log in as root<br/>(enter root password)"]
    C --> D["<code>mount -o remount,rw /</code><br/><i>make root writeable</i>"]
    D --> E["<code>vi /etc/fstab</code><br/>find the broken line<br/>comment it out with <code>#</code><br/>or correct the UUID / syntax"]
    E --> F["<code>mount -a</code><br/>test it works"]
    F --> G{"clean?"}
    G -->|No| E
    G -->|Yes| H["<code>reboot</code>"]
    H --> I(["✅ system boots normally"])

    classDef bad fill:#fee2e2,stroke:#991b1b,color:#7f1d1d
    classDef warn fill:#fef3c7,stroke:#92400e,color:#78350f
    classDef ok fill:#dcfce7,stroke:#166534,color:#14532d
    class A,B bad
    class C,D,E,F warn
    class H,I ok
```

**Prevention is the best cure:** always run `sudo mount -a` *after* editing fstab and *before* rebooting. If `mount -a` is clean, your reboot is safe.

---

## 14. Tool decision matrix

Which command for which job?

```mermaid
flowchart LR
    Q{"What do I want?"}
    Q -->|See disks in a tree| LSBLK["<code>lsblk</code> / <code>lsblk -fp</code>"]
    Q -->|See UUIDs| BLKID["<code>blkid</code>"]
    Q -->|See used / free space| DF["<code>df -h</code>"]
    Q -->|See size of a folder| DU["<code>du -sh dir</code>"]
    Q -->|See partition tables| FDISK["<code>fdisk -l</code> / <code>parted --list</code>"]
    Q -->|Create / edit partitions| PARTED["<code>parted</code> / <code>fdisk</code>"]
    Q -->|Format a partition| MKFS["<code>mkfs.ext4</code> / <code>mkfs.xfs</code>"]
    Q -->|Mount / unmount| MOUNT["<code>mount</code> / <code>umount</code>"]
    Q -->|Find a file by name| FIND["<code>find / -name ...</code><br/><code>locate ...</code>"]
    Q -->|Refresh after parted| UDEV["<code>udevadm settle</code>"]
    Q -->|Make a mount permanent| FSTAB["edit <code>/etc/fstab</code>"]

    classDef read fill:#dbeafe,stroke:#1e40af,color:#1e3a8a
    classDef write fill:#fef3c7,stroke:#92400e,color:#78350f
    classDef destruct fill:#fee2e2,stroke:#991b1b,color:#7f1d1d
    class LSBLK,BLKID,DF,DU,FDISK,FIND read
    class MOUNT,FSTAB,UDEV write
    class PARTED,MKFS destruct
```

🔵 read-only — 🟡 modifies state — 🔴 destructive (can lose data).

---

## How to view these diagrams

**GitHub / GitLab / VS Code:** Markdown previewer renders Mermaid automatically. Just open `05_flow_charts.md`.

**Other Markdown viewers:** Install a Mermaid plugin, or copy any code block between ` ```mermaid` and ` ``` ` and paste into <https://mermaid.live/>.

**Export to image:** From <https://mermaid.live/> click *Export* → PNG/SVG.
