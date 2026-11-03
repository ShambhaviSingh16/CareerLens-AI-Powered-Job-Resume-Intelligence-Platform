import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import api, { errorMessage } from "../api/client";

export default function RequireAuth({ children }) {
  const [status, setStatus] = useState("loading");
  const [error, setError] = useState("");
  const token = sessionStorage.getItem("token");
  useEffect(() => {
    if (!token) return;
    const controller = new AbortController();
    api.get("/auth/me", { signal: controller.signal }).then(() => {
      setStatus("ready");
    }).catch((err) => {
      if (err.code !== "ERR_CANCELED") {
        setError(errorMessage(err));
        setStatus("error");
      }
    });
    return () => controller.abort();
  }, [token]);
  if (!token) return <Navigate to="/login" replace />;
  if (status === "ready") return children;
  return <main className="session-check" aria-live="polite">
    {status === "loading" ? "Checking your session…" : <>
      <p role="alert">{error}</p>
      <button className="mt-4 underline" onClick={() => window.location.reload()}>Try again</button>
    </>}
  </main>;
}
