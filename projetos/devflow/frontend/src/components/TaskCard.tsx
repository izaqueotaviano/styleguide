import { Task } from "../api/types";
import Avatar from "./Avatar";

export const PRIORITY_COLORS: Record<Task["priority"], string> = {
  urgent: "#d1395b",
  high: "#ec8d71",
  medium: "#f1bd6c",
  low: "#aecf55",
};

export function formatDate(iso: string | null): string {
  if (!iso) return "";
  const [year, month, day] = iso.split("-").map(Number);
  return new Date(year, month - 1, day).toLocaleDateString("pt-BR", {
    day: "numeric",
    month: "short",
  });
}

export default function TaskCard({
  task,
  onOpen,
  onDragStart,
  onDropBefore,
}: {
  task: Task;
  onOpen: () => void;
  onDragStart: (event: React.DragEvent) => void;
  onDropBefore?: (event: React.DragEvent) => void;
}) {
  const done = task.completed_at !== null;
  return (
    <div
      className="task-card"
      draggable
      onDragStart={onDragStart}
      onClick={onOpen}
      onDragOver={(e) => e.preventDefault()}
      onDrop={onDropBefore}
    >
      <div className={`task-card-title ${done ? "task-done" : ""}`}>
        <span className={`check-circle ${done ? "checked" : ""}`}>✓</span>
        {task.title}
      </div>
      {task.labels.length > 0 && (
        <div className="labels-row">
          {task.labels.slice(0, 3).map((label) => (
            <span
              key={label.id}
              className="label-chip"
              style={{ background: `${label.color}26`, color: label.color }}
            >
              {label.name}
            </span>
          ))}
        </div>
      )}
      <div className="task-card-footer">
        <Avatar user={task.assignee} size={22} />
        <span className="task-key">{task.key}</span>
        <span
          className="priority-dot"
          title={`Prioridade: ${task.priority}`}
          style={{ background: PRIORITY_COLORS[task.priority] }}
        />
        {task.due_date && <span className="task-due">{formatDate(task.due_date)}</span>}
        {task.subtasks_count > 0 && (
          <span className="subtask-count">⑃ {task.subtasks_count}</span>
        )}
      </div>
    </div>
  );
}
