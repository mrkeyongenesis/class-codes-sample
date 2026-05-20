# Build a CI/CD Pipeline with Jenkins in GitHub Codespaces

A complete, self-contained guide to building a sample Flask web app and running it through a Jenkins **build → test → pipeline** workflow — entirely inside a GitHub Codespace.

This adapts the Cisco DEVASC "Build a CI/CD Pipeline Using Jenkins" lab to Codespaces. The key differences from the VM version are called out as **Codespaces notes** throughout.

---

## Prerequisites

- A GitHub Codespace with Docker available (see Step 0).
- The `gh` CLI (preinstalled in Codespaces).
- A GitHub **Personal Access Token (PAT)** for Jenkins credentials — generate one at **GitHub → Settings → Developer settings → Personal access tokens**, with at least `repo` scope.

---

## Step 0: Confirm Docker Works

In your Codespace terminal:

```bash
docker --version && docker ps
```

> **Codespaces note:** If `docker ps` errors, your Codespace lacks Docker-in-Docker. Add the feature below to `.devcontainer/devcontainer.json`, then rebuild the container (Command Palette → **Rebuild Container**):
>
> ```json
> {
>   "features": {
>     "ghcr.io/devcontainers/features/docker-in-docker:2": {}
>   }
> }
> ```

---

## Step 1: Create the Sample Web App Files

Create the folder structure:

```bash
mkdir -p ~/sample-app/templates ~/sample-app/static
cd ~/sample-app
```

### `sample_app.py`

A tiny Flask app on **port 5050** (Jenkins uses 8080, so the app must use a different port):

```python
from flask import Flask
from flask import request
from flask import render_template

sample = Flask(__name__)

@sample.route("/")
def main():
    return render_template("index.html")

if __name__ == "__main__":
    sample.run(host="0.0.0.0", port=5050)
```

### `templates/index.html`

```html
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <h1>You are calling me from {{ request.remote_addr }}</h1>
</body>
</html>
```

### `static/style.css`

```css
body {
    background-color: lightsteelblue;
    font-family: sans-serif;
    text-align: center;
}
```

### `sample-app.sh`

Builds and runs the app in Docker on port 5050:

```bash
#!/bin/bash
rm -rf tempdir
mkdir tempdir
mkdir tempdir/templates
mkdir tempdir/static
cp sample_app.py tempdir/.
cp -r templates/* tempdir/templates/.
cp -r static/* tempdir/static/.
echo "FROM python" >> tempdir/Dockerfile
echo "RUN pip install flask" >> tempdir/Dockerfile
echo "COPY ./static /home/myapp/static/" >> tempdir/Dockerfile
echo "COPY ./templates /home/myapp/templates/" >> tempdir/Dockerfile
echo "COPY sample_app.py /home/myapp/" >> tempdir/Dockerfile
echo "EXPOSE 5050" >> tempdir/Dockerfile
echo "CMD python3 /home/myapp/sample_app.py" >> tempdir/Dockerfile
cd tempdir
docker build -t sampleapp .
docker run -t -d -p 5050:5050 --name samplerunning sampleapp
docker ps -a
```

> **Note:** The `rm -rf tempdir` at the top (not in the original lab) lets the script run repeatedly without failing on an existing folder — important because Jenkins runs it on every build.

### Test it locally before bringing Jenkins in

```bash
bash ./sample-app.sh
```

Add port `5050` in the **PORTS** tab and open it. You should see the light-blue "You are calling me from..." page. Then clean up:

```bash
docker stop samplerunning && docker rm samplerunning
```

---

## Step 2: Push the App to GitHub

Jenkins pulls from GitHub, so the app needs a repo:

```bash
cd ~/sample-app
git init
gh repo create sample-app --private --source=. --remote=origin
git add .
git commit -m "Initial sample app on port 5050"
git push -u origin main
```

> **Codespaces note:** The `gh` CLI is preinstalled and authenticated, so this push needs no token. Your default branch is **main** (not `master`) — remember this for the build job.

---

## Step 3: Pull and Run Jenkins

Pull the image:

```bash
docker pull jenkins/jenkins:lts
```

Run it (single line):

```bash
docker run --rm -u root -p 8080:8080 \
  -v jenkins-data:/var/jenkins_home \
  -v /usr/bin/docker:/usr/bin/docker \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v "$HOME":/home \
  --name jenkins_server jenkins/jenkins:lts
```

**Option breakdown:**

| Option | Purpose |
|--------|---------|
| `--rm` | Removes the container when stopped |
| `-u root` | Runs as root so Docker commands inside Jenkins are permitted |
| `-p 8080:8080` | Exposes Jenkins on port 8080 |
| `-v jenkins-data:/var/jenkins_home` | Persists Jenkins data |
| `-v /usr/bin/docker:/usr/bin/docker` | Gives Jenkins the Docker binary |
| `-v /var/run/docker.sock:/var/run/docker.sock` | Lets Jenkins talk to Docker |
| `-v "$HOME":/home` | Mounts your home directory |

> **Codespaces note:** The `-v /usr/bin/docker:/usr/bin/docker` mount assumes Docker's binary lives at that path. Confirm with `which docker` first and substitute if it differs, or Docker commands inside Jenkins will fail.

