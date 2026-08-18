import { FormEvent, useEffect, useRef, useState } from "react";

import { api, ApiError } from "../api/client";
import { Membership, ROLE_LABELS, User } from "../api/types";
import { useAuth } from "../auth/AuthContext";
import Avatar from "../components/Avatar";
import { useWorkspace } from "../components/WorkspaceContext";

export default function Members() {
  const { workspace, members, reload } = useWorkspace();
  const { user: me } = useAuth();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<User[]>([]);
  const [role, setRole] = useState<Membership["role"]>("member");
  const [error, setError] = useState("");
  const timer = useRef<number>();

  const myRole = members.find((member) => member.user.id === me?.id)?.role;
  const isAdmin = myRole === "admin";

  useEffect(() => {
    window.clearTimeout(timer.current);
    if (query.trim().length < 2) {
      setResults([]);
      return;
    }
    timer.current = window.setTimeout(async () => {
      try {
        const users = await api.get<User[]>(`/users/?search=${encodeURIComponent(query.trim())}`);
        const memberIds = new Set(members.map((member) => member.user.id));
        setResults(users.filter((user) => !memberIds.has(user.id)));
      } catch {
        setResults([]);
      }
    }, 300);
    return () => window.clearTimeout(timer.current);
  }, [query, members]);

  async function invite(user: User) {
    if (!workspace) return;
    setError("");
    try {
      await api.post("/memberships/", { workspace: workspace.id, user_id: user.id, role });
      setQuery("");
      setResults([]);
      await reload();
    } catch (err) {
      setError(err instanceof ApiError ? err.firstMessage() : "Erro ao convidar.");
    }
  }

  async function changeRole(membership: Membership, newRole: string) {
    setError("");
    try {
      await api.patch(`/memberships/${membership.id}/`, { role: newRole });
      await reload();
    } catch (err) {
      setError(err instanceof ApiError ? err.firstMessage() : "Erro ao alterar papel.");
    }
  }

  async function remove(membership: Membership) {
    const isSelf = membership.user.id === me?.id;
    const message = isSelf
      ? "Sair deste workspace?"
      : `Remover ${membership.user.username} do workspace?`;
    if (!window.confirm(message)) return;
    setError("");
    try {
      await api.del(`/memberships/${membership.id}/`);
      await reload();
    } catch (err) {
      setError(err instanceof ApiError ? err.firstMessage() : "Erro ao remover.");
    }
  }

  return (
    <div className="members-page">
      <h1>Membros</h1>
      <p className="muted">
        {members.length} {members.length === 1 ? "membro" : "membros"} em {workspace?.name}
      </p>

      {isAdmin && (
        <div className="widget">
          <div className="widget-title">Convidar para o workspace</div>
          <form className="invite-form" onSubmit={(e: FormEvent) => e.preventDefault()}>
            <div className="invite-search">
              <input
                placeholder="Busque por usuário ou e-mail…"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
              {results.length > 0 && (
                <div className="search-results">
                  {results.map((user) => (
                    <button
                      key={user.id}
                      type="button"
                      className="search-result"
                      onMouseDown={() => invite(user)}
                    >
                      <Avatar user={user} size={24} />
                      <span className="search-result-title">{user.username}</span>
                      <span className="search-result-project">{user.email}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
            <select value={role} onChange={(e) => setRole(e.target.value as Membership["role"])}>
              {Object.entries(ROLE_LABELS).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </form>
          {error && <div className="form-error">{error}</div>}
        </div>
      )}

      <div className="widget">
        <div className="widget-body">
          {members.map((membership) => (
            <div key={membership.id} className="member-row">
              <Avatar user={membership.user} size={34} />
              <span className="member-info">
                <span className="member-name">
                  {membership.user.first_name
                    ? `${membership.user.first_name} ${membership.user.last_name}`.trim()
                    : membership.user.username}
                  {membership.user.id === me?.id && <span className="muted"> (você)</span>}
                </span>
                <span className="muted">{membership.user.email}</span>
              </span>
              {isAdmin ? (
                <select
                  value={membership.role}
                  onChange={(e) => changeRole(membership, e.target.value)}
                >
                  {Object.entries(ROLE_LABELS).map(([value, label]) => (
                    <option key={value} value={value}>
                      {label}
                    </option>
                  ))}
                </select>
              ) : (
                <span className="role-chip">{ROLE_LABELS[membership.role]}</span>
              )}
              {(isAdmin || membership.user.id === me?.id) && (
                <button
                  className="icon-btn"
                  title={membership.user.id === me?.id ? "Sair do workspace" : "Remover"}
                  onClick={() => remove(membership)}
                >
                  ✕
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
