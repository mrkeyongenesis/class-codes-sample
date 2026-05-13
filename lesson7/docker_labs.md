# 🐳 Docker & CI/CD Labs - Hands-On Exercises

## Lab Overview

These labs are designed to help you understand Docker and CI/CD through **hands-on practice**. Each lab builds on the previous one.

### Time Estimates
- **Lab 1:** 20 minutes
- **Lab 2:** 30 minutes
- **Lab 3:** 25 minutes
- **Lab 4:** 35 minutes
- **Lab 5 (Optional):** 45 minutes

**Total:** ~2.5 hours for complete mastery

---

## Lab 1: Your First Docker Container (20 min)

### Goal
Understand how Docker images and containers work by running a simple container.

### Prerequisites
- GitHub Codespaces open (or Docker installed locally)
- Terminal access

### Steps

#### Step 1.1: Verify Docker Installation
```bash
docker --version
docker run hello-world
```

**What happened?**
- Docker pulled `hello-world` image from Docker Hub
- Created a container from that image
- Ran the container
- Container printed a message and exited

#### Step 1.2: Run an Interactive Container
```bash
docker run -it python:3.11 python --version
```

**Questions to answer:**
1. What does the `-it` flag do?
2. How is this different from `hello-world`?

#### Step 1.3: Explore Inside a Container
```bash
docker run -it python:3.11 bash
```

Now you're inside a running container! Try these commands:

```bash
# Inside container
pwd                    # Where are you?
ls -la                 # What files exist?
python --version       # Check Python version
pip list               # What packages are installed?
touch /hello.txt       # Create a file
ls /hello.txt          # Verify it exists
exit                   # Leave the container
```

#### Step 1.4: Key Insight - Containers are Isolated
```bash
# Create a file INSIDE the container
docker run -it python:3.11 bash -c "touch /created-inside.txt && ls /"

# Try to access that file from your computer
ls /created-inside.txt
# → "No such file or directory"

# Why? The container's filesystem is isolated from your computer!
```

### 🎓 Learning Points

| Concept | What You Learned |
|---------|-----------------|
| **Image** | A template (like `python:3.11`) |
| **Container** | A running copy of that template |
| **Isolation** | Each container has its own filesystem |
| **Temporary** | Changes inside a container are lost when it exits |

### ✅ Success Criteria
- [ ] Ran `docker --version` successfully
- [ ] Ran `hello-world` container
- [ ] Created and exited an interactive bash session
- [ ] Understood that container filesystem is isolated

---

## Lab 2: Build Your First Docker Image (30 min)

### Goal
Create a Dockerfile, build an image, and run a container from it.

### Project: Simple Hello World Server

#### Step 2.1: Create Your Project Files

In your Codespaces (or local folder), create these files:

**`app.py`:**
```python
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        response = {
            "message": "Hello from Docker!",
            "timestamp": datetime.now().isoformat(),
            "path": self.path
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8000), MyHandler)
    print("Server started on http://0.0.0.0:8000")
    server.serve_forever()
```

**`Dockerfile`:**
```dockerfile
# Build instructions
FROM python:3.11-slim

WORKDIR /app

COPY app.py .

EXPOSE 8000

CMD ["python", "app.py"]
```

#### Step 2.2: Build the Image
```bash
docker build -t my-server:1.0 .
```

**What happened?**
- Docker read the `Dockerfile`
- Executed each instruction
- Created a new image called `my-server` with tag `1.0`

Verify the image was created:
```bash
docker images | grep my-server
```

#### Step 2.3: Run Your Container
```bash
docker run -p 8000:8000 my-server:1.0
```

**What's happening?**
- `-p 8000:8000`: Map port 8000 from container to your machine
- The server is running inside the container
- You can access it at http://localhost:8000

#### Step 2.4: Test Your Server

**In a new terminal:**
```bash
curl http://localhost:8000/
curl http://localhost:8000/test?name=docker
```

**Or in Codespaces:**
- Look for the port forwarding notification
- Click the port 8000 link
- Browser opens http://localhost:8000

#### Step 2.5: Stop the Container
```bash
# In the terminal running the container, press Ctrl+C
# OR in another terminal:
docker ps                          # Find container ID
docker stop <container-id>
```

#### Step 2.6: Run It Detached
```bash
# Run in background
docker run -d -p 8000:8000 --name my-server my-server:1.0

# Check status
docker ps

# View logs
docker logs my-server

# Stop it
docker stop my-server
```

### 📝 Dockerfile Breakdown

