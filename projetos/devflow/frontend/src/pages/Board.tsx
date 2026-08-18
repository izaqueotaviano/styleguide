import { FormEvent, useCallback, useEffect, useState } from "react";
import { useParams, useSearchParams } from "react-router-dom";

import { api, listAll } from "../api/client";
import { PRIORITY_LABELS, Section, Task, TaskStatus, TYPE_LABELS } from "../api/types";
import Avatar from "../components/Avatar";
import { projectColor } from "../components/Sidebar";
import TaskCard, { formatDate, PRIORITY_COLORS } from "../components/TaskCard";
import TaskPanel from "../components/TaskPanel";
import { useWorkspace } from "../components/WorkspaceContext";

function sortTasks(list: Task[]): Task[] {
  return [...list].sort(
    (a, b) => a.order - b.order || a.created_at.localeCompare(b.created_at),
  );
}

export default function Board() {
  const { projectId } = useParams<{ projectId: string }>();
  const { projects, members } = useWorkspace();
  const project = projects.find((item) => item.id === projectId);
  const [statuses, setStatuses] = useState<TaskStatus[]>([]);
  const [sections, setSections] = useState<Section[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [view, setView] = useState<"board" | "list">("board");
  const [addingIn, setAddingIn] = useState<string | null>(null);
  const [newTitle, setNewTitle] = useState("");
  const [newSection, setNewSection] = useState("");
  const [addingSection, setAddingSection] = useState(false);
  const [filterAssignee, setFilterAssignee] = useState("all");
  const [filterType, setFilterType] = useState("all");
  const [filterPriority, setFilterPriority] = useState("all");
  const [searchParams, setSearchParams] = useSearchParams();
  const openTaskId = searchParams.get("task");

  useEffect(() => {
    if (!projectId) return;
    setStatuses([]);
    setSections([]);
    setTasks([]);
    Promise.all([
      listAll<TaskStatus>(`/statuses/?project=${projectId}`),
      listAll<Section>(`/sections/?project=${projectId}`),
      listAll<Task>(`/tasks/?project=${projectId}`),
    ]).then(([statusList, sectionList, taskList]) => {
      setStatuses(statusList);
      setSections(sectionList);
      setTasks(taskList);
    });
  }, [projectId]);

  const applyUpdate = useCallback((updated: Task) => {
    setTasks((previous) =>
      previous.map((task) => (task.id === updated.id ? { ...task, ...updated } : task)),
    );
  }, []);

  async function moveTask(taskId: string, statusId: string, order?: number) {
    const target = statuses.find((status) => status.id === statusId);
    const original = tasks.find((task) => task.id === taskId);
    if (!target || !original) return;
    if (original.status?.id === statusId && order === undefined) return;
    applyUpdate({ ...original, status: target, order: order ?? original.order });
    try {
      await api.post<Task>(`/tasks/${taskId}/move/`, {
        status: statusId,
        ...(order !== undefined ? { order } : {}),
      });
      // Recarrega para refletir a reordenação feita no servidor.
      setTasks(await listAll<Task>(`/tasks/?project=${projectId}`));
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

  async function createSection(event: FormEvent) {
    event.preventDefault();
    if (!newSection.trim() || !projectId) return;
    const section = await api.post<Section>("/sections/", {
      project: projectId,
      name: newSection.trim(),
      order: sections.length,
    });
    setSections([...sections, section]);
    setNewSection("");
    setAddingSection(false);
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

  const topLevel = tasks.filter((task) => {
    if (task.parent !== null) return false;
    if (filterAssignee === "none" && task.assignee !== null) return false;
    if (
      filterAssignee !== "all" &&
      filterAssignee !== "none" &&
      String(task.assignee?.id ?? "") !== filterAssignee
    )
      return false;
    if (filterType !== "all" && task.type !== filterType) return false;
    if (filterPriority !== "all" && task.priority !== filterPriority) return false;
    return true;
  });

  function renderRow(task: Task) {
    return (
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
          <span className="priority-chip" style={{ background: PRIORITY_COLORS[task.priority] }}>
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
    );
  }

  const orderedSections = [...sections].sort((a, b) => a.order - b.order);
  const noSectionTasks = sortTasks(
    topLevel.filter((task) => task.section === null),
  );

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
        <div className="filter-bar">
          <select value={filterAssignee} onChange={(e) => setFilterAssignee(e.target.value)}>
            <option value="all">Responsável: todos</option>
            <option value="none">Sem responsável</option>
            {members.map((member) => (
              <option key={member.user.id} value={String(member.user.id)}>
                {member.user.username}
              </option>
            ))}
          </select>
          <select value={filterType} onChange={(e) => setFilterType(e.target.value)}>
            <option value="all">Tipo: todos</option>
            {Object.entries(TYPE_LABELS).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
          <select value={filterPriority} onChange={(e) => setFilterPriority(e.target.value)}>
            <option value="all">Prioridade: todas</option>
            {Object.entries(PRIORITY_LABELS).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="board-body">
        {view === "board" ? (
          <div className="board-columns">
            {statuses.map((status) => {
              const columnTasks = sortTasks(
                topLevel.filter((task) => task.status?.id === status.id),
              );
              const appendOrder =
                columnTasks.length > 0 ? columnTasks[columnTasks.length - 1].order + 1 : 0;
              return (
                <div
                  key={status.id}
                  className="board-column"
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={(e) =>
                    moveTask(e.dataTransfer.getData("text/task"), status.id, appendOrder)
                  }
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
                        onDropBefore={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          const draggedId = e.dataTransfer.getData("text/task");
                          if (draggedId && draggedId !== task.id) {
                            moveTask(draggedId, status.id, task.order);
                          }
                        }}
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
          <div className="list-view">
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
                {orderedSections.map((section) => {
                  const sectionTasks = sortTasks(
                    topLevel.filter((task) => task.section?.id === section.id),
                  );
                  return [
                    <tr key={section.id} className="section-row">
                      <td colSpan={5}>▾ {section.name}</td>
                    </tr>,
                    ...sectionTasks.map(renderRow),
                  ];
                })}
                {noSectionTasks.length > 0 && (
                  <>
                    {orderedSections.length > 0 && (
                      <tr className="section-row">
                        <td colSpan={5}>▾ Sem seção</td>
                      </tr>
                    )}
                    {noSectionTasks.map(renderRow)}
                  </>
                )}
              </tbody>
            </table>
            {addingSection ? (
              <form className="inline-form section-form" onSubmit={createSection}>
                <input
                  autoFocus
                  placeholder="Nome da seção"
                  value={newSection}
                  onChange={(e) => setNewSection(e.target.value)}
                  onBlur={() => setAddingSection(false)}
                />
              </form>
            ) : (
              <button className="add-task-btn section-form" onClick={() => setAddingSection(true)}>
                + Adicionar seção
              </button>
            )}
          </div>
        )}

        {openTaskId && (
          <TaskPanel
            taskId={openTaskId}
            statuses={statuses}
            sections={sections}
            onClose={closePanel}
            onChanged={applyUpdate}
          />
        )}
      </div>
    </div>
  );
}
