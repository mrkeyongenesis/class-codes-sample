# 🐳 Docker & CI/CD - Visual Guide & Diagrams

## Understanding Docker Flow

### The Docker Architecture (from your diagram)

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                       │
│                    Step 1: Type of Image?                           │
│                                                                       │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
            ┌───────▼───────┐        ┌───────▼──────┐
            │ Existing Image│        │  New Image   │
            └───────┬───────┘        └───────┬──────┘
                    │                        │
                    │                   docker build
                    │                        │
                    └────────────┬───────────┘
                                 │
                      ┌──────────▼──────────┐
                      │   docker run        │
                      │   Step 2: Run it    │
                      └──────────┬──────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
            ┌───────▼──────┐        ┌────────▼─────┐
            │  Local Copy  │        │ No Local Copy│
            │   Exists?    │        │  of Image    │
            └───────┬──────┘        └────────┬─────┘
                    │ YES                   │ NO
                    │                       │
                    │            ┌──────────▼──────┐
                    │            │ Pull from       │
                    │            │ Registry/Hub    │
                    │            └──────────┬──────┘
                    │                       │
                    └────────────┬──────────┘
                                 │
                      ┌──────────▼──────────┐
                      │ Step 4: Create      │
                      │ Container from Image│
                      └──────────┬──────────┘
                                 │
                      ┌──────────▼──────────┐
                      │ Container Running!  │
                      └─────────────────────┘
```

---

## Docker Image Layers

### How Docker Builds Images

```
Your Application
Dockerfile: FROM python:3.11-slim

              ┌───────────────────────┐
              │  Layer 5: My Code     │ (app.py, config)
              ├───────────────────────┤
              │  Layer 4: Entrypoint  │ (CMD)
              ├───────────────────────┤
              │  Layer 3: Dependencies│ (pip install)
              ├───────────────────────┤
              │  Layer 2: Metadata    │ (WORKDIR, ENV)
              ├───────────────────────┤
              │  Layer 1: Base OS     │ (python:3.11)
              └───────────────────────┘

Each layer is cached:
- If Layer 2 changes, Docker rebuilds from Layer 2 onward
- Unchanged layers are reused (fast rebuilds!)

GOOD ordering:          BAD ordering:
┌──────────────────┐   ┌──────────────────┐
│ FROM base        │   │ FROM base        │
│ RUN pip install  │ < │ COPY app.py      │ (changes often)
│ COPY app.py      │   │ RUN pip install  │
└──────────────────┘   └──────────────────┘
(dependencies cached)   (always rebuilds!)
```

---

## Container Lifecycle

### States & Transitions

```
                     docker run
                         │
                         ▼
            ┌────────────────────────┐
            │   CREATED              │
            │  (container exists,    │
            │   not running)         │
            └───────────┬────────────┘
                        │
                        ▼
            ┌────────────────────────┐
            │   RUNNING              │◄────────┐
            │  (executing)           │         │
            └────────┬───────────────┘         │
                     │                    docker restart
                     │
         ┌───────────┴──────────┐
         │                      │
    (Ctrl+C or                  │
     docker stop)               │
         │                      │
         ▼                      │
    ┌────────────┐          docker start
    │  EXITED    │◄──────────┘
    │ (stopped)  │
    └────────────┘
         │
    docker rm
         │
         ▼
    (removed)
```

### Docker Run Command Breakdown

```bash
docker run -d -p 5000:5000 -e DEBUG=1 --name my-app my-app:1.0

│       │  │  │              │           │           │
│       │  │  │              │           │           └─ Image name and tag
│       │  │  │              │           └─ Give container a name
│       │  │  │              └─ Environment variable
│       │  │  └─ Port mapping (host:container)
│       │  └─ Run in background (detached)
│       └─ Docker command
└─ Run subcommand
```

---

## Docker vs Virtual Machines

```
Virtual Machines          Docker Containers
═════════════════════════════════════════════

┌─────────────────────┐  ┌──────────────────┐
│ App 1               │  │ App 1            │
├─────────────────────┤  ├──────────────────┤
│ OS (Linux)          │  │ Libraries Only   │
├─────────────────────┤  ├──────────────────┤
│ Hypervisor          │  │ Docker Engine    │
├─────────────────────┤  ├──────────────────┤
│ Host OS             │  │ Host OS          │
└─────────────────────┘  └──────────────────┘

