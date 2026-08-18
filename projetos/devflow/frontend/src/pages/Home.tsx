import { FormEvent, useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { ApiError, listAll } from "../api/client";
import { Task } from "../api/types";
import { useAuth } from "../auth/AuthContext";
import { projectColor } from "../components/Sidebar";
import { formatDate } from "../components/TaskCard";
import { suggestKey, useWorkspace } from "../components/WorkspaceContext";

type Tab = "upcoming" | "overdue" | "done";

function greeting(): string {
  const hour = new Date().getHours();
  if (hour < 12) return "Bom dia";
  if (hour < 18) return "Boa tarde";
  return "Boa noite";
}

export default function Home() {
  const { user } = useAuth();
  const { projects, projectName, createProject } = useWorkspace();
  const navigate = useNavigate();
  const [myTasks, setMyTasks] = useState<Task[]>([]);
  const [tab, setTab] = useState<Tab>("upcoming");
  const [creating, setCreating] = useState(false);
  const [projectNameInput, setProjectNameInput] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    listAll<Task>("/tasks/my/").then(setMyTasks);
  }, []);

  const today = new Date().toISOString().slice(0, 10);
  const grouped = useMemo(() => {
    const done = myTasks.filter((task) => task.completed_at !== null);
    const overdue = myTasks.filter(
      (task) => !task.completed_at && task.due_date !== null && task.due_date < today,
    );
    const upcoming = myTasks.filter(
      (task) => !task.completed_at && (task.due_date === null || task.due_date >= today),
    );
    return { done, overdue, upcoming };
  }, [myTasks, today]);

  const visible = tab === "done" ? grouped.done : tab === "overdue" ? grouped.overdue : grouped.upcoming;

  const dateLine = new Date().toLocaleDateString("pt-BR", {
    weekday: "long",
    day: "numeric",
    month: "long",
  });

  async function handleCreateProject(event: FormEvent) {
    event.preventDefault();
    if (!projectNameInput.trim()) return;
    try {
      const project = await createProject(projectNameInput.trim(), suggestKey(projectNameInput));
      setCreating(false);
      setProjectNameInput("");
      navigate(`/projects/${project.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.firstMessage() : "Erro ao criar projeto.");
    }
  }

  return (
    <div className="home-page">
      <div className="home-greeting">
        <div className="home-date">{dateLine}</div>
        <h1>
          {greeting()}, {user?.first_name || user?.username}!
        </h1>
      </div>

      <div className="home-grid">
        <section className="widget">
          <div className="widget-title">Minhas tarefas</div>
          <div className="widget-tabs">
            <button className={tab === "upcoming" ? "active" : ""} onClick={() => setTab("upcoming")}>
              Próximas
            </button>
            <button className={tab === "overdue" ? "active" : ""} onClick={() => setTab("overdue")}>
              Atrasadas {grouped.overdue.length > 0 && `(${grouped.overdue.length})`}
            </button>
            <button className={tab === "done" ? "active" : ""} onClick={() => setTab("done")}>
              Concluídas
            </button>
          </div>
          <div className="widget-body">
            {visible.length === 0 && <div className="muted empty-hint">Nenhuma tarefa aqui. 🎉</div>}
            {visible.slice(0, 10).map((task) => (
              <Link
                key={task.id}
                className="mytask-row"
                to={`/projects/${task.project}?task=${task.id}`}
              >
                <span className={`check-circle ${task.completed_at ? "checked" : ""}`}>✓</span>
                <span className="mytask-title">{task.title}</span>
                <span
                  className="project-chip"
                  style={{ background: `${projectColor(task.project)}33` }}
                >
                  {projectName(task.project)}
                </span>
                {task.due_date && <span className="task-due">{formatDate(task.due_date)}</span>}
              </Link>
            ))}
          </div>
        </section>

        <section className="widget">
          <div className="widget-title">Projetos</div>
          <div className="project-grid">
            <button className="project-tile project-tile-new" onClick={() => setCreating(!creating)}>
              <span className="project-tile-icon dashed">+</span>
              Criar projeto
            </button>
            {projects.map((project) => (
              <Link key={project.id} className="project-tile" to={`/projects/${project.id}`}>
                <span className="project-tile-icon" style={{ background: projectColor(project.id) }}>
                  {project.key.slice(0, 2)}
                </span>
                <span>
                  <span className="project-tile-name">{project.name}</span>
                  <span className="muted project-tile-key">{project.key}</span>
                </span>
              </Link>
            ))}
          </div>
          {creating && (
            <form className="inline-form" onSubmit={handleCreateProject}>
              <input
                autoFocus
                placeholder="Nome do projeto"
                value={projectNameInput}
                onChange={(e) => setProjectNameInput(e.target.value)}
              />
              <button className="btn btn-primary">Criar</button>
              {error && <div className="form-error">{error}</div>}
            </form>
          )}
        </section>
      </div>
    </div>
  );
}
