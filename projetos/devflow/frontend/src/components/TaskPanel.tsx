import { FormEvent, useEffect, useState } from "react";

import { api, listAll } from "../api/client";
import {
  Activity,
  Comment,
  Label,
  PRIORITY_LABELS,
  Section,
  Task,
  TaskStatus,
  TYPE_LABELS,
} from "../api/types";
import { useWorkspace } from "./WorkspaceContext";
import Avatar from "./Avatar";
import { formatDate } from "./TaskCard";

const ACTIVITY_VERBS: Record<Activity["verb"], string> = {
  created: "criou a tarefa",
  updated: "atualizou",
  status_changed: "alterou o status",
  section_changed: "moveu de seção",
  assigned: "alterou o responsável",
  commented: "comentou",
  deleted: "excluiu a tarefa",
};

const FIELD_LABELS: Record<string, string> = {
  title: "o título",
  description: "a descrição",
  type: "o tipo",
  priority: "a prioridade",
  estimate: "a estimativa",
  due_date: "a entrega",
  reviewer: "o revisor",
  parent: "a tarefa pai",
};

function valueLabel(value: unknown): string {
  if (value === null || value === undefined || value === "") return "—";
  if (typeof value === "object") {
    const record = value as { label?: string; id?: string };
    return record.label ?? String(record.id ?? "—");
  }
  return String(value);
}

interface TaskPanelProps {
  taskId: string;
  statuses: TaskStatus[];
  sections: Section[];
  onClose: () => void;
  onChanged: (task: Task) => void;
}

