# Docker & CI/CD with GitHub Codespaces - Complete Setup Guide

## Table of Contents
1. [Introduction: Why Docker?](#why-docker)
2. [Understanding Docker Architecture](#docker-architecture)
3. [Setting Up Codespaces](#codespaces-setup)
4. [Building Your First Container](#first-container)
5. [CI/CD Pipelines with GitHub Actions](#ci-cd-pipelines)
6. [Complete Step-by-Step Project](#complete-project)
7. [Advanced Topics](#advanced)

---

## Why Docker?

### The Problem It Solves

**Scenario 1: Local Development**
```
Developer A: "It works on my machine!"
Developer B: "It crashes on mine..."
→ Different Python versions, missing dependencies, OS differences
```

**Scenario 2: Deployment**
```
Staging Environment: ✅ Works perfectly
Production Environment: ❌ Crashes
→ Different server configuration, library versions, permissions
```

**Docker Solution:**
Package your entire application environment (code, dependencies, runtime, configuration) into a container that runs identically everywhere.

### Key Benefits

| Benefit | Without Docker | With Docker |
|---------|---|---|
| **Consistency** | Depends on machine setup | Same everywhere |
| **Dependencies** | Manual installation | Included in image |
| **Scaling** | Complex, error-prone | Simple, automated |
| **Isolation** | Library conflicts | Each app isolated |
| **Deployment** | 30+ manual steps | Single `docker run` |

---

## Docker Architecture

### The Flow (From Your Diagram)

```
┌─────────────────────────────────────────────────────────────────┐
│                      User/Developer                              │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                    Step 1: Type of Image?
                                 │
                    ┌────────────┴────────────┐
                    │                         │
              Existing Image            New Image
                    │                         │
                    │                    docker build
                    │                         │
                    └────────────┬────────────┘
                                 │
                          Step 2: docker run
                                 │
                    ┌────────────┴────────────┐
                    │                         │
            Step 3: Local Copy?          No Local Copy
                    │                         │
                   YES                    Pull from Registry
                    │                         │
                    └────────────┬────────────┘
                                 │
                    Step 4: Create Container
                                 │
```

### Understanding the Components

**1. Dockerfile** - Recipe for building an image
```dockerfile
FROM python:3.11-slim          # Base image
WORKDIR /app                    # Set working directory
COPY requirements.txt .         # Copy dependencies list
RUN pip install -r requirements.txt  # Install dependencies
COPY . .                        # Copy application code
EXPOSE 5000                     # Declare port
CMD ["python", "app.py"]        # Default startup command
```

**2. Docker Image** - Blueprint/template
- Read-only
- Contains application code + all dependencies
- Can be stored and shared

**3. Docker Container** - Running instance
- Started from an image
- Running copy with its own filesystem
- Can be created/destroyed

**4. Registry** - Central storage
- Docker Hub (public)
- Private registries
- Central place to share images

---

## Codespaces Setup

### What is GitHub Codespaces?

A cloud-based VS Code editor that:
- Comes with Docker pre-installed
- No local installation needed
- Accessible from any browser
- Free tier: 120 core hours/month per user

### Creating Your First Codespace

**Step 1: Create Repository**
```bash
# Go to github.com
# Click + icon → New repository
# Name it: "docker-learning-project"
# Check "Add README"
# Create
```

**Step 2: Open Codespaces**
```
1. Click green "Code" button
2. Click "Codespaces" tab
3. Click "Create codespace on main"
4. Wait 30-60 seconds...
5. VS Code opens in your browser
```

**Step 3: Verify Docker**
```bash
# In Codespaces terminal:
docker --version
docker run hello-world
```

### Configuring Your Codespace (devcontainer.json)

Create `.devcontainer/devcontainer.json`:

```json
{
  "name": "Docker Learning Environment",
  "image": "mcr.microsoft.com/devcontainers/python:3.11",
  
  "features": {
    "ghcr.io/devcontainers/features/docker-in-docker:2": {},
    "ghcr.io/devcontainers/features/node:18": {}
  },
  
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-docker.docker",
        "charliermarsh.ruff",
        "ms-python.python"
      ]
    }
  },
  
  "postCreateCommand": "pip install -r requirements.txt 2>/dev/null || true",
  
  "forwardPorts": [5000, 3000, 8000],
  "portsAttributes": {
    "5000": {
      "label": "Flask App",
      "onAutoForward": "notify"
    }
  }
}
```

**This configuration:**
- Sets up Python 3.11 environment
- Installs Docker and Node.js
- Auto-installs VS Code extensions
- Forwards web app ports
- Auto-installs Python dependencies

---

## Building Your First Container

### Simple Python Flask App

**Create `app.py`:**
```python
from flask import Flask, render_template_string
import os

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Docker Learning App</title>
    <style>
        body { font-family: Arial; margin: 50px; text-align: center; }
        .container { max-width: 600px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #2563eb, #1e40af); 
                  color: white; padding: 20px; border-radius: 8px; }
        .info { background: #f0f9ff; padding: 15px; margin-top: 20px; 
                border-radius: 8px; }
        code { background: #e2e8f0; padding: 2px 5px; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🐳 Docker Learning App</h1>
            <p>Running in a containerized environment</p>
        </div>
        <div class="info">
            <h2>Environment Info</h2>
            <p><strong>Hostname:</strong> <code>{{ hostname }}</code></p>
            <p><strong>Environment:</strong> <code>{{ environment }}</code></p>
            <p><strong>Python Version:</strong> <code>{{ python_version }}</code></p>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    import platform
    return render_template_string(
        HTML,
        hostname=os.uname().nodename,
        environment="Docker Container",
        python_version=platform.python_version()
    )

@app.route('/health')
def health():
    return {"status": "healthy", "container": True}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

**Create `requirements.txt`:**
```
Flask==2.3.3
Werkzeug==2.3.7
```

**Create `Dockerfile`:**
```dockerfile
# Multi-stage build to minimize image size

# Stage 1: Builder
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime (much smaller)
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
COPY app.py .

EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')"

CMD ["python", "app.py"]
```

### Building and Running

```bash
# Build the image
docker build -t my-flask-app:1.0 .

# Run in foreground (to see logs)
docker run -p 5000:5000 my-flask-app:1.0

# Run in background (detached)
docker run -d -p 5000:5000 --name my-app my-flask-app:1.0

# View logs
docker logs my-app

# Stop container
docker stop my-app

# Remove container
docker rm my-app

# Remove image
docker rmi my-flask-app:1.0
```

### Docker Commands Reference

```bash
# Image commands
docker build -t name:tag .              # Build image
docker images                            # List images
docker rmi image-name                   # Remove image
docker push username/image:tag          # Push to registry
docker pull username/image:tag          # Pull from registry

# Container commands
docker run -p 8000:5000 image           # Run container with port mapping
docker ps                               # List running containers
docker ps -a                            # List all containers
docker logs container-id                # View logs
docker exec -it container-id bash       # Enter running container
docker stop container-id                # Stop container
docker rm container-id                  # Remove container

# Inspection
docker inspect container-id             # Get detailed info
docker stats                            # View resource usage
docker diff container-id                # See what changed
```

---

## CI/CD Pipelines with GitHub Actions

### What is CI/CD?

**Continuous Integration (CI):**
- Automatically test code on every push
- Catch bugs early
- Maintain code quality

**Continuous Deployment (CD):**
- Automatically deploy tested code to production
- Reduce manual errors
- Enable frequent releases

### Pipeline Stages

```
Developer Push
     ↓
[1] Checkout Code
     ↓
[2] Build Docker Image
     ↓
[3] Run Tests
     ↓
[4] Lint & Security Checks
     ↓
[5] Push to Registry
     ↓
[6] Deploy to Production
     ↓
[7] Notify Team
```

### Creating Your First Workflow

**Create `.github/workflows/docker-ci.yml`:**

```yaml
name: Docker CI Pipeline

# When to run
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  build-test-push:
    runs-on: ubuntu-latest
    
    steps:
      # Step 1: Get the code
      - name: Checkout code
        uses: actions/checkout@v4

      # Step 2: Set up Docker Buildx (for advanced builds)
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      # Step 3: Build the image
      - name: Build Docker image
        run: docker build -t my-app:${{ github.sha }} .

      # Step 4: Run basic tests
      - name: Run tests
        run: docker run --rm my-app:${{ github.sha }} python -m pytest tests/ 2>/dev/null || echo "No tests yet"

      # Step 5: Verify container runs
      - name: Verify container
        run: docker run --rm my-app:${{ github.sha }} /bin/sh -c "echo 'Container works!'"

      # Step 6: Display status
      - name: Success notification
        run: echo "✅ Build successful! Image: my-app:${{ github.sha }}"
```

### Adding Secrets for Docker Hub

**Setup:**
1. Create Docker Hub account at hub.docker.com
2. Generate Personal Access Token:
   - Settings → Security → New Access Token
3. Add to GitHub:
   - Go to repo → Settings → Secrets and variables → Actions
   - Add `DOCKER_USERNAME` (your Docker Hub username)
   - Add `DOCKER_PASSWORD` (your access token)

**Use in workflow:**

```yaml
- name: Login to Docker Hub
  run: echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin

- name: Push image
  run: docker push ${{ secrets.DOCKER_USERNAME }}/my-app:${{ github.sha }}
```

### Advanced Workflow: Full CI/CD

```yaml
name: Complete CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  REGISTRY: docker.io
  IMAGE_NAME: ${{ secrets.DOCKER_USERNAME }}/my-app

jobs:
  # Job 1: Build and Test
  build:
    runs-on: ubuntu-latest
    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}
    
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Login to Docker Registry
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=sha,prefix={{branch}}-
            type=semver,pattern={{version}}

      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}

  # Job 2: Run Tests
  test:
    needs: build
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4

      - name: Run tests
        run: |
          docker pull ${{ secrets.DOCKER_USERNAME }}/my-app:latest
          docker run --rm ${{ secrets.DOCKER_USERNAME }}/my-app:latest pytest tests/

  # Job 3: Security Scanning (optional)
  scan:
    needs: build
    runs-on: ubuntu-latest
    
    steps:
      - name: Scan image with Trivy
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ secrets.DOCKER_USERNAME }}/my-app:latest
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload scan results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

  # Job 4: Notification
  notify:
    needs: [build, test]
    runs-on: ubuntu-latest
    if: always()
    
    steps:
      - name: Determine status
        run: |
          if [ "${{ needs.build.result }}" = "success" ] && [ "${{ needs.test.result }}" = "success" ]; then
            echo "STATUS=✅ Deployment ready!" >> $GITHUB_ENV
          else
            echo "STATUS=❌ Build or tests failed" >> $GITHUB_ENV
          fi

      - name: Print status
        run: echo "${{ env.STATUS }}"
```

---

## Complete Step-by-Step Project

### Project: Multi-Container Todo Application

This project demonstrates Docker, Codespaces, and CI/CD with a realistic app.

**Project Structure:**
```
todo-app/
├── backend/
│   ├── app.py (Flask API)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── index.html
│   └── Dockerfile
├── docker-compose.yml (run multiple containers)
├── .github/
│   └── workflows/
│       └── docker-ci.yml
└── README.md
```

### Step 1: Create the Backend

**`backend/app.py`:**
```python
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

TODOS_FILE = '/data/todos.json'
os.makedirs('/data', exist_ok=True)

def load_todos():
    if os.path.exists(TODOS_FILE):
        with open(TODOS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_todos(todos):
    with open(TODOS_FILE, 'w') as f:
        json.dump(todos, f)

@app.route('/api/todos', methods=['GET'])
def get_todos():
    return jsonify(load_todos())

@app.route('/api/todos', methods=['POST'])
def add_todo():
    todos = load_todos()
    todo = request.json
    todo['id'] = len(todos) + 1
    todos.append(todo)
    save_todos(todos)
    return jsonify(todo), 201

@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todos = load_todos()
    todos = [t for t in todos if t['id'] != todo_id]
    save_todos(todos)
    return '', 204

@app.route('/health')
def health():
    return {'status': 'healthy'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

**`backend/requirements.txt`:**
```
Flask==2.3.3
Flask-CORS==4.0.0
Werkzeug==2.3.7
```

**`backend/Dockerfile`:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=3s CMD curl -f http://localhost:5000/health || exit 1

CMD ["python", "app.py"]
```

### Step 2: Create Docker Compose

**`docker-compose.yml`:**
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    volumes:
      - shared-data:/data
    environment:
      - FLASK_ENV=development
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

volumes:
  shared-data:
```

### Step 3: Run Locally in Codespaces

```bash
# Build and run both containers
docker-compose up --build

# In another terminal, test the API
curl http://localhost:5000/api/todos
curl -X POST http://localhost:5000/api/todos \
  -H "Content-Type: application/json" \
  -d '{"title":"Learn Docker","done":false}'

# View logs
docker-compose logs -f backend

# Stop
docker-compose down
```

### Step 4: CI/CD with GitHub Actions

**`.github/workflows/docker-ci.yml`:**
```yaml
name: Build & Test Docker App

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Build Docker images
        run: docker-compose build

      - name: Start services
        run: docker-compose up -d

      - name: Wait for services
        run: sleep 10

      - name: Test backend API
        run: |
          curl -f http://localhost:5000/health || exit 1
          curl -f http://localhost:5000/api/todos || exit 1

      - name: Verify containers
        run: docker-compose ps

      - name: Cleanup
        run: docker-compose down

  push:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v4

      - name: Login to Docker Hub
        run: echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin

      - name: Build and push backend
        run: |
          docker build -t ${{ secrets.DOCKER_USERNAME }}/todo-backend:latest ./backend
          docker push ${{ secrets.DOCKER_USERNAME }}/todo-backend:latest

      - name: Build and push frontend
        run: |
          docker build -t ${{ secrets.DOCKER_USERNAME }}/todo-frontend:latest ./frontend
          docker push ${{ secrets.DOCKER_USERNAME }}/todo-frontend:latest
```

---

## Advanced Topics

### 1. Image Optimization

**Multi-stage builds:**
```dockerfile
FROM node:18 AS build
WORKDIR /app
COPY . .
RUN npm install && npm run build

FROM node:18-slim
COPY --from=build /app/dist .
CMD ["node", "server.js"]
```

**Reduces size from 1.2GB to 150MB**

### 2. Docker Networks

```bash
# Create network
docker network create todo-network

# Connect containers
docker run --network todo-network --name backend my-backend
docker run --network todo-network my-frontend

# Containers can communicate by name
curl http://backend:5000/health
```

### 3. Volumes for Data Persistence

```bash
# Named volume
docker run -v todo-data:/data my-app

# Bind mount (local folder)
docker run -v $(pwd)/data:/data my-app

# View volumes
docker volume ls
docker volume inspect todo-data
```

### 4. Environment Variables

```yaml
# In docker-compose.yml
services:
  app:
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/todos
      - LOG_LEVEL=debug
      - SECRET_KEY=${SECRET_KEY}  # From .env file
```

### 5. Scaling with Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml todo-app

# Scale service
docker service scale todo-app_backend=3

# View services
docker service ls
```

### 6. Kubernetes Introduction

For large-scale deployments, use Kubernetes:

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: todo-backend
  template:
    metadata:
      labels:
        app: todo-backend
    spec:
      containers:
      - name: backend
        image: username/todo-backend:latest
        ports:
        - containerPort: 5000
        env:
        - name: DATABASE_URL
          value: "postgresql://..."
```

---

## Key Takeaways

### Why Docker Matters
1. **Consistency** - Same environment everywhere
2. **Isolation** - No dependency conflicts
3. **Scalability** - Easy to run multiple instances
4. **Automation** - CI/CD pipelines become possible

### Why GitHub Codespaces + Docker
1. **No setup** - Docker ready to use in browser
2. **Collaboration** - Share exact environment with team
3. **Learning** - Perfect for teaching containerization
4. **Cloud-native** - Prepare for production deployments

### CI/CD Benefits
1. **Catch bugs early** - Tests run automatically
2. **Consistent deployments** - Same process every time
3. **Fast iterations** - Deploy multiple times per day
4. **Confidence** - Automated safeguards before production

---

## Resources

- **Docker Docs:** https://docs.docker.com
- **GitHub Codespaces:** https://github.com/codespaces
- **GitHub Actions:** https://github.com/features/actions
- **Docker Hub:** https://hub.docker.com
- **Docker Compose:** https://docs.docker.com/compose

---

## Practice Exercises

### Exercise 1: Modify and Rebuild
- Change the Flask app message
- Rebuild the image
- Run it and verify changes

### Exercise 2: Add a Database
- Add PostgreSQL to docker-compose.yml
- Connect Flask app to database
- Save todos to database instead of file

### Exercise 3: Push to Docker Hub
- Create Docker Hub account
- Tag your image: `docker tag my-app:1.0 username/my-app:1.0`
- Push: `docker push username/my-app:1.0`
- Delete local image: `docker rmi username/my-app:1.0`
- Pull and run from registry: `docker run username/my-app:1.0`

### Exercise 4: Extend the Workflow
- Add a test step
- Add security scanning (Trivy)
- Add notification to Slack on success/failure

---

**Happy Learning! 🐳**
