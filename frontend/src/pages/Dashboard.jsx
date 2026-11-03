import { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api, { errorMessage } from "../api/client";
import Brand, { Icon } from "../components/Brand";
import AnalysisResults from "../components/AnalysisResults";

export default function Dashboard() {
  const navigate = useNavigate();
  const [history, setHistory] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState("");
  const [historyError, setHistoryError] = useState("");
  const [busy, setBusy] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [fileName, setFileName] = useState("");
  const [description, setDescription] = useState("");
  const selection = useRef(0);

  useEffect(() => {
    const controller = new AbortController();
    api.get("/analyses", { signal: controller.signal }).then(({ data }) => {
      setHistory(data);
      setHistoryLoading(false);
    }).catch((err) => {
      if (err.code !== "ERR_CANCELED") {
        setHistoryError(errorMessage(err));
        setHistoryLoading(false);
      }
    });
    return () => controller.abort();
  }, []);

  async function submit(event) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const file = form.get("resume");
    if (file.size > 5 * 1024 * 1024 || !/\.(pdf|docx)$/i.test(file.name)) {
      setError("Choose a PDF or DOCX up to 5 MB.");
      return;
    }
    setError("");
    setBusy(true);
    selection.current += 1;
    try {
      const { data } = await api.post("/analyses", form);
      setAnalysis(data);
      setHistory((items) => [{
        id: data.id, job_title: data.job_title, filename: data.filename,
        created_at: data.created_at, match_score: data.result.match_score,
      }, ...items].slice(0, 50));
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function openAnalysis(id) {
    const request = ++selection.current;
    setError("");
    try {
      const { data } = await api.get(`/analyses/${id}`);
      if (request === selection.current) setAnalysis(data);
    } catch (err) {
      if (request === selection.current) setError(errorMessage(err));
    }
  }

  async function removeAnalysis(id) {
    setBusy(true);
    setError("");
    selection.current += 1;
    try {
      await api.delete(`/analyses/${id}`);
      setHistory((items) => items.filter((item) => item.id !== id));
      setAnalysis(null);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return <div className="workspace">
    <aside className="workspace-sidebar">
      <Brand/><div className="workspace-label eyebrow">YOUR WORKSPACE</div>
      <nav className="workspace-nav" aria-label="Workspace navigation">
        <button className={!analysis ? "active" : ""} disabled={busy} onClick={() => { selection.current += 1; setAnalysis(null); document.querySelector('.analysis-form')?.reset(); setFileName(''); setDescription(''); document.getElementById("job-title")?.focus(); }}><Icon name="plus" size={18}/>New analysis <span>↗</span></button>
        <a href="#recent-analyses"><Icon name="clock" size={18}/>Recent reports <span>{history.length}</span></a>
        <Link to="/sample"><Icon name="eye" size={18}/>Explore a sample <span>↗</span></Link>
      </nav>
      <div id="recent-analyses" className="workspace-history"><p className="eyebrow">RECENT REPORTS</p>
        {historyLoading && <p className="sidebar-note">Loading your reports…</p>}
        {historyError && <p role="alert" className="sidebar-note">{historyError}</p>}
        {!historyLoading && !historyError && history.length === 0 && <p className="sidebar-note">A fresh start.<br/>Your reports will live here.</p>}
        <ul>{history.map(item => <li key={item.id}><button disabled={busy} onClick={() => openAnalysis(item.id)} className={analysis?.id === item.id ? "selected" : ""}><Icon name="file" size={16}/><span><strong>{item.job_title}</strong><small>{new Date(item.created_at).toLocaleDateString(undefined, {month:"short", day:"numeric"})} · {item.match_score}% fit</small></span></button></li>)}</ul>
      </div>
      <div className="sidebar-bottom"><div className="sidebar-tip"><span className="eyebrow">A SMALL REMINDER</span><p>Your experience is the story.<br/>Your resume is how you tell it.</p></div><button className="logout-button" onClick={() => { sessionStorage.removeItem("token"); navigate("/login", { replace: true }); }}><span className="avatar">Y</span>Your workspace<Icon name="logout" size={17}/><span className="sr-only">Log out</span></button></div>
    </aside>
    <div className="workspace-main">
      <header className="workspace-topbar"><span><span className="breadcrumb-root">Workspace</span><span className="breadcrumb-slash">/</span>{analysis ? "Match report" : "New analysis"}</span><Link to="/sample">See an example <Icon size={14}/></Link></header>
      <main className="workspace-content">
        <div className="workspace-heading"><div><p className="eyebrow">A LITTLE CLARITY BEFORE YOU APPLY</p><h1>{analysis ? "Here's how you connect." : "Let's find your fit."}</h1><p>{analysis ? "A closer look at your experience, through the lens of this role." : "Your experience on one side. The opportunity on the other."}</p></div><span className="workspace-edition">CAREERLENS<br/>RESUME INTELLIGENCE</span></div>
        {error && <div role="alert" className="notice notice-error">{error}</div>}
        <div className="analysis-layout">
          <form onSubmit={submit} className="analysis-form">
            <div className="form-step"><span>01</span><h2>Your experience</h2><Icon name="file" size={18}/></div>
            <label htmlFor="resume" className={"upload-zone " + (fileName ? "has-file" : "")}>
              <input id="resume" name="resume" type="file" accept=".pdf,.docx" required disabled={busy} onChange={event => setFileName(event.target.files[0]?.name || "")}/>
              <span className="upload-icon"><Icon name={fileName ? "file" : "upload"} size={25}/></span><strong>{fileName || "Drop your resume here"}</strong><span>{fileName ? "Click to choose a different file" : <>or <u>browse your files</u></>}</span><small>PDF or DOCX · up to 5 MB</small>
            </label>
            <div className="form-step second-step"><span>02</span><h2>The opportunity</h2></div>
            <div className="form-group"><label htmlFor="job-title">Job title</label><input id="job-title" name="job_title" required maxLength={255} placeholder="e.g. Junior backend developer" disabled={busy}/></div>
            <div className="form-group"><label htmlFor="job-description">Job description <span>80+ characters</span></label><textarea id="job-description" name="job_description" required minLength={80} maxLength={12000} rows={6} placeholder="Paste the responsibilities, requirements, and preferred qualifications…" disabled={busy} value={description} onChange={event => setDescription(event.target.value)}/><span className="character-count">{description.length.toLocaleString()} / 12,000</span></div>
            <label className="consent"><input type="checkbox" required disabled={busy}/><span>I agree to send my extracted resume text and this description to Groq for analysis. The original file is discarded; saved text and results can be deleted.</span></label>
            <button disabled={busy} className="button analysis-submit">{busy ? "Working on your report…" : "Find my fit"}{busy ? <span className="spinner"/> : <Icon/>}</button>
            <p className="form-footnote" aria-live="polite">{busy ? "Please keep this page open. This can take up to a minute." : "Text-based resumes only · PDF up to 10 pages · Free-tier limits apply"}</p>
          </form>
          <div className="analysis-output">
            {analysis ? <><AnalysisResults key={analysis.id} analysis={analysis}/><details className="delete-report"><summary>Manage this report</summary><p>Deleting permanently removes the report, extracted resume text, and job description.</p><button disabled={busy} onClick={() => removeAnalysis(analysis.id)}>Delete this report</button></details></> :
              <section className={"report-empty " + (busy ? "is-working" : "")} aria-live="polite">
                <div className="empty-report-art" aria-hidden="true"><div className="empty-document"><span/><span/><i/><i/><i/><div><b/><b/><b/></div></div><div className="empty-lens">↗</div></div>
                <p className="eyebrow">{busy ? "CONNECTING THE DOTS" : "THE OTHER SIDE OF THE SCORE"}</p><h2>{busy ? <>Looking a little<br/><em>closer.</em></> : <>Your story,<br/><em>in perspective.</em></>}</h2>
                <p>{busy ? "We're comparing the role with the evidence in your resume. Your report will appear here when it is ready." : "Add your resume and a role to see where your experience connects, and where a little more evidence would help."}</p>
                <div className="empty-report-legend"><span><i className="status-dot strong"/>What's demonstrated</span><span><i className="status-dot partial"/>What needs context</span><span><i className="status-dot missing"/>What's missing</span></div>
                {!busy && <Link to="/sample" className="text-link">See what a report looks like <Icon size={16}/></Link>}
              </section>}
          </div>
        </div>
        <footer className="workspace-footer"><span>Thoughtful feedback. Grounded in your experience.</span><span>CAREERLENS / YOUR NEXT CHAPTER</span></footer>
      </main>
    </div>
  </div>;
}
