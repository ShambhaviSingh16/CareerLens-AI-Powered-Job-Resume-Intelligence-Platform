<!--# CareerLens-AI-Powered-Job-Resume-Intelligence-Platform-->
<div align="center">

# CareerLens

### AI-powered resume and job match intelligence

Know exactly how well you match a job, what's missing, and how to fix it — before you apply.

🚧 **Live demo link coming soon — see Running Locally below to try it now**

<!--[Live Demo](#) · [Report a Bug](#) · [Features](#features)-->

</div>

---

## The Problem

Most job seekers apply without knowing how well their resume actually fits the role. They find out something was wrong only after getting rejected — and even then, rarely know exactly what to fix. Generic keyword-matching tools don't help much either, since they miss the fact that "developed REST APIs" and "built scalable backend services" often mean the same thing in different words.

**CareerLens replaces that guesswork with a clear, evidence-based answer.**

---

<!--## What CareerLens Does-->
## Core Features

Upload a resume and paste in a job description. CareerLens reads both, compares them using AI, and returns a structured breakdown — not just a score, but the *reasoning* behind it.

### Features

**🎯 Match Score**
A single, clear score showing overall fit between the resume and the job description.

**🧩 Skill-by-Skill Breakdown**
Every required skill from the job description is checked against the resume and marked as a Strong Match, Partial Match, or Missing — with a short, specific explanation for each. Instead of a generic "Python: ✓," CareerLens explains *where* in the resume that skill is demonstrated, or why it's only a partial match.

**🔍 Semantic Understanding, Not Just Keywords**
CareerLens recognizes when a resume demonstrates a skill using different wording than the job description — for example, connecting "built REST APIs with Spring Boot" to a requirement for "backend service development," rather than requiring an exact keyword match.

**✍️ Resume Improvement Suggestions**
For each gap or weak match, CareerLens suggests specific rewritten phrasing — always grounded in what the candidate has actually done, never inventing experience they don't have.

**📄 ATS Readiness Check**
Flags common formatting and structural issues that can cause a resume to be misread or rejected by automated screening systems — missing sections, unclear headings, inconsistent formatting.

**🔐 Personal Account**
Sign up, log in, and keep a history of every resume-to-job analysis in one place.

---

## How It Works

```
1. Sign up / log in
2. Upload your resume (PDF or Word)
3. Paste in a job description
4. CareerLens parses both and runs them through its AI matching engine
5. Get a full breakdown: match score, skill analysis, resume suggestions, ATS notes
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite, Tailwind CSS |
| Backend | FastAPI (Python) |
| Database | PostgreSQL (Neon) |
| AI / Matching Engine | Groq API (LLM-based semantic analysis) |
| Resume Parsing | PyMuPDF, python-docx |
| Authentication | JWT-based auth with hashed passwords |
| Testing | Pytest |
| Deployment | Render (backend), Vercel (frontend) |
| CI/CD | GitHub Actions |

<!--Built and hosted entirely on free-tier infrastructure — no paid services.-->

---

<!--## Screenshots

*(Add real screenshots here once available — landing page, upload flow, and the results dashboard are the three that matter most to a recruiter skimming this repo.)* 

| Landing Page | Analysis Results |
|---|---|
| *screenshot* | *screenshot* |

---
-->
## Running Locally

```bash
git clone https://github.com/your-username/careerlens.git
cd careerlens

# Backend
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
# Add a .env file with DATABASE_URL, GROQ_API_KEY, JWT_SECRET
uvicorn main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Backend runs at `http://localhost:8000` · Frontend runs at `http://localhost:5173`

---

## Why This Project

Job searching is a process most people go through with very little real feedback. CareerLens was built to close that gap — turning the vague feeling of "I'm not sure if I'm a good fit for this role" into a specific, actionable answer, grounded in the actual content of a resume rather than a keyword count.

---
 
## License

MIT
