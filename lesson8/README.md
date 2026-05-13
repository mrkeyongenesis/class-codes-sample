# 🚀 Complete CI/CD Pipeline Demo - Jenkins + GitHub + Docker

A production-ready example demonstrating a complete CI/CD pipeline with Jenkins, GitHub Actions, Docker, and a Flask application.

## 📸 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Repository                          │
│                  (GitHub/GitLab/etc)                        │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    ┌────▼────┐      ┌───▼────┐    ┌────▼────┐
    │ GitHub  │      │ Jenkins│    │ Local   │
    │ Actions │      │ Server │    │ Dev     │
    └────┬────┘      └───┬────┘    └────┬────┘
         │               │              │
         └───────────────┼──────────────┘
                         │
                  ┌──────▼─────┐
                  │   Build    │
                  │   Docker   │
                  │   Image    │
                  └──────┬─────┘
                         │
                    ┌────▼────┐
                    │   Test  │
                    │   & Run │
                    └────┬────┘
                         │
            ┌────────────┴──────────┐
            │                       │
        ┌───▼────┐            ┌────▼───┐
        │ Flask  │            │Database│
        │ App    │            │(PG)    │
        └────────┘            └────────┘
```

## ✨ Features

- 🐳 **Docker Containerization** - Complete containerized setup
- 🔄 **GitHub Actions** - Automated CI/CD pipeline
- 🔧 **Jenkins Integration** - Enterprise-grade CI/CD server
- 🧪 **Automated Testing** - Unit tests with pytest
- 🔐 **Security Scanning** - Automated security checks
- 📊 **PostgreSQL Database** - Data persistence
- 🌐 **Flask Web App** - Modern web interface
- 📈 **Health Checks** - Monitoring and verification
- 🚀 **Ready to Deploy** - Production-ready setup

## 🎯 Quick Start

### Prerequisites
- Docker & Docker Compose
- 4GB free disk space
- Modern web browser
- (Optional) GitHub account for Actions

### Installation

**1. Clone/Setup Repository**
```bash
# If using Git
git clone https://github.com/YOUR_USERNAME/cicd-demo
cd cicd-demo

# Or create new directory
mkdir cicd-demo && cd cicd-demo
```

**2. Start Everything**
```bash
# Option A: Use quick start script (Linux/Mac)
chmod +x quickstart.sh
./quickstart.sh

# Option B: Manual start
docker-compose up --build
```

**3. Access Services**
- **Flask App**: http://localhost:5000
- **Jenkins**: http://localhost:8080  
- **PostgreSQL**: localhost:5432

**4. Initial Jenkins Setup (First Time)**
```bash
# Get initial password
docker exec jenkins-server cat /var/jenkins_home/secrets/initialAdminPassword

# Paste into http://localhost:8080
# Follow setup wizard
```

## 📁 Project Structure

```
.
├── app.py                          # Flask application (570 lines)
├── test_app.py                     # Unit tests (100+ lines)
├── Dockerfile                      # Container specification
├── docker-compose.yml              # Multi-container setup
├── requirements.txt                # Python dependencies
├── Jenkinsfile                     # Jenkins pipeline
├── .github/
│   └── workflows/
│       └── cicd.yml               # GitHub Actions workflow
├── SETUP_GUIDE.md                 # Detailed setup guide
├── quickstart.sh                  # Quick start script
└── README.md                       # This file
```

## 🐳 Docker Compose Services

### Jenkins (Port 8080)
- CI/CD automation server
- Web interface for job configuration
- Supports both freestyle and pipeline jobs
- Docker integration for building images

### Flask App (Port 5000)
- Web interface with message functionality
- REST API endpoints
- PostgreSQL database integration
- Health checks and monitoring

### PostgreSQL (Port 5432)
- Data persistence
- User: appuser
- Password: apppass
- Database: appdb

## 📊 Complete Workflow

### From Commit to Running App

```
1. Developer commits code
   └─→ git push origin main

2. GitHub Actions triggers
   ├─→ Checkout code
   ├─→ Build Docker image
   ├─→ Run tests
   ├─→ Security scan
   ├─→ Push to registry (optional)
   └─→ Report status

3. Jenkins can also run (optional)
   ├─→ Pull code
   ├─→ Build Docker image
   ├─→ Run tests
   ├─→ Security scan
   ├─→ Push to registry (optional)
   └─→ Deployment simulation

4. Application is running
   └─→ Access at http://localhost:5000
```

## 🧪 Testing

### Run All Tests
```bash
# Using pytest
pytest test_app.py -v

# Or in Docker
docker-compose run app pytest test_app.py -v
```

### Test Coverage
```bash
# Generate coverage report
pytest test_app.py --cov=. --cov-report=html

# View report
open htmlcov/index.html
```

### Specific Tests
```bash
# Run one test class
pytest test_app.py::TestHealthCheck -v

# Run one test
pytest test_app.py::TestHealthCheck::test_health_endpoint_exists -v
```

## 🌐 API Endpoints

### Web Interface
- `GET /` - Main web page

### API Endpoints
```bash
# Get all messages
curl http://localhost:5000/api/messages

# Add message
curl -X POST http://localhost:5000/api/messages \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello"}'

# Delete message
curl -X DELETE http://localhost:5000/api/messages/1

# Get statistics
curl http://localhost:5000/api/stats

# Health check
curl http://localhost:5000/health
```

## 🔧 Jenkins Pipeline

### Create New Pipeline Job

1. Click "New Item"
2. Name: `cicd-demo-app`
3. Select: "Pipeline"
4. In "Pipeline" section:
   - Definition: "Pipeline script from SCM"
   - SCM: "Git"
   - Repository URL: Your GitHub repo
   - Branch: `*/main`
5. Click "Save"
6. Click "Build Now"

### Pipeline Stages

```
Checkout
  ↓