```dockerfile
FROM python:3.11-slim      # 1. Start with Python 3.11 (slim = smaller)
WORKDIR /app               # 2. Create /app directory inside container
COPY app.py .              # 3. Copy app.py from your computer into /app
EXPOSE 8000                # 4. Tell Docker the container listens on 8000
CMD ["python", "app.py"]   # 5. Default command when container starts
```

### 🎓 Learning Points

| Step | Docker Action | Real World Analogy |
|------|---------------|-------------------|
| FROM | Choose base OS | Buy a computer |
| WORKDIR | Create folder | Create workspace |
| COPY | Add files | Install software |
| EXPOSE | Declare port | Open a port |
| CMD | Start app | Turn on the computer |

### ✅ Success Criteria
- [ ] Created Dockerfile and app.py
- [ ] Built image with `docker build`
- [ ] Ran container with port mapping
- [ ] Accessed server via http://localhost:8000
- [ ] Viewed logs with `docker logs`

---

## Lab 3: Multi-File Application with Docker (25 min)

### Goal
Work with dependencies and create a realistic Python application.

### Project: Todo API

#### Step 3.1: Create the Application

**`requirements.txt`:**
```
Flask==2.3.3
Werkzeug==2.3.7
```

**`app.py`:**
```python
from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)

TODOS_FILE = '/tmp/todos.json'

def load_todos():
    if os.path.exists(TODOS_FILE):
        with open(TODOS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_todos(todos):
    with open(TODOS_FILE, 'w') as f:
        json.dump(todos, f)

@app.route('/todos', methods=['GET'])
def get_todos():
    return jsonify(load_todos())

@app.route('/todos', methods=['POST'])
def add_todo():
    todo = request.json
    todos = load_todos()
    todo['id'] = len(todos) + 1
    todos.append(todo)
    save_todos(todos)
    return jsonify(todo), 201

@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todos = load_todos()
    todos = [t for t in todos if t.get('id') != todo_id]
    save_todos(todos)
    return '', 204

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

**`Dockerfile`:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy and install dependencies first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

EXPOSE 5000

HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

CMD ["python", "app.py"]
```

#### Step 3.2: Build and Run
```bash
docker build -t todo-api:1.0 .
docker run -p 5000:5000 todo-api:1.0
```

#### Step 3.3: Test the API

**Create a todo:**
```bash
curl -X POST http://localhost:5000/todos \
  -H "Content-Type: application/json" \
  -d '{"title":"Learn Docker","description":"Complete all labs"}'
```

**Get all todos:**
```bash
curl http://localhost:5000/todos
```

**Delete a todo:**
```bash
curl -X DELETE http://localhost:5000/todos/1
```

**Health check:**
```bash
curl http://localhost:5000/health
```

### 📝 Key Concepts

**Why separate dependency installation?**
```dockerfile
# This layers your image efficiently:
# Layer 1: Base Python image
# Layer 2: Install dependencies (rarely changes)
# Layer 3: Copy code (changes frequently)

# If you change only app.py, Docker skips layers 1-2 (cached)
# This makes rebuilds much faster!
```

### 🎓 Why HEALTHCHECK?

The `HEALTHCHECK` instruction tells Docker how to verify the container is healthy:
- Runs every 10 seconds
- Makes an HTTP request to `/health`
- If fails 3 times, marks container as unhealthy

### ✅ Success Criteria
- [ ] Built image with dependencies
- [ ] Ran container and accessed API
- [ ] Created, read, and deleted todos via API
- [ ] Health check works

---

## Lab 4: Docker Compose - Multiple Containers (35 min)

### Goal
Run multiple containers together and understand how they communicate.

### Project: Todo App with Database

#### Step 4.1: Create docker-compose.yml

In a new folder called `lab4-compose`:

**`docker-compose.yml`:**
```yaml
version: '3.8'

services:
  # Backend API
  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=development
    depends_on:
      - db
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 10s
      timeout: 3s
      retries: 3

  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=todouser
      - POSTGRES_PASSWORD=todopass
      - POSTGRES_DB=todos
    volumes:
      - db-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U todouser"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Adminer (database UI - optional)
  adminer:
    image: adminer
    ports:
      - "8080:8080"
    depends_on:
      - db

volumes:
  db-data:
```

#### Step 4.2: Update the Python App for Database

**`requirements.txt`:**
```
Flask==2.3.3
psycopg2-binary==2.9.6
SQLAlchemy==2.0.19
python-dotenv==1.0.0
```

