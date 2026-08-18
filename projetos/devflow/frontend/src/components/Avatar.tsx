import { User } from "../api/types";

const COLORS = ["#f06a6a", "#ec8d71", "#f1bd6c", "#aecf55", "#5da283", "#4ecbc4", "#8d84e8", "#f9aaef"];

export function initialsOf(user: User): string {
  const first = user.first_name?.trim();
  const last = user.last_name?.trim();
  if (first && last) return (first[0] + last[0]).toUpperCase();
  return user.username.slice(0, 2).toUpperCase();
}

export default function Avatar({ user, size = 24 }: { user: User | null; size?: number }) {
  if (!user) {
    return (
      <span className="avatar avatar-empty" style={{ width: size, height: size }} title="Sem responsável">
        <svg width={size * 0.6} height={size * 0.6} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="8" r="4" />
          <path d="M4 21c0-4 4-6 8-6s8 2 8 6" />
        </svg>
      </span>
    );
  }
  const color = COLORS[user.id % COLORS.length];
  return (
    <span
      className="avatar"
      style={{ width: size, height: size, background: color, fontSize: size * 0.42 }}
      title={user.first_name ? `${user.first_name} ${user.last_name}`.trim() : user.username}
    >
      {initialsOf(user)}
    </span>
  );
}
