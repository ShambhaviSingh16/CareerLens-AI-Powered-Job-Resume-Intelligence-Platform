import { useNavigate } from "react-router-dom";

function Dashboard() {
  const navigate = useNavigate();

  const handleLogout = () => {
    sessionStorage.removeItem("token");
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white">

      <nav className="border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-8 py-5 flex justify-between items-center">

          <h1 className="text-2xl font-bold">
            Career<span className="text-indigo-400">Lens</span>
          </h1>

          <button
            onClick={handleLogout}
            className="px-4 py-2 rounded-lg border border-slate-700 hover:bg-slate-800 transition"
          >
            Log out
          </button>

        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-8 py-12">

        <h2 className="text-3xl font-bold">
          Welcome to CareerLens
        </h2>

        <p className="text-slate-400 mt-2">
          Your dashboard will appear here.
        </p>

        <div className="mt-10 p-8 rounded-2xl border border-slate-800 bg-slate-900">
          <h3 className="text-xl font-semibold">
            Resume Analysis
          </h3>

          <p className="text-slate-400 mt-2">
            Resume upload and job matching will be added in Phase 6.
          </p>
        </div>

      </main>
    </div>
  );
}

export default Dashboard;