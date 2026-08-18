import {
  createContext,
  ReactNode,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";

import { api, listAll } from "../api/client";
import { Membership, Project, Workspace } from "../api/types";

interface WorkspaceState {
  workspace: Workspace | null;
  projects: Project[];
  members: Membership[];
  loading: boolean;
  createWorkspace: (name: string) => Promise<void>;
  createProject: (name: string, key: string) => Promise<Project>;
  projectName: (id: string) => string;
}

const WorkspaceContext = createContext<WorkspaceState | null>(null);

export function WorkspaceProvider({ children }: { children: ReactNode }) {
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [members, setMembers] = useState<Membership[]>([]);
  const [loading, setLoading] = useState(true);

  const loadAll = useCallback(async () => {
    const workspaces = await listAll<Workspace>("/workspaces/");
    const current = workspaces[0] ?? null;
    setWorkspace(current);
    if (current) {
      const [projectList, memberList] = await Promise.all([
        listAll<Project>(`/projects/?workspace=${current.id}`),
        listAll<Membership>(`/memberships/?workspace=${current.id}`),
      ]);
      setProjects(projectList);
      setMembers(memberList);
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    loadAll().catch(() => setLoading(false));
  }, [loadAll]);

  const createWorkspace = useCallback(
    async (name: string) => {
      await api.post<Workspace>("/workspaces/", { name });
      await loadAll();
    },
    [loadAll],
  );

  const createProject = useCallback(
    async (name: string, key: string) => {
      if (!workspace) throw new Error("Sem workspace");
      const project = await api.post<Project>("/projects/", {
        workspace: workspace.id,
        name,
        key,
      });
      setProjects((previous) => [...previous, project]);
      return project;
    },
    [workspace],
  );

  const projectName = useCallback(
    (id: string) => projects.find((project) => project.id === id)?.name ?? "",
    [projects],
  );

  return (
    <WorkspaceContext.Provider
      value={{ workspace, projects, members, loading, createWorkspace, createProject, projectName }}
    >
      {children}
    </WorkspaceContext.Provider>
  );
}

export function useWorkspace(): WorkspaceState {
  const state = useContext(WorkspaceContext);
  if (!state) throw new Error("useWorkspace deve ser usado dentro de WorkspaceProvider");
  return state;
}

/** Sugere uma chave de projeto a partir do nome (ex.: "Loja Virtual" → "LV"). */
export function suggestKey(name: string): string {
  const words = name
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toUpperCase()
    .split(/[^A-Z0-9]+/)
    .filter(Boolean);
  let key = words.length >= 2 ? words.map((w) => w[0]).join("") : (words[0] ?? "").slice(0, 4);
  key = key.replace(/^[0-9]+/, "");
  if (key.length < 2) key = ((words[0] ?? "PROJ") + "PROJ").slice(0, 4).replace(/^[0-9]+/, "PR");
  return key.slice(0, 10);
}