Size:  ~5-10GB           Size:  ~100-500MB
Boot:  30-60 seconds     Boot:  <1 second
Memory: 2-4GB per VM     Memory: 10-50MB per container


Why Docker is better for most use cases:
✅ Lightweight
✅ Fast startup
✅ Easy to scale
✅ Less overhead
✅ Better for microservices

Why VMs are still needed:
✅ Different OS kernels needed
✅ Full isolation required
✅ Legacy applications
```

---

## Docker Compose: Service Orchestration

### Multi-Container Application Architecture

```
Your Application
         │
         ▼
    ┌──────────────────────────────────┐
    │   docker-compose up              │
    └──────────┬───────────────────────┘
               │
       ┌───────┴────────┬────────────┬────────────┐
       │                │            │            │
    ┌──▼──┐          ┌──▼──┐     ┌──▼──┐      ┌──▼──┐
    │ API │          │ API │     │ API │      │ DB  │
    │ 5000│          │ 5000│     │ 5000│      │ 5432│
    └──┬──┘          └──┬──┘     └──┬──┘      └─────┘
       │                │           │
       │                │           │ (all on same
       └────────┬───────┴───────────┘  network)
                │
         docker network
         (todo-network)
                │
         Services talk via
         service names!
```

### Docker Compose Service Dependencies

```yaml
services:
  api:
    depends_on:
      - db          ◄─ Wait for db service to be CREATED
    
  db:
    healthcheck:   ◄─ But not for it to be READY
      test: ["CMD", "pg_isready"]
      
What happens:
1. docker-compose starts db first
2. docker-compose starts api
3. But db might not be ready yet!
4. Solution: Add healthcheck to db
5. api should retry connections
6. Or wait with shell script
```

---

## CI/CD Pipeline Flow

### Automated Workflow

```
Developer Code              GitHub Repository
    │                              │
    └──────────push───────────────►│
                                    │
                            ┌───────▼─────────┐
                            │  GitHub Actions │
                            │  Workflow Start │
                            └───────┬─────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
               ┌────▼────┐     ┌────▼────┐    ┌────▼────┐
               │ Job 1   │     │ Job 2   │    │ Job 3   │
               │ Build   │     │ Test    │    │ Scan    │
               └────┬────┘     └────┬────┘    └────┬────┘
                    │               │              │
                    └───────────────┼──────────────┘
                                    │
                            ┌───────▼─────────┐
                            │ All Pass?       │
                            └───────┬─────────┘
                                    │
                        ┌───────────┴───────────┐
                        │                       │
                    YES │                       │ NO
                        │                       │
                   ┌────▼────┐            ┌────▼────┐
                   │ Deploy   │            │ Reject  │
                   │ to Prod  │            │ + Alert │
                   └────┬────┘            └─────────┘
                        │
                   ┌────▼────┐
                   │ Success! │
                   └──────────┘
```

### GitHub Actions Workflow Structure

```yaml
name: CI Pipeline
                    │
on: [push]          │ ◄─ TRIGGERS
                    │
jobs:               │
  build:            │ ◄─ JOB 1
    runs-on: ubuntu │
    steps:          │
      - checkout    │ ◄─ STEP 1
      - build       │ ◄─ STEP 2
      - test        │ ◄─ STEP 3
                    │
  deploy:           │ ◄─ JOB 2 (depends on job 1)
    needs: build    │
    steps:          │
      - deploy      │ ◄─ STEP 1
      - notify      │ ◄─ STEP 2
```

---

## Image Registry

### How Images are Stored & Retrieved

```
Your Computer              Docker Hub Registry
                           (docker.io)
                           
┌─────────────────┐
│ Local Images:   │        ┌──────────────────┐
│                 │        │ Public Library   │
│ python:3.11     │◄──────►│ Images:          │
│ my-app:1.0      │ pull   │                  │
│                 │        │ python:3.11      │
└────────┬────────┘        │ node:18          │
         │                 │ nginx            │
         │ push            │ postgres         │
         │                 └──────────────────┘
         │
         ▼
  ┌──────────────────┐
  │ Your Account     │
  │ (if logged in)   │
  │                  │
  │ username/app:1.0 │
  └──────────────────┘