Get the admin password from a **second terminal**:

```bash
docker exec -it jenkins_server cat /var/jenkins_home/secrets/initialAdminPassword
```

In the **PORTS** tab, open the forwarded URL for port `8080`. Paste the password → **Install suggested plugins** → **Skip and continue as admin** → **Save and Finish** → **Start using Jenkins**.

---

## Step 4: Find Your Gateway IP

The test job curls the app over the Docker bridge. Find the real gateway:

```bash
docker network inspect bridge | grep Gateway
```

Use that value wherever this guide writes `<GATEWAY-IP>` below. It may be `172.17.0.1`, but **don't assume** — a wrong IP is the #1 cause of test failures.

---

## Step 5: BuildAppJob (the Build)

1. **New Item** → name `BuildAppJob` → **Freestyle project** → **OK**.
2. **General**: add a description like "Builds the sample app."
3. **Source Code Management → Git**, Repository URL:
   ```
   https://github.com/<your-username>/sample-app.git
   ```
4. **Credentials → Add → Jenkins**: enter your GitHub **username** and **Personal Access Token** as the password, click **Add**, then select it from the dropdown. (The red connection error clears once selected.)

   > **Note:** Jenkins can't reuse the Codespaces `gh` session, so it needs the PAT here.
5. **Branch Specifier**: set to `*/main`.
6. **Build Steps → Add build step → Execute shell**:
   ```bash
   bash ./sample-app.sh
   ```
7. **Save** → **Build Now**.
8. Open the build number under **Build History → Console Output**. Look for `Successfully tagged sampleapp:latest` and `Finished: SUCCESS`.

To verify the app, add port `5050` in the **PORTS** tab and open it.

---

## Step 6: TestAppJob (the Test)

First clean up the running container:

```bash
docker stop samplerunning && docker rm samplerunning
```

1. **New Item** → name `TestAppJob` → **Freestyle project** → **OK**.
2. Add a description like "Tests the sample app build."
3. **Source Code Management**: leave as **None** (this job doesn't need the repo).
4. **Build Triggers**: check **Build after other projects are built**; in **Projects to watch**, enter `BuildAppJob`. This chains the test to run after every successful build.
5. **Build Steps → Add build step → Execute shell** (the `if ...; then` must be on one line):
   ```bash
   if curl http://<GATEWAY-IP>:5050/ | grep "You are calling me from"; then
     exit 0
   else
     exit 1
   fi
   ```
   > **Note:** The grep is trimmed to "You are calling me from" (without a specific IP) so it matches regardless of your gateway. Exit code `0` = pass, `1` = fail.
6. **Save**.
7. Trigger `BuildAppJob` again (clock/play icon). Both jobs' **Last Success** timestamps should update.
8. Open `TestAppJob` → **Permalinks → Last build → Console Output**. Success shows the `<h1>You are calling me from...</h1>` line, then `+ exit 0` and `Finished: SUCCESS`.

---

## Step 7: SamplePipeline (the CI/CD Pipeline)

1. **New Item** → name `SamplePipeline` → **Pipeline** → **OK**.
2. In the **Pipeline** section, paste:
   ```groovy
   node {
       stage('Preparation') {
           catchError(buildResult: 'SUCCESS') {
               sh 'docker stop samplerunning'
               sh 'docker rm samplerunning'
           }
       }
       stage('Build') {
           build 'BuildAppJob'
       }
       stage('Results') {
           build 'TestAppJob'
       }
   }
   ```
   **What it does:**
   - **Preparation** — stops/removes any old container, wrapped in `catchError` so a "no such container" error on the first run doesn't fail the pipeline.
   - **Build** — runs `BuildAppJob`.
   - **Results** — runs `TestAppJob`.
3. **Save** → **Build Now**.
4. The **Stage View** shows three green boxes (Preparation, Build, Results), each with a timing.
5. Open the latest build under **Permalinks → Console Output** to see the full `[Pipeline]` trace ending in `Finished: SUCCESS`.

That's the full CI/CD loop: change code, push to GitHub, re-run the pipeline, and it rebuilds and re-tests automatically.

---

## Troubleshooting

| Symptom | Likely cause / fix |
|---------|--------------------|
| `docker ps` fails | Docker-in-Docker not enabled — see Step 0. |
| Docker commands fail inside Jenkins | Wrong Docker binary path in the `-v` mount — check `which docker` (Step 3). |
| `TestAppJob` exits `1` but the app works in the browser | Wrong gateway IP — re-check `docker network inspect bridge` (Step 4). |
| Build can't reach the repo | Wrong branch (`*/main` vs `*/master`), wrong case-sensitive username, or missing/expired PAT. |
| `sample-app.sh` fails on second run | Make sure the `rm -rf tempdir` line is present, or stop/remove the `samplerunning` container. |
| Port 8080 not forwarding | Add it manually in the **PORTS** tab. |

---

*Adapted from the Cisco DEVASC lab "Build a CI/CD Pipeline Using Jenkins" for the GitHub Codespaces environment.*
