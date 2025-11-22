

# 📡 AstroResearch Agent

A full-stack AI-powered tool that analyzes astrophysics topics, retrieves relevant research papers, performs domain-specific computations, and generates structured research-style reports.

Built with **FastAPI**, **React + Vite**, and a modular service-based architecture designed for future LLM + arXiv integration.

---

# 🧱 Tech Stack

**Frontend**

* React (Vite)
* TailwindCSS
* Fetch API

**Backend**

* FastAPI
* Uvicorn
* Pydantic
* httpx (for future arXiv API integration)

**Other**

* Python virtual environment
* Node.js (LTS)
* Git + GitHub

---

# 📂 Project Structure

```
astroresearch-agent/
│
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app entry point
│   │   ├── routers/           # API route files
│   │   ├── models/            # Pydantic request/response schemas
│   │   ├── services/          # arXiv, LLM, astrophysics logic (modular)
│   └── requirements.txt
│
├── frontend/
│   ├── src/                   # React components & pages
│   ├── public/
│   ├── package.json
│
└── docs/                      # API & project documentation
```

---

# ⚙️ Running the Project Locally

## **1. Clone the Repository**

```bash
git clone https://github.com/Sujatx/astroresearch-agent.git
cd astroresearch-agent
```

---

# 🔧 Backend (FastAPI)

### **2. Navigate to backend**

```bash
cd backend
```

### **3. Create & activate virtual environment**

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

### **4. Install dependencies**

```bash
pip install -r requirements.txt
```

### **5. Start backend server**

```bash
uvicorn app.main:app --reload
```

Runs at:

```
http://127.0.0.1:8000
```

---

# 🎨 Frontend (React + Vite)

### **6. Open a new terminal & navigate to frontend**

```bash
cd frontend
```

### **7. Install dependencies**

```bash
npm install
```

### **8. Start the dev server**

```bash
npm run dev
```

Runs at:

```
http://localhost:5173
```

(or a nearby port)

---

# 🤝 Contribution Guide

### **Branching Strategy**

* Create a new branch for each feature.
* Keep `main` clean.

### **Commits**

Use clear commit messages:

```
feat: added arxiv lookup service
fix: corrected API response model
chore: updated readme
```

### **Pull Requests**

* Small PRs = faster review.
* Describe what you changed and why.
* Link related issues if any.

### **Code Style**

* Follow existing folder structure.
* Keep backend logic modular inside `/services`.
* Keep frontend clean and component-based.

