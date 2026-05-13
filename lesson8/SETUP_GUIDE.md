# 🚀 Complete CI/CD Pipeline with Jenkins & GitHub - Quick Start Guide

## Project Overview

```
Your Application
    ↓
GitHub Repository
    ↓
GitHub Actions (Automated Testing)
    ↓
Jenkins (Manual/Automated Deployment)
    ↓
Docker Container
    ↓
Running Application (Accessible in Browser)
```

---

## 📋 What's Included

- ✅ **Flask Application** - Simple web app with database
- ✅ **Docker Setup** - Containerized with PostgreSQL
- ✅ **Jenkins** - CI/CD server running in Docker
- ✅ **GitHub Actions** - Automated testing and deployment
- ✅ **Docker Compose** - Multi-container orchestration
- ✅ **Tests** - Unit tests with pytest
- ✅ **Complete Pipeline** - From code to running app

---

## 🎯 Quick Start (5 minutes)

### Step 1: Open GitHub Codespaces

```bash
# In GitHub, click Code → Codespaces → Create codespace on main
# Wait for VS Code to load in browser
```

### Step 2: Start Everything

```bash
# In Codespaces terminal:
docker-compose up --build

# Wait for all services to start:
# - Jenkins: http://localhost:8080
# - Flask App: http://localhost:5000
# - PostgreSQL: localhost:5432
```

### Step 3: Access the Applications

**Flask App (The Application You Built):**
- Open browser: `http://localhost:5000`
- You'll see the web interface
- Try sending a message (saved to PostgreSQL)

**Jenkins (CI/CD Server):**
- Open browser: `http://localhost:8080`
- First time: Unlock Jenkins and set up
- Create a new Pipeline job

---

## 📁 Project Structure

```
.
├── app.py                          # Flask application
├── test_app.py                     # Unit tests
├── Dockerfile                      # Container config
├── docker-compose.yml              # Multi-container setup
├── requirements.txt                # Python dependencies
├── Jenkinsfile                     # Jenkins pipeline definition
├── .github/
│   └── workflows/
│       └── cicd.yml               # GitHub Actions workflow
└── README.md                       # This file
```

---

## 🐳 Docker Compose: What Gets Started

```yaml
Services:
├── jenkins (Port 8080)    - CI/CD server
├── app (Port 5000)        - Flask application
├── db (Port 5432)         - PostgreSQL database
└── All on same network for communication
```

### Start Services

```bash
# Build and start all
docker-compose up --build

# Run in background
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop everything
docker-compose down

# Stop and remove data
docker-compose down -v
```

---

## 🔧 Configuration & Setup

### Jenkins Initial Setup (First Time Only)

**1. Get Initial Password:**
```bash
# In another terminal (while docker-compose is running):
docker exec jenkins-server cat /var/jenkins_home/secrets/initialAdminPassword
```

**2. Open Jenkins:**
- Go to http://localhost:8080
- Paste the password
- Click "Continue"

**3. Install Suggested Plugins:**
- Click "Install suggested plugins"
- Wait 5-10 minutes

**4. Create Admin User:**
- Username: `admin`
- Password: `admin123`
- Click "Save and Continue"

**5. Jenkins URL:**
- Keep default: `http://localhost:8080`
- Click "Save and Finish"

### Create Jenkins Pipeline Job

**1. New Item:**
- Click "New Item"
- Name: `cicd-demo-app`
- Select: "Pipeline"
- Click OK

**2. Configure Pipeline:**
- Scroll to "Pipeline" section
- Definition: "Pipeline script from SCM"
- SCM: "Git"
- Repository URL: Your GitHub repo URL
  ```
  https://github.com/YOUR_USERNAME/cicd-demo
  ```
- Branch: `*/main`

**3. Save & Build:**
- Click "Save"
- Click "Build Now"
- Watch the build progress

---

## 📊 GitHub Actions Workflow

The workflow automatically runs when you push code.