Build Docker Image
  ↓
Test Image
  ↓
Run Unit Tests
  ↓
Security Scan
  ↓
Push to Registry (optional)
  ↓
Deploy
  ↓
Verify Deployment
```

## 🔐 GitHub Actions Workflow

The workflow automatically runs when you push code.

### Jobs in Workflow

1. **build** - Creates Docker image
2. **test** - Runs unit tests with PostgreSQL
3. **security** - Scans for security issues
4. **push-image** - Pushes to Docker Hub (optional)
5. **notify** - Reports status
6. **deploy** - Deployment simulation

### Monitor Workflow

1. Push code to GitHub
2. Go to repo → Actions tab
3. See workflow running in real-time
4. Check logs for each job

### Enable Docker Hub Integration

1. Create Docker Hub account at hub.docker.com
2. Generate Personal Access Token:
   - Settings → Security → New Access Token
3. Add GitHub Secrets:
   - Repo → Settings → Secrets → Actions
   - `DOCKER_USERNAME`: Your Docker Hub username
   - `DOCKER_PASSWORD`: Your access token

## 📊 Monitoring & Logs

### Docker Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs -f app
docker-compose logs -f jenkins
docker-compose logs -f db

# Last N lines
docker-compose logs --tail=50
```

### Jenkins Logs
```bash
# Container logs
docker logs -f jenkins-server

# Job console output
# Jenkins UI → Job → Build → Console Output
```

### Application Logs
```bash
# Flask app
docker-compose logs -f app

# Database
docker-compose logs -f db
```

## 🛠️ Useful Commands

### Docker Compose
```bash
# Start services
docker-compose up --build

# Start in background
docker-compose up -d --build

# View status
docker-compose ps

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Restart service
docker-compose restart app
```

### Docker
```bash
# Build image
docker build -t myapp .

# Run container
docker run -p 5000:5000 myapp

# View images
docker images

# View containers
docker ps -a

# View logs
docker logs <container-id>

# Execute command
docker exec <container-id> bash
```

### Testing
```bash
# Run all tests
pytest test_app.py -v

# Run with coverage
pytest test_app.py --cov

# Run specific test
pytest test_app.py::TestHealthCheck -v

# Verbose output
pytest test_app.py -v -s
```

## 🐛 Troubleshooting

### Jenkins won't start
```bash
# Check logs
docker-compose logs jenkins

# Restart
docker-compose restart jenkins

# Rebuild
docker-compose down && docker-compose up --build
```

### Port conflicts
```bash
# Find process using port
lsof -i :8080      # Jenkins
lsof -i :5000      # Flask
lsof -i :5432      # PostgreSQL

# Kill process
kill -9 <PID>

# Or modify docker-compose.yml ports
```

### Database connection failed
```bash
# Check PostgreSQL
docker-compose logs db

# Restart database
docker-compose restart db

# Test connection
docker-compose exec app psql -h db -U appuser -d appdb
```

### Tests failing
```bash
# Run with verbose output
pytest test_app.py -v -s

# Run in Docker
docker-compose run app pytest test_app.py -v

# Check database is running
docker-compose ps db
```

## 📚 Learning Resources

### Docker
- [Docker Official Docs](https://docs.docker.com)
- [Docker Compose Docs](https://docs.docker.com/compose)

### Jenkins
- [Jenkins Documentation](https://www.jenkins.io/doc)
- [Jenkins Pipelines](https://www.jenkins.io/doc/book/pipeline)

### GitHub Actions
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)

### Flask
- [Flask Documentation](https://flask.palletsprojects.com)
- [Flask API](https://flask.palletsprojects.com/api)

## ✅ Checklist

- [ ] Docker installed
- [ ] Docker Compose installed
- [ ] Project files downloaded/cloned
- [ ] `docker-compose up --build` successful
- [ ] Flask app accessible at http://localhost:5000
- [ ] Jenkins accessible at http://localhost:8080
- [ ] PostgreSQL connected
- [ ] Tests passing
- [ ] GitHub repo created (optional)
- [ ] GitHub Actions enabled (optional)
- [ ] Jenkins pipeline configured (optional)

## 🎯 Next Steps

1. **Explore the Code** - Understand app.py and Jenkinsfile
2. **Customize** - Modify Flask app for your needs
3. **Deploy** - Push to AWS, GCP, or Azure
4. **Monitor** - Add Prometheus/Grafana
5. **Scale** - Use Kubernetes for multiple instances

## 📞 Support

### Common Issues

| Issue | Solution |
|-------|----------|
| Jenkins won't unlock | `docker exec jenkins-server cat /var/jenkins_home/secrets/initialAdminPassword` |
| Port already in use | Change ports in docker-compose.yml |
| Tests failing | Run `pytest test_app.py -v -s` for details |
| Database error | Check `docker-compose logs db` |
| Image too large | Use `docker system prune` |

## 📄 License

MIT License - Use freely!

## 🤝 Contributing

Feel free to fork, modify, and improve!

## 👨‍💼 Author

Created as a learning resource for CI/CD pipelines with Docker, Jenkins, and GitHub.

---

## 🎉 Success Indicators

You'll know everything is working when:

✅ Flask app shows message UI at http://localhost:5000  
✅ Can send and view messages in browser  
✅ Jenkins dashboard accessible at http://localhost:8080  
✅ `docker-compose ps` shows 3 healthy services  
✅ `pytest test_app.py -v` passes all tests  
✅ GitHub Actions workflow runs on push  

**Congratulations! You have a complete CI/CD pipeline! 🚀**

---

**Last Updated**: 2024  
**Status**: Production Ready ✅
