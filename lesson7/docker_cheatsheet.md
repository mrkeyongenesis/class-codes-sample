# Docker & CI/CD Quick Reference Cheat Sheet

## 🐳 Docker Essentials

### Understanding Core Concepts

| Concept | What It Is | Example |
|---------|-----------|---------|
| **Dockerfile** | Recipe for building an image | `FROM python:3.11` |
| **Image** | Blueprint/template (read-only) | `python:3.11-slim` |
| **Container** | Running instance of image | `docker run python:3.11` |
| **Registry** | Storage for images | Docker Hub |

---

## 📝 Dockerfile Template

```dockerfile
# Choose base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy files
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 5000

# Health check (optional)
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:5000/health || exit 1

# Run application
CMD ["python", "app.py"]
```

---

## 🔨 Essential Docker Commands

### Building Images
```bash
# Build image from Dockerfile
docker build -t my-app:1.0 .
docker build -t username/my-app:latest -f Dockerfile.prod .
docker build --build-arg ENV=production -t my-app .

# Build without cache
docker build --no-cache -t my-app .
```

### Running Containers
```bash
# Basic run
docker run my-app:1.0

# With port mapping
docker run -p 5000:5000 my-app:1.0

# With port mapping (specific interface)
docker run -p 127.0.0.1:5000:5000 my-app:1.0

# Detached mode (background)
docker run -d -p 5000:5000 --name my-app my-app:1.0

# With environment variables
docker run -e DATABASE_URL=postgres://... my-app

# With volume mount
docker run -v /local/path:/app/data my-app

# With interactive terminal
docker run -it my-app:1.0 /bin/bash

# With resource limits
docker run -m 512m --cpus=1 my-app

# Remove container after run
docker run --rm my-app:1.0
```

### Managing Containers
```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# View container logs
docker logs container-id
docker logs -f container-id      # Follow logs
docker logs --tail=50 container-id

# Stop container
docker stop container-id

# Start stopped container
docker start container-id

# Remove container
docker rm container-id

# Force remove running container
docker rm -f container-id

# Execute command in running container
docker exec container-id ls
docker exec -it container-id bash

# Inspect container details
docker inspect container-id

# View container resource usage
docker stats container-id
```

### Managing Images
```bash
# List images
docker images

# Search images on Docker Hub
docker search python

# Remove image
docker rmi image-id

# Remove unused images
docker image prune

# Tag image for registry
docker tag my-app:1.0 username/my-app:latest

# Push to registry
docker push username/my-app:latest

# Pull from registry
docker pull username/my-app:latest

# Save image to tar file
docker save my-app:1.0 > my-app.tar

# Load image from tar file
docker load < my-app.tar
```

### Cleanup
```bash
# Remove stopped containers
docker container prune

# Remove dangling images
docker image prune

# Remove everything (BE CAREFUL!)
docker system prune --all
```

---

## 🐳 Docker Compose

### Basic docker-compose.yml
```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/todos
    volumes:
      - ./backend:/app
    depends_on:
      - db
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=todos
    volumes:
      - db-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  db-data:

networks:
  default:
    name: todo-network
```

### Docker Compose Commands
```bash
# Build and start containers
docker-compose up --build

# Start in background
docker-compose up -d

# Stop containers
docker-compose down

# View logs
docker-compose logs
docker-compose logs -f backend

# View running services
docker-compose ps

# Execute command in service
docker-compose exec backend bash

# Rebuild images
docker-compose build

# Remove volumes on down
docker-compose down -v

# Scale service
docker-compose up -d --scale backend=3
```

---

## 🔄 GitHub Actions Workflows

### Basic Workflow Structure
```yaml
name: CI Pipeline

# Trigger
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

# Environment variables
env:
  REGISTRY: docker.io
  IMAGE_NAME: my-app

# Jobs
jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Step name
        run: command-here
      
      - name: Use output from previous step
        run: echo ${{ steps.step-id.outputs.output-name }}
```

### Common Workflow Actions

**Checkout code:**
```yaml
- uses: actions/checkout@v4
```

**Setup Docker Buildx:**
```yaml
- uses: docker/setup-buildx-action@v2
```

**Build and push image:**
```yaml
- name: Build and push
  run: |
    docker build -t ${{ secrets.DOCKER_USERNAME }}/app:latest .
    docker push ${{ secrets.DOCKER_USERNAME }}/app:latest
```

**Using secrets:**
```yaml
- name: Login to Docker Hub
  run: echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
```

**Upload artifacts:**
```yaml
- name: Upload test results
  uses: actions/upload-artifact@v3
  with:
    name: test-results
    path: test-results.xml
```

**Set up Node.js:**
```yaml
- uses: actions/setup-node@v3
  with:
    node-version: '18'
    cache: 'npm'
```

**Set up Python:**
```yaml
- uses: actions/setup-python@v4
  with:
    python-version: '3.11'
    cache: 'pip'
```

---

## 📋 Complete CI/CD Workflow Example

```yaml
name: Build, Test, and Deploy

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: docker.io
  IMAGE_NAME: ${{ secrets.DOCKER_USERNAME }}/my-app

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Build Docker image
        run: docker build -t ${{ env.IMAGE_NAME }}:${{ github.sha }} .
      
      - name: Test image
        run: docker run --rm ${{ env.IMAGE_NAME }}:${{ github.sha }} pytest tests/
  
  push:
    needs: build
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Login to Docker Hub
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | \
          docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
      
      - name: Build and push
        run: |
          docker build -t ${{ env.IMAGE_NAME }}:latest .
          docker push ${{ env.IMAGE_NAME }}:latest
      
      - name: Tag as release
        run: |
          docker tag ${{ env.IMAGE_NAME }}:latest \
                      ${{ env.IMAGE_NAME }}:v1.${{ github.run_number }}
          docker push ${{ env.IMAGE_NAME }}:v1.${{ github.run_number }}
```

