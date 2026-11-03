import { Link } from "react-router-dom";
import { Footer, Icon, PublicNav } from "../components/Brand";
import AnalysisResults from "../components/AnalysisResults";
import { sample } from "../data/sample";
export default function Sample() {
  return <div className="sample-page"><PublicNav/><main className="sample-main container">
    <div className="sample-heading"><div><p className="eyebrow">THE CAREERLENS REPORT / AN EXAMPLE</p><h1>More than<br/><em>a percentage.</em></h1></div><div><p>See the connection between experience and opportunity. Explore the evidence, suggested edits, and document checks below.</p><span className="sample-stamp">FICTIONAL DATA · ILLUSTRATIVE ASSESSMENTS</span></div></div>
    <AnalysisResults analysis={sample}/>
    <div className="sample-cta"><div><h2>Now, let's look at your story.</h2><p>This hand-authored example is not a live AI result and is not saved to your account.</p></div><Link to="/dashboard" className="button">Analyze my resume <Icon/></Link></div>
  </main><Footer/></div>;
}
