import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { listAll } from "../api/client";
import { Task } from "../api/types";
import Avatar from "../components/Avatar";
import { formatDate, PRIORITY_COLORS } from "../components/TaskCard";
import { useWorkspace } from "../components/WorkspaceContext";

export default function MyTasks() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const { projectName } = useWorkspace();

  useEffect(() => {
    listAll<Task>("/tasks/my/").then(setTasks);
  }, []);

  const pending = tasks.filter((task) => !task.completed_at);
  const done = tasks.filter((task) => task.completed_at);

  function renderRows(list: Task[]) {
    return list.map((task) => (
      <Link key={task.id} className="mytask-row" to={`/projects/${task.project}?task=${task.id}`}>
        <span className={`check-circle ${task.completed_at ? "checked" : ""}`}>✓</span>
        <span className="task-key">{task.key}</span>
        <span className={`mytask-title ${task.completed_at ? "task-done" : ""}`}>{task.title}</span>
        <span
          className="priority-chip"
          style={{ background: PRIORITY_COLORS[task.priority] }}
        >
          {task.priority}
        </span>
        <span className="project-chip">{projectName(task.project)}</span>
        <span className="task-due">{formatDate(task.due_date)}</span>
        <Avatar user={task.assignee} size={22} />
      </Link>
    ));
  }

  return (
    <div className="mytasks-page">
      <h1>Minhas tarefas</h1>
      <div className="widget">
        <div className="widget-title">Pendentes ({pending.length})</div>
        <div className="widget-body">{renderRows(pending)}</div>
      </div>
      <div className="widget">
        <div className="widget-title">Concluídas ({done.length})</div>
        <div className="widget-body">{renderRows(done)}</div>
      </div>
    </div>
  );
}