---

## 🚀 GitHub Codespaces Essentials

### devcontainer.json Template
```json
{
  "name": "My Development Environment",
  
  "image": "mcr.microsoft.com/devcontainers/python:3.11",
  
  "features": {
    "ghcr.io/devcontainers/features/docker-in-docker:2": {},
    "ghcr.io/devcontainers/features/node:18": {}
  },
  
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-docker.docker",
        "ms-python.python",
        "ms-vscode.makefile-tools"
      ],
      "settings": {
        "python.linting.enabled": true,
        "python.formatting.provider": "black"
      }
    }
  },
  
  "postCreateCommand": "pip install -r requirements.txt",
  
  "forwardPorts": [5000, 3000, 8000],
  
  "portsAttributes": {
    "5000": {
      "label": "Application",
      "onAutoForward": "notify"
    }
  }
}
```

### Codespaces CLI
```bash
# List codespaces
gh codespace list

# Create codespace
gh codespace create -r owner/repo

# Delete codespace
gh codespace delete -c codespace-name

# SSH into codespace
gh codespace ssh -c codespace-name
```

---

## 🔐 Setting Up GitHub Secrets

**From GitHub UI:**
1. Repo → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `DOCKER_USERNAME`, Value: your Docker Hub username
4. Click "Add secret"

**From GitHub CLI:**
```bash
gh secret set DOCKER_USERNAME --body "your-username"
gh secret set DOCKER_PASSWORD --body "your-token"
gh secret list
gh secret delete DOCKER_PASSWORD
```

---

## 📊 Docker Best Practices

### Dockerfile Best Practices
```dockerfile
# ✅ DO: Use specific base image versions
FROM python:3.11-slim

# ✅ DO: Use .dockerignore to exclude files
# .dockerignore: __pycache__, .git, venv, node_modules

# ✅ DO: Combine RUN commands to reduce layers
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ✅ DO: Use multi-stage builds to reduce size
FROM node:18 AS builder
WORKDIR /app
COPY . .
RUN npm install && npm run build

FROM node:18-slim
COPY --from=builder /app/dist .

# ❌ DON'T: Run as root
# ✅ DO: Create non-root user
RUN useradd -m appuser
USER appuser

# ❌ DON'T: Put secrets in Dockerfile
# ✅ DO: Use build args or environment at runtime
```

### Image Size Tips
```bash
# Use slim versions
FROM python:3.11-slim  # 150MB
FROM python:3.11       # 900MB

# Multi-stage builds
# 10x size reduction typical

# Remove package managers in production
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
```

### Security Best Practices
```bash
# Scan for vulnerabilities
docker scan my-app:1.0

# Use non-root user in Dockerfile
RUN useradd -m appuser
USER appuser

# Don't use 'latest' tag in production
docker run my-app:v1.2.3  # ✅ Good
docker run my-app:latest  # ❌ Bad

# Scan with Trivy
trivy image my-app:1.0
```

---

## 🐛 Troubleshooting

### Container won't start
```bash
# Check logs
docker logs container-id

# Run with more verbosity
docker run -it my-app bash

# Inspect image
docker inspect my-app:1.0
```

### Port already in use
```bash
# Use different port
docker run -p 8000:5000 my-app

# Find what's using port
lsof -i :5000

# Kill process
kill -9 PID
```

### Docker daemon issues
```bash
# Check Docker status
systemctl status docker

# Restart Docker
systemctl restart docker

# In Codespaces, rebuild
# Settings → Codespaces → Rebuild
```

### Disk space
```bash
# Check disk usage
docker system df

# Clean up
docker system prune --all -f
```

---

## 🎯 Quick Start Checklist

### First Time Setup
- [ ] Install Docker (or use Codespaces)
- [ ] Create Dockerfile
- [ ] Build image: `docker build -t my-app .`
- [ ] Run: `docker run -p 5000:5000 my-app`
- [ ] Test in browser: `localhost:5000`

### Add to GitHub
- [ ] Create GitHub repo
- [ ] Push code: `git push`
- [ ] Create `.github/workflows/docker-ci.yml`
- [ ] Add secrets (DOCKER_USERNAME, DOCKER_PASSWORD)
- [ ] Push workflow
- [ ] Check Actions tab

### Using Codespaces
- [ ] Create `.devcontainer/devcontainer.json`
- [ ] Open Codespaces
- [ ] Run: `docker build -t my-app .`
- [ ] Run: `docker run -p 5000:5000 my-app`
- [ ] Access via forwarded port

---

## 📚 Additional Resources

**Official Docs:**
- Docker: https://docs.docker.com
- GitHub Actions: https://docs.github.com/en/actions
- Codespaces: https://github.com/features/codespaces

**Learning:**
- Docker Get Started: https://docs.docker.com/get-started
- GitHub Skills: https://skills.github.com
- Learn Docker: https://docker.com/resources/what-docker

**Tools:**
- Docker Hub: https://hub.docker.com
- GitHub CLI: https://cli.github.com
- Docker Scout: https://docs.docker.com/scout

---

**Last Updated:** 2024
**Print this page for quick reference!** 📖
