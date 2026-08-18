import { FormEvent, useState } from "react";
import { Outlet } from "react-router-dom";

import Sidebar from "./Sidebar";
import Topbar from "./Topbar";
import { useWorkspace, WorkspaceProvider } from "./WorkspaceContext";

function WorkspaceGate() {
  const { workspace, loading, createWorkspace } = useWorkspace();
  const [name, setName] = useState("");
  const [busy, setBusy] = useState(false);

  if (loading) return <div className="screen-center">Carregando…</div>;

  if (!workspace) {
    async function handleSubmit(event: FormEvent) {
      event.preventDefault();
      setBusy(true);
      try {
        await createWorkspace(name.trim() || "Meu Workspace");
      } finally {
        setBusy(false);
      }
    }
    return (
      <div className="screen-center">
        <form className="login-card" onSubmit={handleSubmit}>
          <div className="login-logo">DevFlow</div>
          <p className="login-subtitle">Crie seu workspace para começar</p>
          <label>
            Nome do workspace
            <input value={name} onChange={(e) => setName(e.target.value)} autoFocus />
          </label>
          <button className="btn btn-primary" disabled={busy}>
            {busy ? "Criando…" : "Criar workspace"}
          </button>
        </form>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <Sidebar />
      <div className="app-main">
        <Topbar />
        <main className="app-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default function Layout() {
  return (
    <WorkspaceProvider>
      <WorkspaceGate />
    </WorkspaceProvider>
  );
}
