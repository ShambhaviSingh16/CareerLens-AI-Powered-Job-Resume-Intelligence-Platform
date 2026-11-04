import { useId, useState } from "react";
import { Icon } from "./Brand";

const labels = { strong: "Strong match", partial: "Partial match", missing: "Not demonstrated" };

export default function AnalysisResults({ analysis }) {
  const { result } = analysis;
  const [tab, setTab] = useState("skills");
  const [filter, setFilter] = useState("all");
  const id = useId();
  function exportReport() {
    const blob = new Blob([JSON.stringify(analysis, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "careerlens-report.json";
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  function navigateTabs(event) {
    const tabs = ["skills", "edits", "checks"];
    const index = tabs.indexOf(tab);
    const moves = { ArrowRight: (index + 1) % 3, ArrowLeft: (index + 2) % 3, Home: 0, End: 2 };
    if (!(event.key in moves)) return;
    event.preventDefault();
    setTab(tabs[moves[event.key]]);
    event.currentTarget.parentElement.children[moves[event.key]].focus();
  }
  const counts = Object.fromEntries(["strong", "partial", "missing"].map(status => [status, result.skills.filter(skill => skill.status === status).length]));
  const skills = result.skills.filter(skill => filter === "all" || skill.status === filter);
  return <section className="report" aria-label="Analysis results">
    <div className="report-toolbar"><span className="eyebrow">YOUR MATCH REPORT</span><button onClick={exportReport}>Download report ↓</button></div>
    <div className="report-summary">
      <div className="score-ring"><svg viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r="42" className="ring-track"/><circle cx="50" cy="50" r="42" className="ring-fill" strokeDasharray="263.9" strokeDashoffset={263.9 * (1 - result.match_score / 100)}/></svg><div><strong>{result.match_score}<small>%</small></strong><span>SKILL FIT</span></div></div>
      <div className="report-summary-copy"><p className="eyebrow">YOUR MATCH, IN CONTEXT</p><h2>{analysis.job_title}</h2><p>{result.summary}</p><span className="report-file"><Icon name="file" size={14}/>{analysis.filename}</span></div>
    </div>
    <details className="score-method"><summary>How we arrived at this score <span>+</span></summary><p>{result.score_explanation}</p><p>Model: {result.model} · Rubric {result.rubric_version}. AI assessments can be wrong; this is not a hiring prediction.</p></details>
    <div className="report-tabs" role="tablist" aria-label="Report sections">
      {[["skills", "Skill evidence", result.skills.length], ["edits", "Suggested edits", result.suggestions.length], ["checks", "Document checks", result.document_checks.length]].map(([value, label, count]) => <button key={value} role="tab" id={id + value} tabIndex={tab === value ? 0 : -1} aria-selected={tab === value} aria-controls={id + "-panel"} onKeyDown={navigateTabs} onClick={() => setTab(value)} className={tab === value ? "active" : ""}>{label}<span>{count}</span></button>)}
    </div>
    <div role="tabpanel" id={id + "-panel"} aria-labelledby={id + tab} className="report-content">
      {tab === "skills" && <>
        <div className="skill-filters" aria-label="Filter skill matches">{[["all", "All skills", result.skills.length], ["strong", "Strong", counts.strong], ["partial", "Partial", counts.partial], ["missing", "Missing", counts.missing]].map(([value, label, count]) => <button key={value} onClick={() => setFilter(value)} aria-pressed={filter === value} className={filter === value ? "active" : ""}>{value !== "all" && <span className={"status-dot " + value}/>} {label} <span className="filter-count">{count}</span></button>)}</div>
        {skills.length === 0 && <p className="empty-filter">No skills in this category.</p>}
        {skills.map((skill, index) => <article className="skill-row" key={skill.skill + index}>
          <div className="skill-row-heading"><div><h3>{skill.skill}</h3><span className="skill-priority">{skill.required ? "REQUIRED · WEIGHT 2" : "PREFERRED · WEIGHT 1"}</span></div><span className={"status-label " + skill.status}><span className={"status-dot " + skill.status}/>{labels[skill.status]}</span></div>
          <div className="evidence-columns"><div><p className="evidence-label">THE ROLE ASKS FOR</p><p>“{skill.requirement_quote}”</p></div><div className={skill.evidence ? "evidence-found" : "evidence-absent"}><p className="evidence-label">{skill.evidence ? "YOUR RESUME SAYS" : "IN YOUR RESUME"}</p><p>{skill.evidence ? "“" + skill.evidence + "”" : "No supporting passage found."}</p></div></div>
          <p className="skill-explanation"><span>↳</span>{skill.explanation}</p>
        </article>)}
      </>}
      {tab === "edits" && <div className="edit-list"><p className="report-section-note">Clearer wording, grounded in your experience. Review each suggestion before adding it to your resume.</p>{result.suggestions.length === 0 && <p className="empty-filter">No grounded rewrites were suggested for this resume.</p>}{result.suggestions.map((item, index) => <article className="edit-row" key={index}><span className="eyebrow">EDIT {String(index + 1).padStart(2, "0")}</span><div className="edit-original"><span className="evidence-label">BEFORE</span><p>{item.original}</p></div><div className="edit-rewrite"><span className="evidence-label">A CLEARER WAY TO SAY IT</span><p>{item.rewrite}</p></div><p className="skill-explanation"><span>↳</span>{item.reason}</p></article>)}</div>}
      {tab === "checks" && <div><p className="report-section-note">A check for common headings and contact text. This does not inspect visual formatting or certify compatibility with any ATS.</p>{result.document_checks.map(check => <div className="document-check" key={check.label}><span>{check.label}</span><span className={"status-label " + (check.found ? "strong" : "partial")}>{check.found ? <Icon name="check" size={15}/> : "○"}{check.found ? "Found" : "Review needed"}</span></div>)}</div>}
    </div>
  </section>;
}