docker pull ═  Download from Hub to Local
docker push ═  Upload from Local to Hub
docker build ═ Create locally
```

---

## Debugging Guide: Visual Flowchart

```
┌──────────────────────┐
│ Docker Issue?        │
└──────────┬───────────┘
           │
    ┌──────▼──────┐
    │ Image or    │
    │ Container?  │
    └──┬──────┬───┘
       │      │
   IMAGE│     │CONTAINER
       │      │
   ┌───▼──┐  ┌▼──────┐
   │docker│  │docker │
   │images│  │ps     │ ◄─ List containers
   └──┬───┘  └┬──────┘
      │       │
   ┌──▼─┐  ┌──▼────┐
   │Not │  │Not    │
   │see?│  │running?
   └──┬─┘  └───┬────┘
      │        │
   ┌──▼────┐ ┌─▼─────┐
   │docker │ │docker │
   │build  │ │logs   │ ◄─ View output
   └───────┘ └───────┘

Common Issues:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Issue              Solution
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Port conflict      Use different port
Connection refused Container not ready
File not found     Check COPY path
Out of memory      Increase docker limits
Slow builds        Use .dockerignore
Large images       Use multi-stage builds
Permission denied  Run as non-root user
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Dockerfile Best Practices

### Comparison: Good vs Bad

```
❌ BAD DOCKERFILE              ✅ GOOD DOCKERFILE
───────────────────────────────────────────────────

FROM python:3.11              FROM python:3.11-slim
RUN apt-get update            (smaller base)
RUN apt-get install git       
RUN pip install flask         WORKDIR /app
COPY . .                       COPY requirements.txt .
RUN pip install -r \          RUN pip install \
    requirements.txt          -r requirements.txt
EXPOSE 5000                   COPY . .
CMD ["python", "app.py"]      EXPOSE 5000
                              USER appuser
Issues:                       CMD ["python", "app.py"]
- Large image (900MB)
- Runs as root                Benefits:
- Dependencies rebuild        - Small image (150MB)
  if code changes            - Non-root user
- No cache layering          - Better security
                              - Fast rebuilds
```

---

## GitHub Actions: Visual Workflow Execution

```
Developer pushes code
         │
         ▼
GitHub detects push
         │
         ▼
    triggers on: push
         │
         ▼
Job 1: build        ┌────────────────────┐
  step: checkout    │ Parallel if no     │
  step: setup       │ dependencies       │
  step: build       │                    │ Job 2: test
  step: test        │ Sequential if      │  step: setup
         │          │ needs: build       │  step: run tests
         ├─────────►│                    │
         │          │                    │
         ▼          └────────────────────┘
    All pass?
         │
    ┌────┴────┐
    │          │
   YES        NO
    │          │
 Deploy    Fail & Notify
    │          │
    ▼          ▼
   ✅         ❌
```

---

## Docker Networking

### How Containers Connect

```
Scenario 1: Single Container
┌───────────────────┐
│ Your Machine      │
│ localhost:5000    │
│      │            │
│      ▼            │
│  ┌────────────┐   │
│  │ Container  │   │
│  │ Port 5000  │   │
│  └────────────┘   │
└───────────────────┘

Access: http://localhost:5000


Scenario 2: Multiple Containers (default bridge)
┌──────────────────────────┐
│ Your Machine             │
│                          │
│ ┌─────────────────────┐  │
│ │ docker-network      │  │
│ │                     │  │
│ │ ┌────────┐          │  │
│ │ │ api    │          │  │
│ │ │ :5000  │          │  │
│ │ └────────┘          │  │
│ │      ↔              │  │
│ │ ┌────────┐          │  │
│ │ │ db     │          │  │
│ │ │ :5432  │          │  │
│ │ └────────┘          │  │
│ │                     │  │
│ └─────────────────────┘  │
│                          │
│ Internal DNS:            │
│ api → 172.18.0.2:5000    │
│ db → 172.18.0.3:5432     │
└──────────────────────────┘

Access from api to db:
  FROM: api
  TO:   postgresql://db:5432
        (not localhost!)
```

---

## Docker Compose Override

### Development vs Production

