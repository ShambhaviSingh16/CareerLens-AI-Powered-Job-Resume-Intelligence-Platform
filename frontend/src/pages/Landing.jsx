import { useState } from "react";
import { Link } from "react-router-dom";
import { Footer, Icon, PublicNav } from "../components/Brand";

const annotations = [
  { title: "Python API development", status: "strong", label: "Evidence found", text: "Your FastAPI project demonstrates the API development this role asks for.", quote: "Built a Python FastAPI service for a college library." },
  { title: "SQL query optimization", status: "partial", label: "Needs more evidence", text: "Using SQLite is relevant. The resume does not yet demonstrate query optimization.", quote: "Used SQLite to store books and borrowers." },
  { title: "Automated testing", status: "missing", label: "Not demonstrated", text: "This role asks for automated tests. There is no supporting evidence in this resume.", quote: "No supporting passage found." },
];

function ResumePreview() {
  const [active, setActive] = useState(0);
  const item = annotations[active];
  return <div className="hero-visual">
    <div className="visual-caption"><span className="tiny-dot"/> A closer look at your experience <span>0{active + 1} / 03</span></div>
    <div className="resume-sheet">
      <div className="resume-topline"><span>THE RESUME</span><Icon name="file" size={16}/></div>
      <h3>Alex Morgan</h3><p className="resume-role">Junior backend developer</p>
      <div className="resume-rule"/>
      <p className="resume-section">PROJECTS & EXPERIENCE</p>
      <h4>Library management service</h4>
      <button onClick={() => setActive(0)} className={"resume-highlight " + (active === 0 ? "selected" : "")}>Built a Python FastAPI service for a college library.<span>01</span></button>
      <button onClick={() => setActive(1)} className={"resume-highlight amber " + (active === 1 ? "selected" : "")}>Used SQLite to store books and borrowers.<span>02</span></button>
      <div className="resume-lines"><i/><i/><i/></div>
      <p className="resume-section">SKILLS</p><div className="resume-tags"><span>Python</span><span>FastAPI</span><span>SQL</span></div>
      <div className="resume-bottom">EXAMPLE RESUME <span>1 / 1</span></div>
    </div>
    <div className={"annotation annotation-" + item.status} aria-live="polite">
      <div className="annotation-label"><span className={"status-dot " + item.status}/>{item.label}<span className="annotation-index">0{active + 1}</span></div>
      <h4>{item.title}</h4><p>{item.text}</p>
      <div className="annotation-tabs" aria-label="Explore example matches">{annotations.map((_, index) => <button key={index} aria-label={"Show example " + (index + 1)} aria-pressed={active === index} onClick={() => setActive(index)} className={active === index ? "active" : ""}/>)}</div>
    </div>
    <p className="visual-note">Illustrative resume & assessments. Try a highlight.</p>
  </div>;
}

export default function Landing() {
  return <div className="marketing-page">
    <PublicNav/>
    <main>
      <section className="hero container">
        <div className="hero-copy">
          <div className="eyebrow"><span className="tiny-dot"/> RESUME INTELLIGENCE, WITH CONTEXT</div>
          <h1>Your experience.<br/>Seen <em>clearly.</em></h1>
          <p className="hero-description">You bring more than a list of keywords.<br className="desktop-break"/> Find out what your resume actually says about your fit for the role, and what it could say better.</p>
          <div className="hero-actions"><Link to="/signup" className="button">Find my fit <Icon/></Link><Link to="/sample" className="text-link">Take a look inside <span>↗</span></Link></div>
          <p className="hero-fineprint"><span className="small-check">✓</span> Free to try <span>·</span> PDF & Word <span>·</span> Evidence behind every match</p>
        </div>
        <ResumePreview/>
      </section>
      <section className="principle-strip"><div className="container"><span className="eyebrow">LESS GUESSWORK.<br/>MORE PERSPECTIVE.</span><p>A match score is a starting point.<br/><strong>The useful part is knowing why.</strong></p><div className="strip-symbol" aria-hidden="true">↗</div></div></section>
      <section className="how-section container" id="how-it-works">
        <div className="section-intro"><div><p className="eyebrow">FROM APPLICATION TO UNDERSTANDING</p><h2>A second look.<br/>A clearer next move.</h2></div><p>No guessing which keywords to squeeze in. Start with what you have actually done, and see how it connects to the opportunity.</p></div>
        <div className="process-grid">
          {[["01", "Bring the two sides.", "Your resume and the job description. Upload a PDF or Word document, then paste the role you have in mind.", "file"], ["02", "Connect the evidence.", "See strong matches, related experience, and missing requirements, with the passages behind each assessment.", "eye"], ["03", "Make your next edit count.", "Get suggested wording rooted in your experience. Review the gaps and decide what deserves a clearer place on the page.", "arrow"]].map(([number, title, description, icon]) => <article key={number}><div className="process-top"><span>{number}</span><Icon name={icon}/></div><h3>{title}</h3><p>{description}</p></article>)}
        </div>
      </section>
      <section className="closing-section container"><div className="eyebrow">YOUR NEXT CHAPTER STARTS HERE</div><h2>Apply with a little<br/><em>more perspective.</em></h2><Link to="/signup" className="button">Look at my resume <Icon/></Link><Link to="/sample" className="text-link">Or explore a sample report ↗</Link></section>
    </main>
    <Footer/>
  </div>;
}
