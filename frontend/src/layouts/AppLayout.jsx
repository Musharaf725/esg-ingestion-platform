import { NavLink, Outlet } from "react-router-dom";
import useTenant from "../hooks/useTenant";

const navItems = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/upload", label: "Upload" },
  { to: "/review", label: "Review" },
];

export default function AppLayout() {
  const { tenant, setTenant } = useTenant();

  return (
    <div className="min-h-screen text-slate-100">
      <div className="mx-auto grid max-w-[1500px] grid-cols-1 gap-5 px-4 pb-8 pt-6 lg:grid-cols-[240px_1fr]">
        <aside className="glass-panel h-fit p-4 lg:sticky lg:top-6">
          <div className="mb-6">
            <p className="font-heading text-xl font-semibold tracking-tight text-white">ESG Ops Console</p>
            <p className="mt-1 text-xs text-slate-400">Analyst review and sign-off</p>
          </div>

          <nav className="space-y-2">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `block rounded-xl px-3 py-2 text-sm transition ${
                    isActive
                      ? "bg-ops-700/40 text-white"
                      : "text-slate-300 hover:bg-slate-800/70 hover:text-white"
                  }`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>

          <div className="mt-6 border-t border-slate-700/60 pt-4">
            <label className="mb-1 block text-xs uppercase tracking-wide text-slate-400">Tenant</label>
            <input
              value={tenant}
              onChange={(e) => setTenant(e.target.value)}
              className="w-full rounded-lg border border-slate-600 bg-slate-950 px-3 py-2 text-sm outline-none ring-0 transition focus:border-ops-400"
              placeholder="e.g. demo-org"
            />
          </div>
        </aside>

        <main className="space-y-6">
          <header className="glass-panel flex flex-col gap-2 p-5 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="font-heading text-2xl font-semibold">ESG Ingestion & Review</h1>
              <p className="text-sm text-slate-300">Operational dashboard for analyst-level data quality and audit readiness.</p>
            </div>
            <div className="rounded-lg border border-ops-500/30 bg-ops-500/10 px-3 py-2 text-xs text-ops-100">
              Tenant Context: <span className="font-semibold">{tenant}</span>
            </div>
          </header>

          <Outlet />
        </main>
      </div>
    </div>
  );
}