**`app.py` (updated for database):**
```python
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Database configuration
db_user = os.getenv('DB_USER', 'todouser')
db_pass = os.getenv('DB_PASS', 'todopass')
db_host = os.getenv('DB_HOST', 'db')
db_name = os.getenv('DB_NAME', 'todos')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_pass}@{db_host}/{db_name}'
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    done = db.Column(db.Boolean, default=False)

@app.route('/todos', methods=['GET'])
def get_todos():
    todos = Todo.query.all()
    return jsonify([{
        'id': t.id,
        'title': t.title,
        'description': t.description,
        'done': t.done
    } for t in todos])

@app.route('/todos', methods=['POST'])
def add_todo():
    data = request.json
    todo = Todo(title=data['title'], description=data.get('description', ''))
    db.session.add(todo)
    db.session.commit()
    return jsonify({'id': todo.id, **data}), 201

@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    db.session.delete(todo)
    db.session.commit()
    return '', 204

@app.route('/health')
def health():
    return {'status': 'healthy'}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
```

**`Dockerfile`:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5000

CMD ["python", "app.py"]
```

#### Step 4.3: Start All Services
```bash
# Build and start all containers
docker-compose up --build

# Run in background
docker-compose up -d --build
```

**What's running?**
- API on http://localhost:5000
- PostgreSQL on localhost:5432
- Adminer (DB UI) on http://localhost:8080

#### Step 4.4: Test Everything

**Wait for services to start (watch for "ready to accept connections"):**

```bash
# Test API health
curl http://localhost:5000/health

# Create a todo
curl -X POST http://localhost:5000/todos \
  -H "Content-Type: application/json" \
  -d '{"title":"Learn Docker Compose","description":"Multiple containers"}'

# Get todos
curl http://localhost:5000/todos

# View database in Adminer
# Open http://localhost:8080
# Server: db
# User: todouser
# Password: todopass
# Database: todos
```

#### Step 4.5: View Logs

```bash
# View all logs
docker-compose logs

# Follow specific service
docker-compose logs -f api

# Last 20 lines
docker-compose logs --tail=20
```

#### Step 4.6: Stop Everything
```bash
# Stop all containers
docker-compose down

# Stop and remove volumes (delete database)
docker-compose down -v
```

### 🎓 Key Concepts

**Service Communication:**
- Services communicate by name: `db`, `api`, etc.
- `api` connects to `db:5432` (not `localhost:5432`)
- Docker Compose creates a network automatically

**Volumes:**
- `db-data:/var/lib/postgresql/data` persists database between runs
- Remove with `docker-compose down -v`

**depends_on:**
- `api` waits for `db` to be defined
- Doesn't wait for DB to be *ready* (use healthcheck)

### ✅ Success Criteria
- [ ] Created docker-compose.yml
- [ ] Updated app to use PostgreSQL
- [ ] Started all services with `docker-compose up`
- [ ] Created and retrieved todos from the database
- [ ] Accessed Adminer and viewed database

---

## Lab 5: CI/CD Pipeline with GitHub Actions (45 min)

### Goal
Set up automated testing and deployment with GitHub Actions.

### Part 5.1: Push to GitHub

```bash
# Initialize git repo
git init
git add .
git commit -m "Initial commit: Docker Todo App"

# Create new repo on GitHub
# Then:
git remote add origin https://github.com/YOUR_USERNAME/todo-docker.git
git push -u origin main
```

### Part 5.2: Create GitHub Workflow

Create `.github/workflows/docker-ci.yml`:

```yaml
name: Docker Build & Test

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  build-and-test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_USER: todouser
          POSTGRES_PASSWORD: todopass
          POSTGRES_DB: todos
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4

      - name: Build Docker image
        run: docker build -t todo-app:${{ github.sha }} .

      - name: Test image builds
        run: docker run --rm todo-app:${{ github.sha }} python -c "import flask; print('Flask OK')"

      - name: Test Docker Compose
        run: |
          docker-compose -f docker-compose.yml config
          docker-compose up -d
          sleep 10
          curl -f http://localhost:5000/health || exit 1
          docker-compose logs
          docker-compose down

      - name: List images
        run: docker images | grep todo-app

  push-to-docker-hub:
    needs: build-and-test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v4

      - name: Login to Docker Hub
        run: echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin

      - name: Build and push
        run: |
          docker build -t ${{ secrets.DOCKER_USERNAME }}/todo-app:latest .
          docker push ${{ secrets.DOCKER_USERNAME }}/todo-app:latest

      - name: Logout from Docker Hub
        run: docker logout