export default function TaskPanel({ taskId, statuses, sections, onClose, onChanged }: TaskPanelProps) {
  const { members, workspace, projects } = useWorkspace();
  const [task, setTask] = useState<Task | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [activities, setActivities] = useState<Activity[]>([]);
  const [tab, setTab] = useState<"comments" | "activity">("comments");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [newSubtask, setNewSubtask] = useState("");
  const [newComment, setNewComment] = useState("");
  const [estimate, setEstimate] = useState("");
  const [allLabels, setAllLabels] = useState<Label[]>([]);
  const [labelsOpen, setLabelsOpen] = useState(false);
  const [newLabel, setNewLabel] = useState("");

  useEffect(() => {
    setTask(null);
    setTab("comments");
    api.get<Task>(`/tasks/${taskId}/`).then((data) => {
      setTask(data);
      setTitle(data.title);
      setDescription(data.description);
      setEstimate(data.estimate ?? "");
    });
    listAll<Comment>(`/comments/?task=${taskId}`).then(setComments);
  }, [taskId]);

  useEffect(() => {
    if (workspace) {
      listAll<Label>(`/labels/?workspace=${workspace.id}`).then(setAllLabels);
    }
  }, [workspace]);

  useEffect(() => {
    if (tab === "activity") {
      listAll<Activity>(`/activities/?task=${taskId}`).then(setActivities);
    }
  }, [tab, taskId]);

  if (!task) {
    return (
      <div className="task-panel">
        <div className="task-panel-loading">Carregando…</div>
      </div>
    );
  }

  async function patch(changes: Record<string, unknown>) {
    const updated = await api.patch<Task>(`/tasks/${task!.id}/`, changes);
    setTask({ ...updated, subtasks: task!.subtasks });
    onChanged(updated);
  }

  const doneStatus = statuses.find((status) => status.category === "completed");
  const isDone = task.completed_at !== null;

  async function toggleDone() {
    if (!doneStatus) return;
    const target = isDone
      ? statuses.find((status) => status.category !== "completed" && status.category !== "canceled")
      : doneStatus;
    if (target) await patch({ status: target.id });
  }

  async function addSubtask(event: FormEvent) {
    event.preventDefault();
    if (!newSubtask.trim()) return;
    const subtask = await api.post<Task>("/tasks/", {
      project: task!.project,
      title: newSubtask.trim(),
      parent: task!.id,
    });
    setTask({ ...task!, subtasks: [...(task!.subtasks ?? []), subtask] });
    setNewSubtask("");
  }

  async function toggleSubtask(subtask: Task) {
    if (!doneStatus) return;
    const target = subtask.completed_at
      ? statuses.find((status) => status.category !== "completed" && status.category !== "canceled")
      : doneStatus;
    if (!target) return;
    const updated = await api.post<Task>(`/tasks/${subtask.id}/move/`, { status: target.id });
    setTask({
      ...task!,
      subtasks: (task!.subtasks ?? []).map((item) => (item.id === updated.id ? updated : item)),
    });
  }

  async function toggleLabel(label: Label) {
    const current = task!.labels.map((item) => item.id);
    const next = current.includes(label.id)
      ? current.filter((id) => id !== label.id)
      : [...current, label.id];
    await patch({ labels: next });
  }

  async function createLabel(event: FormEvent) {
    event.preventDefault();
    if (!newLabel.trim() || !workspace) return;
    const palette = ["#8D84E8", "#4ECBC4", "#F1BD6C", "#AECF55", "#F06A6A", "#5DA283"];
    const label = await api.post<Label>("/labels/", {
      workspace: workspace.id,
      name: newLabel.trim(),
      color: palette[allLabels.length % palette.length],
    });
    setAllLabels([...allLabels, label]);
    setNewLabel("");
    await toggleLabel(label);
  }

  async function addComment(event: FormEvent) {
    event.preventDefault();
    if (!newComment.trim()) return;
    const comment = await api.post<Comment>("/comments/", {
      task: task!.id,
      body: newComment.trim(),
    });
    setComments([...comments, comment]);
    setNewComment("");
  }

  return (
    <div className="task-panel">
      <div className="task-panel-header">
        <button className={`btn btn-done ${isDone ? "is-done" : ""}`} onClick={toggleDone}>
          ✓ {isDone ? "Concluída" : "Marcar como concluída"}
        </button>
        <span className="task-key">{task.key}</span>
        <button className="icon-btn" title="Fechar" onClick={onClose}>
          ✕
        </button>
      </div>

      <input
        className="task-panel-title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        onBlur={() => title.trim() && title !== task.title && patch({ title: title.trim() })}
      />

      <div className="field-grid">
        <label>Responsável</label>
        <select
          value={task.assignee?.id ?? ""}
          onChange={(e) => patch({ assignee: e.target.value ? Number(e.target.value) : null })}
        >
          <option value="">Nenhum responsável</option>
          {members.map((member) => (
            <option key={member.user.id} value={member.user.id}>
              {member.user.first_name
                ? `${member.user.first_name} ${member.user.last_name}`.trim()
                : member.user.username}
            </option>
          ))}
        </select>

        <label>Data de conclusão</label>
        <input
          type="date"
          value={task.due_date ?? ""}
          onChange={(e) => patch({ due_date: e.target.value || null })}
        />

        <label>Status</label>
        <select value={task.status?.id ?? ""} onChange={(e) => patch({ status: e.target.value })}>
          {statuses.map((status) => (
            <option key={status.id} value={status.id}>
              {status.name}
            </option>
          ))}
        </select>

        <label>Seção</label>
        <select
          value={task.section?.id ?? ""}
          onChange={(e) => patch({ section: e.target.value || null })}
        >
          <option value="">Sem seção</option>
          {sections.map((section) => (
            <option key={section.id} value={section.id}>
              {section.name}
            </option>
          ))}
        </select>

        <label>Prioridade</label>
        <select value={task.priority} onChange={(e) => patch({ priority: e.target.value })}>
          {Object.entries(PRIORITY_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>

        <label>Tipo</label>
        <select value={task.type} onChange={(e) => patch({ type: e.target.value })}>
          {Object.entries(TYPE_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>

        <label>Estimativa</label>
        <span className="estimate-wrap">
          <input
            type="number"
            min="0"
            step="0.5"
            placeholder="—"
            value={estimate}
            onChange={(e) => setEstimate(e.target.value)}
            onBlur={() =>
              (estimate || null) !== (task.estimate ?? null) &&
              patch({ estimate: estimate === "" ? null : estimate })
            }
          />
          <span className="muted">
            {projects.find((item) => item.id === task.project)?.estimate_unit === "hours"
              ? "horas"
              : "pontos"}
          </span>
        </span>
      </div>

      <div className="panel-section">
        <div className="panel-section-title">Labels</div>
        <div className="labels-row panel-labels">
          {task.labels.map((label) => (
            <button
              key={label.id}
              className="label-chip label-chip-btn"
              style={{ background: `${label.color}26`, color: label.color }}
              title="Remover label"
              onClick={() => toggleLabel(label)}
            >
              {label.name} ✕
            </button>
          ))}
          <button className="label-add-btn" onClick={() => setLabelsOpen(!labelsOpen)}>
            + Label
          </button>
        </div>
        {labelsOpen && (
          <div className="labels-picker">
            {allLabels.map((label) => {
              const active = task.labels.some((item) => item.id === label.id);
              return (
                <button
                  key={label.id}
                  className={`labels-picker-item ${active ? "active" : ""}`}
                  onClick={() => toggleLabel(label)}
                >
                  <span className="project-dot" style={{ background: label.color }} />
                  {label.name}
                  {active && <span className="muted"> ✓</span>}
                </button>
              );
            })}
            <form onSubmit={createLabel}>
              <input
                className="ghost-input"
                placeholder="Criar nova label…"
                value={newLabel}
                onChange={(e) => setNewLabel(e.target.value)}
              />
            </form>
          </div>
        )}
      </div>

      <div className="panel-section">
        <div className="panel-section-title">Descrição</div>
        <textarea
          placeholder="Do que se trata esta tarefa?"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          onBlur={() => description !== task.description && patch({ description })}
        />
      </div>

      {task.parent === null && (
        <div className="panel-section">
          <div className="panel-section-title">
            Subtarefas{" "}
            {task.subtasks && task.subtasks.length > 0 && (
              <span className="muted">
                {task.subtasks.filter((item) => item.completed_at).length}/{task.subtasks.length}
              </span>
            )}
          </div>
          {(task.subtasks ?? []).map((subtask) => (
            <div key={subtask.id} className="subtask-row">
              <button
                className={`check-circle ${subtask.completed_at ? "checked" : ""}`}
                onClick={() => toggleSubtask(subtask)}
              >
                ✓
              </button>
              <span className={subtask.completed_at ? "task-done" : ""}>{subtask.title}</span>
            </div>
          ))}
          <form onSubmit={addSubtask}>
            <input
              className="ghost-input"
              placeholder="Adicionar subtarefa"
              value={newSubtask}
              onChange={(e) => setNewSubtask(e.target.value)}
            />
          </form>
        </div>
      )}

      <div className="panel-section">
        <div className="panel-tabs">
          <button className={tab === "comments" ? "active" : ""} onClick={() => setTab("comments")}>
            Comentários
          </button>
          <button className={tab === "activity" ? "active" : ""} onClick={() => setTab("activity")}>
            Atividade
          </button>
        </div>

        {tab === "comments" ? (
          <>
            {comments.map((comment) => (
              <div key={comment.id} className="comment">
                <Avatar user={comment.author} size={26} />
                <div>
                  <div className="comment-meta">
                    <strong>{comment.author?.username ?? "—"}</strong>
                    <span className="muted">
                      {new Date(comment.created_at).toLocaleDateString("pt-BR")}
                    </span>
                  </div>
                  <div className="comment-body">{comment.body}</div>
                </div>
              </div>
            ))}
            <form onSubmit={addComment} className="comment-form">
              <input
                placeholder="Adicionar um comentário (use @usuario para mencionar)"
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
              />
              <button className="btn btn-primary" disabled={!newComment.trim()}>
                Comentar
              </button>
            </form>
          </>
        ) : (
          <div className="activity-list">
            {activities.map((activity) => (
              <div key={activity.id} className="activity-row">
                <Avatar user={activity.actor} size={22} />
                <span className="activity-text">
                  <strong>{activity.actor?.username ?? "Sistema"}</strong>{" "}
                  {ACTIVITY_VERBS[activity.verb]}
                  {activity.verb === "updated" && activity.field && (
                    <> {FIELD_LABELS[activity.field] ?? activity.field}</>
                  )}
                  {(activity.verb === "status_changed" ||
                    activity.verb === "section_changed" ||
                    activity.verb === "assigned" ||
                    activity.verb === "updated") &&
                    (activity.old_value !== null || activity.new_value !== null) && (
                      <span className="muted">
                        {" "}
                        · {valueLabel(activity.old_value)} → {valueLabel(activity.new_value)}
                      </span>
                    )}
                </span>
                <span className="muted activity-date">
                  {new Date(activity.created_at).toLocaleDateString("pt-BR")}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {task.due_date && (
        <div className="panel-footnote muted">Entrega: {formatDate(task.due_date)}</div>
      )}
    </div>
  );
}
