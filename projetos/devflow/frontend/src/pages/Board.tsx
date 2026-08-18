import { FormEvent, useCallback, useEffect, useState } from "react";
import { useParams, useSearchParams } from "react-router-dom";

import { api, listAll } from "../api/client";
import { Task, TaskStatus } from "../api/types";
import Avatar from "../components/Avatar";
import { projectColor } from "../components/Sidebar";
import TaskCard, { formatDate, PRIORITY_COLORS } from "../components/TaskCard";
import TaskPanel from "../components/TaskPanel";
import { useWorkspace } from "../components/WorkspaceContext";

export default function Board() {
  const { projectId } = useParams<{ projectId: string }>();
  const { projects } = useWorkspace();
  const project = projects.find((item) => item.id === projectId);
  const [statuses, setStatuses] = useState<TaskStatus[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [view, setView] = useState<"board" | "list">("board");
  const [addingIn, setAddingIn] = useState<string | null>(null);
  const [newTitle, setNewTitle] = useState("");
  const [searchParams, setSearchParams] = useSearchParams();
  const openTaskId = searchParams.get("task");

  useEffect(() => {
    if (!projectId) return;
    setStatuses([]);
    setTasks([]);
    Promise.all([
      listAll<TaskStatus>(`/statuses/?project=${projectId}`),
      listAll<Task>(`/tasks/?project=${projectId}`),
    ]).then(([statusList, taskList]) => {
      setStatuses(statusList);
      setTasks(taskList);
    });
  }, [projectId]);

  const applyUpdate = useCallback((updated: Task) => {
    setTasks((previous) =>
      previous.map((task) => (task.id === updated.id ? { ...task, ...updated } : task)),
    );
  }, []);

  async function moveTask(taskId: string, statusId: string) {
    const target = statuses.find((status) => status.id === statusId);
    const original = tasks.find((task) => task.id === taskId);
    if (!target || !original || original.status?.id === statusId) return;
    applyUpdate({ ...original, status: target });
    try {
      const updated = await api.post<Task>(`/tasks/${taskId}/move/`, { status: statusId });
      applyUpdate(updated);
    } catch {
      applyUpdate(original);
    }
  }

  async function createTask(event: FormEvent, statusId: string) {
    event.preventDefault();
    if (!newTitle.trim() || !projectId) return;
    const task = await api.post<Task>("/tasks/", {
      project: projectId,
      title: newTitle.trim(),
      status: statusId,
    });
    setTasks((previous) => [...previous, task]);
    setNewTitle("");
  }

  function openTask(taskId: string) {
    searchParams.set("task", taskId);
    setSearchParams(searchParams, { replace: true });
  }

  function closePanel() {
    searchParams.delete("task");
    setSearchParams(searchParams, { replace: true });
  }

  if (!project) return <div className="screen-center">Projeto não encontrado.</div>;

  const topLevel = tasks.filter((task) => task.parent === null);

  return (
    <div className="board-page">
      <div className="board-header">
        <span className="project-badge" style={{ background: projectColor(project.id) }}>
          {project.key.slice(0, 2)}
        </span>
        <h1>{project.name}</h1>
        <div className="view-tabs">
          <button className={view === "board" ? "active" : ""} onClick={() => setView("board")}>
            Quadro
          </button>
          <button className={view === "list" ? "active" : ""} onClick={() => setView("list")}>
            Lista
          </button>
        </div>
      </div>

      <div className="board-body">
        {view === "board" ? (
          <div className="board-columns">
            {statuses.map((status) => {
              const columnTasks = topLevel.filter((task) => task.status?.id === status.id);
              return (
                <div
                  key={status.id}
                  className="board-column"
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={(e) => moveTask(e.dataTransfer.getData("text/task"), status.id)}
                >
                  <div className="column-header">
                    <span className="column-title">{status.name}</span>
                    <span className="column-count">{columnTasks.length}</span>
                  </div>
                  <div className="column-cards">
                    {columnTasks.map((task) => (
                      <TaskCard
                        key={task.id}
                        task={task}
                        onOpen={() => openTask(task.id)}
                        onDragStart={(e) => e.dataTransfer.setData("text/task", task.id)}
                      />
                    ))}
                    {addingIn === status.id ? (
                      <form onSubmit={(e) => createTask(e, status.id)}>
                        <input
                          autoFocus
                          className="new-task-input"
                          placeholder="Nome da tarefa"
                          value={newTitle}
                          onChange={(e) => setNewTitle(e.target.value)}
                          onBlur={() => {
                            setAddingIn(null);
                            setNewTitle("");
                          }}
                        />
                      </form>
                    ) : (
                      <button className="add-task-btn" onClick={() => setAddingIn(status.id)}>
                        + Adicionar uma tarefa
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <table className="task-table">
            <thead>
              <tr>
                <th>Tarefa</th>
                <th>Responsável</th>
                <th>Entrega</th>
                <th>Prioridade</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {topLevel.map((task) => (
                <tr key={task.id} onClick={() => openTask(task.id)}>
                  <td>
                    <span className={task.completed_at ? "task-done" : ""}>
                      <span className="task-key">{task.key}</span> {task.title}
                    </span>
                  </td>
                  <td>
                    <Avatar user={task.assignee} size={22} />
                  </td>
                  <td>{formatDate(task.due_date)}</td>
                  <td>
                    <span
                      className="priority-chip"
                      style={{ background: PRIORITY_COLORS[task.priority] }}
                    >
                      {task.priority}
                    </span>
                  </td>
                  <td onClick={(e) => e.stopPropagation()}>
                    <select
                      value={task.status?.id ?? ""}
                      onChange={(e) => moveTask(task.id, e.target.value)}
                    >
                      {statuses.map((status) => (
                        <option key={status.id} value={status.id}>
                          {status.name}
                        </option>
                      ))}
                    </select>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {openTaskId && (
          <TaskPanel
            taskId={openTaskId}
            statuses={statuses}
            onClose={closePanel}
            onChanged={applyUpdate}
          />
        )}
      </div>
    </div>
  );
}