**What it does:**
1. **Checkout** - Gets your code
2. **Build** - Creates Docker image
3. **Test** - Runs unit tests
4. **Security** - Scans for issues
5. **Push** - Pushes to Docker Hub (if configured)
6. **Notify** - Reports status

**Monitor Status:**
- Go to GitHub repo
- Click "Actions" tab
- See workflow run in real-time

### Enable Docker Hub Push (Optional)

To push images to Docker Hub:

1. Create Docker Hub account at hub.docker.com
2. Generate Personal Access Token:
   - Settings → Security → New Access Token
3. Add GitHub Secrets:
   - Repo → Settings → Secrets and variables → Actions
   - Add: `DOCKER_USERNAME` (your Docker Hub username)
   - Add: `DOCKER_PASSWORD` (your access token)

---

## 🚀 Running the Flask Application

### Option 1: Via Docker Compose (Recommended)

```bash
docker-compose up --build
# App runs on http://localhost:5000
```

### Option 2: Standalone (Local Development)

```bash
# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL in Docker
docker run -d \
  -e POSTGRES_USER=appuser \
  -e POSTGRES_PASSWORD=apppass \
  -e POSTGRES_DB=appdb \
  -p 5432:5432 \
  postgres:15-alpine

# Set environment variables
export DB_HOST=localhost
export POSTGRES_USER=appuser
export POSTGRES_PASSWORD=apppass
export POSTGRES_DB=appdb

# Run app
python app.py

# Access at http://localhost:5000
```

---

## 🧪 Testing

### Run Tests Locally

```bash
pip install -r requirements.txt
pytest test_app.py -v
```

### Run Tests in Docker

```bash
docker-compose run app pytest test_app.py -v
```

### Coverage Report

```bash
pytest test_app.py --cov=. --cov-report=html
# Opens htmlcov/index.html in browser
```

---

## 🌐 API Endpoints

All endpoints available at `http://localhost:5000`

### Web Interface
```
GET /                  → Web page (messages UI)
```

### API Endpoints
```
GET  /api/messages              → Get all messages
POST /api/messages              → Add new message
                                 Body: {"text": "Hello"}
DELETE /api/messages/<id>       → Delete message

GET  /api/stats                 → Get statistics
GET  /health                    → Health check
```

### Example API Usage

```bash
# Get all messages
curl http://localhost:5000/api/messages

# Add a message
curl -X POST http://localhost:5000/api/messages \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello from API"}'

# Delete message (ID 1)
curl -X DELETE http://localhost:5000/api/messages/1

# Check health
curl http://localhost:5000/health

# Get statistics
curl http://localhost:5000/api/stats
```

---

## 📋 Complete Workflow Example

### Push Code → Test → Deploy

```bash
# 1. Make a change to app.py
echo "# Updated app" >> app.py

# 2. Commit and push
git add .
git commit -m "Update app"
git push origin main

# 3. Watch GitHub Actions
# - Go to repo → Actions tab
# - See workflow running

# 4. Jenkins can also run
# - Go to Jenkins → cicd-demo-app
# - Click "Build Now"
# - Watch pipeline execute

# 5. When done
# - Image is built
# - Tests passed
# - Ready to deploy!
```

---

## 🔍 Monitoring & Logs

### Docker Compose Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs jenkins
docker-compose logs app
docker-compose logs db

# Follow logs (real-time)
docker-compose logs -f

# Last 50 lines
docker-compose logs --tail=50
```

### Jenkins Logs

```bash
# Jenkins container logs
docker logs jenkins-server

# Jenkins job logs
# Go to Jenkins UI → Select job → Console Output
```

### Application Logs

```bash
# Flask app logs
docker-compose logs -f app

# Database logs
docker-compose logs -f db
```

---

## 🐛 Troubleshooting

### Jenkins won't start
```bash
# Check logs
docker-compose logs jenkins

# Restart
docker-compose restart jenkins

