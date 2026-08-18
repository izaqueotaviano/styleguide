import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import { api } from "../api/client";
import { Paginated, Task } from "../api/types";
import { useWorkspace } from "./WorkspaceContext";

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
    </header>
  );
}
