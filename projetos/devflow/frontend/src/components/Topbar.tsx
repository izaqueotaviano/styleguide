import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import { api } from "../api/client";
import { Notification, Paginated, Task } from "../api/types";
import Avatar from "./Avatar";
import { useWorkspace } from "./WorkspaceContext";

const NOTIF_LABELS: Record<Notification["verb"], string> = {
  task_assigned: "atribuiu uma tarefa a você",
  review_requested: "pediu sua revisão",
  mentioned: "mencionou você",
  commented: "comentou em uma tarefa sua",
};

function Bell() {
  const [unread, setUnread] = useState(0);
  const [items, setItems] = useState<Notification[]>([]);
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();

  const refreshCount = useCallback(() => {
    api
      .get<Paginated<Notification>>("/notifications/?unread=1&page_size=1")
      .then((page) => setUnread(page.count))
      .catch(() => undefined);
  }, []);

  useEffect(() => {
    refreshCount();
    const id = window.setInterval(refreshCount, 30000);
    return () => window.clearInterval(id);
  }, [refreshCount]);

  async function toggle() {
    if (!open) {
      const page = await api.get<Paginated<Notification>>("/notifications/?page_size=15");
      setItems(page.results);
    }
    setOpen(!open);
  }

  async function openNotification(item: Notification) {
    if (!item.read_at) {
      api.post(`/notifications/${item.id}/read/`).catch(() => undefined);
      setUnread((count) => Math.max(0, count - 1));
    }
    setOpen(false);
    if (item.task_project && item.task) {
      navigate(`/projects/${item.task_project}?task=${item.task}`);
    }
  }

  async function markAll() {
    await api.post("/notifications/read-all/");
    setUnread(0);
    setItems(items.map((item) => ({ ...item, read_at: item.read_at ?? new Date().toISOString() })));
  }

  return (
    <div className="bell-wrap">
      <button className="bell-btn" title="Notificações" onClick={toggle}>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9" />
          <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0" />
        </svg>
        {unread > 0 && <span className="badge">{unread > 9 ? "9+" : unread}</span>}
      </button>
      {open && (
        <div className="notif-dropdown">
          <div className="notif-header">
            <strong>Notificações</strong>
            {unread > 0 && (
              <button className="btn-link" onClick={markAll}>
                Marcar todas como lidas
              </button>
            )}
          </div>
          {items.length === 0 && <div className="muted notif-empty">Nenhuma notificação.</div>}
          {items.map((item) => (
            <button
              key={item.id}
              className={`notif-item ${item.read_at ? "" : "notif-unread"}`}
              onClick={() => openNotification(item)}
            >
              <Avatar user={item.actor} size={28} />
              <span className="notif-text">
                <span>
                  <strong>{item.actor?.username ?? "Alguém"}</strong> {NOTIF_LABELS[item.verb]}
                </span>
                {item.task_title && (
                  <span className="muted notif-task">
                    {item.task_key} · {item.task_title}
                  </span>
                )}
              </span>
              {!item.read_at && <span className="unread-dot" />}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default function Topbar() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Task[]>([]);
  const [open, setOpen] = useState(false);
  const { projectName } = useWorkspace();
  const navigate = useNavigate();
  const timer = useRef<number>();

  useEffect(() => {
    window.clearTimeout(timer.current);
    if (query.trim().length < 2) {
      setResults([]);
      setOpen(false);
      return;
    }
    timer.current = window.setTimeout(async () => {
      try {
        const page = await api.get<Paginated<Task>>(
          `/tasks/?search=${encodeURIComponent(query.trim())}&page_size=8`,
        );
        setResults(page.results);
        setOpen(true);
      } catch {
        setResults([]);
      }
    }, 300);
    return () => window.clearTimeout(timer.current);
  }, [query]);

  function openTask(task: Task) {
    setOpen(false);
    setQuery("");
    navigate(`/projects/${task.project}?task=${task.id}`);
  }

  return (
    <header className="topbar">
      <div className="search-wrap">
        <input
          className="search-input"
          placeholder="Buscar tarefas…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onBlur={() => window.setTimeout(() => setOpen(false), 150)}
          onFocus={() => results.length > 0 && setOpen(true)}
        />
        {open && results.length > 0 && (
          <div className="search-results">
            {results.map((task) => (
              <button key={task.id} className="search-result" onMouseDown={() => openTask(task)}>
                <span className="task-key">{task.key}</span>
                <span className="search-result-title">{task.title}</span>
                <span className="search-result-project">{projectName(task.project)}</span>
              </button>
            ))}
          </div>
        )}
      </div>
      <Bell />
    </header>
  );
}
