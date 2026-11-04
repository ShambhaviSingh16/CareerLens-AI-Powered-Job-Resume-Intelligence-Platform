import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Brand, { Icon } from "../components/Brand";
import api, { errorMessage } from "../api/client";

export default function Settings() {
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const navigate = useNavigate();
  async function remove(event) {
    event.preventDefault();
    setBusy(true); setError("");
    try {
      await api.delete("/auth/me", { data: { password } });
      sessionStorage.removeItem("token");
      navigate("/", { replace: true });
    } catch (err) { setError(errorMessage(err)); }
    finally { setBusy(false); }
  }
  return <main className="settings-page container"><Brand/><Link to="/dashboard" className="back-link">Back to workspace</Link><section className="settings-content"><p className="eyebrow">YOUR ACCOUNT & DATA</p><h1>You control what stays.</h1><p className="muted">You can delete individual reports in your workspace. Account deletion removes your account, saved reports, stored resume text, job descriptions, and quota records from CareerLens. It does not control data already processed by the AI provider.</p><form onSubmit={remove} className="auth-form"><h2>Delete your account</h2>{error && <p role="alert" className="notice notice-error">{error}</p>}<div className="form-group"><label htmlFor="delete-password">Confirm your password</label><input id="delete-password" type="password" autoComplete="current-password" required minLength={8} maxLength={128} value={password} onChange={event => setPassword(event.target.value)} disabled={busy}/></div><label className="consent"><input type="checkbox" required disabled={busy}/><span>I understand that this permanently deletes my account and all CareerLens data associated with it.</span></label><button className="button" disabled={busy}>{busy ? "Deleting account…" : "Permanently delete my account"}<Icon size={17}/></button></form></section></main>;
}
