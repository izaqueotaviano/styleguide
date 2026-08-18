import { FormEvent, useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";

import { ApiError } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import { suggestKey, useWorkspace } from "./WorkspaceContext";

const PROJECT_COLORS = ["#f06a6a", "#ec8d71", "#f1bd6c", "#aecf55", "#4ecbc4", "#8d84e8", "#f9aaef", "#5da283"];

export function projectColor(id: string): string {
  let hash = 0;
  for (const char of id) hash = (hash * 31 + char.charCodeAt(0)) >>> 0;
  return PROJECT_COLORS[hash % PROJECT_COLORS.length];
}

export default function Sidebar() {
  const { workspace, projects, createProject } = useWorkspace();
  const { signOut, user } = useAuth();
  const navigate = useNavigate();
  const [creating, setCreating] = useState(false);
  const [name, setName] = useState("");
  const [error, setError] = useState("");

  async function handleCreate(event: FormEvent) {
    event.preventDefault();
    if (!name.trim()) return;
    try {
      const project = await createProject(name.trim(), suggestKey(name));
      setName("");
      setCreating(false);
      setError("");
      navigate(`/projects/${project.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.firstMessage() : "Erro ao criar projeto.");
    }
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-section">
        <NavLink to="/" end className="sidebar-link">
          <span className="sidebar-icon">⌂</span> Página inicial
        </NavLink>
        <NavLink to="/my-tasks" className="sidebar-link">
          <span className="sidebar-icon">✓</span> Minhas tarefas
        </NavLink>
      </div>

      <div className="sidebar-section">
        <div className="sidebar-heading">
          <span>{workspace ? workspace.name : "Projetos"}</span>
          <button
            className="sidebar-plus"
            title="Criar projeto"
            onClick={() => setCreating((value) => !value)}
          >
            +
          </button>
        </div>
        {creating && (
          <form className="sidebar-new-project" onSubmit={handleCreate}>
            <input
              autoFocus
              placeholder="Nome do projeto"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
            {error && <div className="form-error">{error}</div>}
          </form>
        )}
        {projects.map((project) => (
          <NavLink key={project.id} to={`/projects/${project.id}`} className="sidebar-link">
            <span className="project-dot" style={{ background: projectColor(project.id) }} />
            <span className="sidebar-project-name">{project.name}</span>
          </NavLink>
        ))}
      </div>

      <div className="sidebar-footer">
        <span className="sidebar-user">{user?.username}</span>
        <button className="btn-link" onClick={signOut}>
          Sair
        </button>
      </div>
    </aside>
  );
}
