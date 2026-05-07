# 🎓 Student API — FastAPI + Streamlit

Learn how **REST APIs** work by running a real backend + frontend on GitHub Codespaces.

---

## 📁 Project Structure

```
api_project/
├── backend/
│   └── main.py          ← FastAPI — the API server
├── frontend/
│   └── app.py           ← Streamlit — the web UI
├── .devcontainer/
│   └── devcontainer.json  ← Codespaces config
├── requirements.txt
└── README.md
```

---

## 🚀 How to Run

You need **two terminals** — one for each server.

### Terminal 1 — Start the API (Backend)
```bash
uvicorn backend.main:app --reload --port 8000
```

### Terminal 2 — Start the UI (Frontend)
```bash
streamlit run frontend/app.py --server.port 8501
```

Then open the **Streamlit** tab (port 8501) in your browser.

---

## 🌐 API Endpoints

| Method | URL | What it does |
|--------|-----|-------------|
| GET | `/` | Health check |
| GET | `/students` | List all students |
| GET | `/students/{id}` | Get one student |
| GET | `/search?subject=Math` | Filter by subject |
| GET | `/stats` | Class statistics |
| POST | `/students` | Add a student |
| PUT | `/students/{id}` | Update a student |
| DELETE | `/students/{id}` | Remove a student |

---

## 📖 Interactive Docs

FastAPI generates docs automatically!  
Open **port 8000** and visit:

- `/docs` — Swagger UI (try requests directly in browser)
- `/redoc` — ReDoc (clean readable docs)

---

## 🧠 Key Concepts

| Term | Meaning |
|------|---------|
| **API** | A way for two programs to talk to each other |
| **REST** | A style of API using URLs + HTTP methods |
| **Endpoint** | A specific URL the API listens on |
| **GET** | Read / fetch data |
| **POST** | Create new data |
| **PUT** | Update existing data |
| **DELETE** | Remove data |
| **JSON** | The data format APIs use (like a Python dict) |
| **Status 200** | ✅ OK — request succeeded |
| **Status 201** | ✅ Created — new item was made |
| **Status 404** | ❌ Not Found — item doesn't exist |

---

## 🏋️ Exercises for Students

1. **Add a new student** using the POST page, then find them with GET.
2. **Change a grade** using PUT — what happens to the stats?
3. **Delete a student** — what status code do you get if you try to delete again?
4. **Read the backend code** — can you add a new field like `email`?
5. **Open `/docs`** on port 8000 — try calling the API directly from the browser.