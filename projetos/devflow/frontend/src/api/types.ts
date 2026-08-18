export interface User {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  email: string;
}

export interface Workspace {
  id: string;
  name: string;
  slug: string;
}

export interface Membership {
  id: string;
  workspace: string;
  user: User;
  role: "admin" | "member" | "guest";
}

export interface Project {
  id: string;
  workspace: string;
  name: string;
  key: string;
  description: string;
  estimate_unit: string;
}

export interface TaskStatus {
  id: string;
  name: string;
  category: "backlog" | "unstarted" | "started" | "completed" | "canceled";
  project?: string;
  order?: number;
  is_default?: boolean;
}

export interface Section {
  id: string;
  name: string;
  order: number;
}

export interface Label {
  id: string;
  name: string;
  color: string;
}

export interface Task {
  id: string;
  key: string;
  number: number;
  project: string;
  parent: string | null;
  title: string;
  description: string;
  type: "feature" | "bug" | "improvement" | "tech_debt" | "chore";
  priority: "urgent" | "high" | "medium" | "low";
  status: TaskStatus | null;
  section: Section | null;
  assignee: User | null;
  reviewer: User | null;
  labels: Label[];
  estimate: string | null;
  due_date: string | null;
  order: number;
  completed_at: string | null;
  subtasks_count: number;
  created_at: string;
  updated_at: string;
  subtasks?: Task[];
}

export interface Comment {
  id: string;
  task: string;
  author: User | null;
  body: string;
  mentions: User[];
  created_at: string;
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export const TYPE_LABELS: Record<Task["type"], string> = {
  feature: "Feature",
  bug: "Bug",
  improvement: "Melhoria",
  tech_debt: "Débito técnico",
  chore: "Manutenção",
};

export const PRIORITY_LABELS: Record<Task["priority"], string> = {
  urgent: "Urgente",
  high: "Alta",
  medium: "Média",
  low: "Baixa",
};

export interface Activity {
  id: string;
  task: string;
  actor: User | null;
  verb: "created" | "updated" | "status_changed" | "section_changed" | "assigned" | "commented" | "deleted";
  field: string;
  old_value: unknown;
  new_value: unknown;
  created_at: string;
}

export interface Notification {
  id: string;
  actor: User | null;
  verb: "task_assigned" | "review_requested" | "mentioned" | "commented";
  task: string | null;
  task_key: string | null;
  task_title: string | null;
  task_project: string | null;
  comment: string | null;
  read_at: string | null;
  created_at: string;
}

export const ROLE_LABELS: Record<Membership["role"], string> = {
  admin: "Admin",
  member: "Membro",
  guest: "Convidado",
};