```
Base Configuration
(docker-compose.yml)
─────────────────────────────────────
services:
  api:
    image: my-api:latest
    environment:
      LOG_LEVEL: info
    restart: always


Development Override
(docker-compose.override.yml)
─────────────────────────────────────
services:
  api:
    build: .              ◄─ Build locally
    environment:
      LOG_LEVEL: debug    ◄─ More logging
    restart: no           ◄─ Manual restart
    volumes:
      - .:/app            ◄─ Live code reload


Result: Local development has extra features!
In production: Only base config is used
```

---

## Resource Limits

### Docker Container Resource Constraints

```
Without Limits            With Limits
───────────────────────────────────────

┌─────────────┐          ┌──────────────┐
│ Container 1 │ 50MB     │ Container 1  │ 256MB max
├─────────────┤          ├──────────────┤
│ Container 2 │ 60MB     │ Container 2  │ 256MB max
├─────────────┤          ├──────────────┤
│ Container 3 │ 100MB    │ Container 3  │ 256MB max
├─────────────┤          ├──────────────┤
│ OS/System   │ Varies   │ OS/System    │ Remaining
└─────────────┘          └──────────────┘

Can crash      Protected
              (container killed if exceeds limit)


Memory limits in docker run:
docker run -m 512m                # Max 512MB
docker run -m 512m --memory-swap 1g  # 512MB RAM + 512MB swap
docker run --cpus 0.5             # Max 50% of 1 CPU
```

---

## Production Deployment

### Typical Production Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    PRODUCTION                           │
│                                                         │
│  ┌────────────────────────────────────────┐             │
│  │ Load Balancer (nginx/HAProxy)          │             │
│  │ :80 & :443                             │             │
│  └───┬───────────────────────┬────────────┘             │
│      │                       │                          │
│  ┌───▼──┐               ┌────▼───┐                      │
│  │API-1 │               │API-2   │                      │
│  │:5000 │               │:5000   │                      │
│  └───┬──┘               └────┬───┘                      │
│      │                       │                          │
│      └───────────┬───────────┘                          │
│                  │                                      │
│          ┌───────▼────────┐                            │
│          │   Database     │                            │
│          │   (PostgreSQL) │                            │
│          │   Master       │                            │
│          └───────┬────────┘                            │
│                  │                                      │
│          ┌───────▼────────┐                            │
│          │   Database     │                            │
│          │   (PostgreSQL) │                            │
│          │   Replica      │                            │
│          └────────────────┘                            │
│                                                         │
│  ┌────────────────────────────────────────┐             │
│  │ Monitoring & Logging (ELK/Prometheus)  │             │
│  └────────────────────────────────────────┘             │
│                                                         │
└─────────────────────────────────────────────────────────┘

Key Features:
- Multiple app instances for redundancy
- Load balancer distributes traffic
- Database replication
- Monitoring & logging for ops
```

---

## Summary: Docker Ecosystem

```
┌──────────────────────────────────────────────────────────┐
│                   DOCKER ECOSYSTEM                       │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Development        Build            Runtime             │
│  ──────────────    ──────           ──────               │
│                                                          │
│  Codespaces        Dockerfile      docker run            │
│  VS Code           docker build     Docker Daemon        │
│  Docker Desktop    GitHub Actions   Container Registry   │
│                                                          │
│  ──────────────────────────────────────────────────────  │
│                                                          │
│  Orchestration      Deployment       Operations          │
│  ──────────────    ────────────      ──────────          │
│                                                          │
│  Docker Compose     CI/CD            Monitoring          │
│  Kubernetes         GitHub Actions   Prometheus          │
│  Docker Swarm       Webhooks         ELK Stack           │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## Quick Decision Tree

### Which Tool Should I Use?

```
Need to package      ┌─────────────┐
an application?      │  Docker     │ ✓
                     └─────────────┘


Need local dev       ┌──────────────────┐
environment?         │ Docker + Compose │ ✓
                     └──────────────────┘


Need to test many    ┌─────────────┐
containers?          │  Codespaces │ ✓
                     └─────────────┘


Need auto-testing    ┌─────────────────────┐
on code push?        │ GitHub Actions      │ ✓
                     └─────────────────────┘


Need to scale to     ┌─────────────┐
1000+ containers?    │ Kubernetes  │ ✓
                     └─────────────┘


Need simple 3-4      ┌─────────────────────┐
container app?       │ Docker Compose      │ ✓
                     └─────────────────────┘
```

---

**Print this guide for reference!** 📖
