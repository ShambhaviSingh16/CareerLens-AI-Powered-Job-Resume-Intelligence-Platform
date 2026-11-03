export const sample = {
  job_title: "Junior backend developer", filename: "synthetic-example.pdf",
  result: {
    match_score: 50, model: "Illustrative sample; no live model call", rubric_version: "1.0",
    summary: "This fictional candidate demonstrates Python API development and related SQL experience. Automated testing is not evidenced. Docker exposure is introductory.",
    score_explanation: "Required skills count twice as much as preferred skills. Strong = 1, partial = 0.5, missing = 0. Weighted points: (2 + 1 + 0 + 0.5) / (2 + 2 + 2 + 1) = 50%.",
    skills: [
      { skill: "Python APIs", required: true, status: "strong", requirement_quote: "Build backend APIs with Python.", evidence: "Built a Python FastAPI service for a college library.", explanation: "The project provides direct evidence of building APIs in Python with FastAPI." },
      { skill: "SQL", required: true, status: "partial", requirement_quote: "Write and optimize SQL queries.", evidence: "Used SQLite to store books and borrowers.", explanation: "SQLite usage is relevant, but does not demonstrate query optimization." },
      { skill: "Automated testing", required: true, status: "missing", requirement_quote: "Write automated tests.", evidence: null, explanation: "The resume does not mention automated tests or testing tools." },
      { skill: "Docker", required: false, status: "partial", requirement_quote: "Docker familiarity is preferred.", evidence: "Completed an introductory Docker workshop.", explanation: "The workshop shows introductory exposure, but not hands-on project deployment." },
    ],
    suggestions: [{ original: "Built a Python FastAPI service for a college library.", rewrite: "Developed a college library service using Python and FastAPI.", reason: "Makes the implementation stack explicit without adding unverified achievements." }],
    document_checks: [{ label: "Experience or projects heading", found: true }, { label: "Education heading", found: true }, { label: "Skills heading", found: true }, { label: "Email address", found: true }],
  },
};
