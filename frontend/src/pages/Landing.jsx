import { Link } from "react-router-dom";

function Landing() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      
      <nav className="flex items-center justify-between px-8 py-6 max-w-7xl mx-auto">
        <h1 className="text-2xl font-bold">
          Career<span className="text-indigo-400">Lens</span>
        </h1>

        <div className="flex gap-4">
          <Link
            to="/login"
            className="px-5 py-2 rounded-lg border border-slate-700 hover:bg-slate-800 transition"
          >
            Log In
          </Link>

          <Link
            to="/signup"
            className="px-5 py-2 rounded-lg bg-indigo-500 hover:bg-indigo-600 transition"
          >
            Sign Up
          </Link>
        </div>
      </nav>

      <main className="max-w-5xl mx-auto px-8 pt-28 text-center">
        <p className="text-indigo-400 font-medium mb-4">
          AI-Powered Career Analysis
        </p>

        <h2 className="text-5xl md:text-6xl font-bold leading-tight">
          Know how well your resume
          <span className="text-indigo-400"> matches the job.</span>
        </h2>

        <p className="mt-6 text-lg text-slate-400 max-w-2xl mx-auto">
          Upload your resume and a job description. CareerLens analyzes
          your match, identifies missing skills, and shows you exactly
          what you can improve before applying.
        </p>

        <div className="mt-10 flex justify-center gap-4">
          <Link
            to="/signup"
            className="px-7 py-3 rounded-lg bg-indigo-500 hover:bg-indigo-600 font-medium transition"
          >
            Get Started
          </Link>

          <Link
            to="/login"
            className="px-7 py-3 rounded-lg border border-slate-700 hover:bg-slate-800 transition"
          >
            Log In
          </Link>
        </div>
      </main>
    </div>
  );
}

export default Landing;