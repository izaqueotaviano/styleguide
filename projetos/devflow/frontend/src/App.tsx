import { ReactNode } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { AuthProvider, useAuth } from "./auth/AuthContext";
import Layout from "./components/Layout";
import Board from "./pages/Board";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Members from "./pages/Members";
import MyTasks from "./pages/MyTasks";

function RequireAuth({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="screen-center">Carregando…</div>;
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            element={
              <RequireAuth>
                <Layout />
              </RequireAuth>
            }
          >
            <Route index element={<Home />} />
            <Route path="my-tasks" element={<MyTasks />} />
            <Route path="members" element={<Members />} />
            <Route path="projects/:projectId" element={<Board />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
