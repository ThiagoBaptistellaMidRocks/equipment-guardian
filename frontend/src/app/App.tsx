import { Outlet } from "react-router-dom";

export function App() {
  return (
    <main className="app-shell">
      <header>
        <h1>Equipment Guardian</h1>
        <p>Asset-centered mining equipment intelligence.</p>
      </header>
      <Outlet />
    </main>
  );
}