```

### Part 5.3: Add Secrets

**In GitHub:**
1. Go to your repo → Settings
2. Click "Secrets and variables" → "Actions"
3. Click "New repository secret"
4. Add:
   - Name: `DOCKER_USERNAME`, Value: your Docker Hub username
   - Name: `DOCKER_PASSWORD`, Value: your Docker Hub access token

### Part 5.4: Trigger the Workflow

```bash
# Make a change and push
echo "# Lab 5 Complete" >> README.md
git add README.md
git commit -m "Update README"
git push origin main
```

**Watch it happen:**
1. Go to your GitHub repo
2. Click "Actions" tab
3. See your workflow running!
4. Click the workflow to see logs

### Part 5.5: Create a Pull Request Workflow

Create `.github/workflows/pull-request.yml`:

```yaml
name: PR Checks

on: pull_request

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build image
        run: docker build -t pr-check .
      - name: Lint Dockerfile
        run: docker run --rm -i hadolint/hadolint < Dockerfile || true
```

### 🎓 Key Concepts

**Triggers:**
- `on: push` - Run on any push
- `on: [push, pull_request]` - Run on push or PR
- `branches: [main]` - Only main branch

**Jobs:**
- Independent runners of steps
- Can depend on each other with `needs:`
- Run in parallel unless dependencies exist

**Secrets:**
- `${{ secrets.DOCKER_PASSWORD }}` safely accesses secrets
- Never printed in logs
- Only accessible to authorized workflows

### ✅ Success Criteria
- [ ] Created GitHub workflow file
- [ ] Added Docker Hub secrets
- [ ] Triggered workflow by pushing code
- [ ] Verified workflow ran successfully
- [ ] Saw image pushed to Docker Hub

---

## Lab 6 (Challenge): All Together

### Goal
Build a complete project from scratch using everything you've learned.

### Challenge: Create a Weather App

**Requirements:**
1. **Backend:** Python Flask API that:
   - Gets current weather (use OpenWeatherMap API)
   - Caches results in PostgreSQL
   - Provides REST endpoints

2. **Frontend:** Simple HTML page that:
   - Calls the backend API
   - Displays weather

3. **Containers:**
   - Backend container
   - Database container
   - Frontend container

4. **CI/CD:**
   - GitHub workflow that tests all containers
   - Pushes to Docker Hub on success

### 🎯 Bonus Challenges

1. **Add tests** - Include pytest tests and run them in CI
2. **Add database migrations** - Use Alembic for schema
3. **Add logging** - Structured logging with JSON output
4. **Add monitoring** - Prometheus metrics
5. **Deploy** - Deploy to AWS or Heroku from GitHub Actions

---

## 📚 Learning Resources

### Key Files to Review
- **Dockerfile** - Reread the official docs section
- **docker-compose.yml** - Understand each service
- **GitHub Actions** - Review workflow syntax

### Common Mistakes

| Mistake | Solution |
|---------|----------|
| "Port already in use" | Use different port: `-p 8001:5000` |
| "Connection refused" | Container might not be ready (use healthcheck) |
| "File not found" | Check COPY path in Dockerfile |
| "Permission denied" | Run app as non-root user |
| "Image too large" | Use multi-stage builds or slim base images |

### Debugging Commands
```bash
# See all layers of image build
docker build --progress=plain .

# Inspect running container
docker inspect <container-id>

# Execute command in running container
docker exec -it <container-id> bash

# View resource usage
docker stats

# Check networking
docker network inspect <network-name>
```

---

## 🏆 Final Summary

### What You've Learned
- ✅ Docker fundamentals (images, containers, registries)
- ✅ Writing Dockerfiles
- ✅ Running containers
- ✅ Docker Compose for multi-container apps
- ✅ GitHub Actions workflows
- ✅ CI/CD pipelines
- ✅ Deploying code automatically

### Why This Matters
- **Consistency** - Apps run the same everywhere
- **Collaboration** - Share exact environments
- **Automation** - Reduce manual errors
- **Scalability** - Easy to deploy multiple instances
- **Industry Standard** - Used by most tech companies

### Next Steps
1. **Experiment** - Modify the projects
2. **Deploy** - Deploy to AWS, Azure, or Google Cloud
3. **Learn** - Explore Kubernetes for orchestration
4. **Build** - Create your own projects

---

**Congratulations on completing the labs! 🎉**

You now understand containerization and CI/CD pipelines.
Start building and shipping containerized applications!