# Rebuild
docker-compose down
docker-compose up --build
```

### Port already in use
```bash
# Find what's using the port
lsof -i :8080        # Jenkins
lsof -i :5000        # Flask app
lsof -i :5432        # PostgreSQL

# Kill the process
kill -9 <PID>

# Or use different ports in docker-compose.yml
```

### Database connection error
```bash
# Check PostgreSQL
docker-compose logs db

# Test connection
docker-compose exec app psql -h db -U appuser -d appdb

# Restart database
docker-compose restart db
```

### Tests failing
```bash
# Run tests with more detail
pytest test_app.py -v -s

# Run in container
docker-compose run app pytest test_app.py -v
```

---

## 📊 Pipeline Status Checks

### GitHub Actions
- ✅ Code quality checks
- ✅ Unit tests
- ✅ Security scanning
- ✅ Docker image build
- ✅ Push to registry

### Jenkins
- ✅ Code checkout
- ✅ Docker build
- ✅ Image tests
- ✅ Unit tests
- ✅ Security scan
- ✅ Image push
- ✅ Deploy simulation

---

## 🎓 Learning Path

### Day 1: Understand the Basics
1. Start docker-compose
2. Access Flask app
3. Send a message
4. Check API endpoints

### Day 2: Learn Docker
1. Examine Dockerfile
2. Build image manually
3. Run container
4. Check logs

### Day 3: Explore Jenkins
1. Access Jenkins UI
2. Create a new job
3. Configure Git repo
4. Run a build
5. Check console output

### Day 4: GitHub Actions
1. Go to GitHub Actions tab
2. Watch workflow run
3. Check logs
4. Review status checks

### Day 5: Full Pipeline
1. Make code change
2. Push to GitHub
3. Watch GitHub Actions run
4. Run Jenkins build
5. See deployment simulation

---

## 📚 Quick Reference

### Most Used Commands

```bash
# Start everything
docker-compose up --build

# View logs
docker-compose logs -f

# Run tests
pytest test_app.py -v

# Build image
docker build -t myapp .

# Run container
docker run -p 5000:5000 myapp

# Stop everything
docker-compose down
```

### Access Points

| Service | URL | Port |
|---------|-----|------|
| Flask App | http://localhost:5000 | 5000 |
| Jenkins | http://localhost:8080 | 8080 |
| PostgreSQL | localhost:5432 | 5432 |
| Adminer (DB UI) | http://localhost:8081 | 8081 |

---

## ✅ Verification Checklist

- [ ] Docker installed and running
- [ ] Codespaces opened with project
- [ ] `docker-compose up --build` successful
- [ ] Flask app accessible at http://localhost:5000
- [ ] Jenkins accessible at http://localhost:8080
- [ ] Can send message in Flask app
- [ ] Tests pass: `pytest test_app.py -v`
- [ ] GitHub Actions workflow configured
- [ ] Jenkinsfile in repository
- [ ] Ready to push and trigger pipeline

---

## 🎉 Success!

You now have:
- ✅ A complete Flask application
- ✅ Docker containerization
- ✅ Jenkins CI/CD server
- ✅ GitHub Actions automation
- ✅ Automated testing
- ✅ Security scanning
- ✅ Deployment pipeline

**Next Steps:**
1. Deploy to cloud (AWS, GCP, Azure)
2. Add more complex tests
3. Implement Kubernetes
4. Add monitoring with Prometheus

---

## 📞 Help & Support

### Common Issues & Solutions

**Q: Jenkins won't unlock**
A: Run: `docker exec jenkins-server cat /var/jenkins_home/secrets/initialAdminPassword`

**Q: Flask app returns 500 error**
A: Check database is running: `docker-compose logs db`

**Q: Tests failing**
A: Run with verbose: `pytest test_app.py -v -s`

**Q: Port conflicts**
A: Edit docker-compose.yml port mappings or kill conflicting processes

---

**Happy CI/CD Learning! 🚀**
