import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import api, { errorMessage } from "../api/client";
import Brand, { Icon } from "./Brand";

export default function AuthPage({ signup = false }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  async function submit(event) {
    event.preventDefault();
    setError(""); setLoading(true);
    try {
      const { data } = await api.post(signup ? "/auth/register" : "/auth/login", { email, password });
      if (signup) navigate("/login", { state: { registered: true } });
      else { sessionStorage.setItem("token", data.access_token); navigate("/dashboard"); }
    } catch (err) { setError(errorMessage(err)); }
    finally { setLoading(false); }
  }
  return <main className="auth-page">
    <aside className="auth-story"><Brand/><div><p className="eyebrow">A DIFFERENT KIND OF SECOND OPINION</p><h2>There's more<br/>to your story.<br/><em>Let it show.</em></h2><p>Your next opportunity deserves a resume that makes the connection clear.</p><Link to="/sample" className="text-link">Explore a sample report <Icon size={17}/></Link></div><span className="eyebrow">CAREERLENS / A CLEARER NEXT CHAPTER</span><div className="auth-circles" aria-hidden="true"><i/><i/><i/></div></aside>
    <section className="auth-form-side">
      <Link to="/" className="back-link">← Back to CareerLens</Link>
      <div className="auth-form-wrap"><p className="eyebrow">{signup ? "LET'S GET YOU STARTED" : "YOUR WORKSPACE AWAITS"}</p><h1>{signup ? "A fresh perspective." : "Good to see you."}</h1><p className="muted">{signup ? "Create an account to analyze your fit and keep your reports in one place." : "Pick up where you left off. Your next chapter is waiting."}</p>
        <form onSubmit={submit} className="auth-form">
          {!signup && location.state?.registered && <p role="status" className="notice">Your account is ready. Log in to enter your workspace.</p>}
          {error && <div role="alert" className="notice notice-error">{error}</div>}
          <div className="form-group"><label htmlFor="email">Email address</label><input id="email" type="email" autoComplete="email" required value={email} onChange={e => setEmail(e.target.value)} placeholder="you@example.com" disabled={loading}/></div>
          <div className="form-group"><label htmlFor="password">Password</label><div className="password-field"><input id="password" type={showPassword ? "text" : "password"} autoComplete={signup ? "new-password" : "current-password"} minLength={8} maxLength={128} required value={password} onChange={e => setPassword(e.target.value)} placeholder={signup ? "At least 8 characters" : "Your password"} disabled={loading}/><button type="button" aria-label={showPassword ? "Hide password" : "Show password"} aria-pressed={showPassword} onClick={() => setShowPassword(!showPassword)}><Icon name="eye" size={19}/></button></div></div>
          <button className="button" disabled={loading}>{loading ? "One moment…" : signup ? "Create my account" : "Enter my workspace"}<Icon size={18}/></button>
        </form>
        <p className="auth-switch">{signup ? "Already have an account?" : "New to CareerLens?"} <Link to={signup ? "/login" : "/signup"}>{signup ? "Log in" : "Create an account"} ↗</Link></p>
        <div className="auth-divider"><span>just looking around?</span></div><Link to="/sample" className="button button-outline">Explore the sample report <Icon size={16}/></Link>
      </div>
      <p className="auth-footnote">A thoughtful next step. No payment required.</p>
    </section>
  </main>;
}
