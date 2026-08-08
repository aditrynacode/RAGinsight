import { NavLink } from "react-router-dom";
import "./NavBar.css";

export default function NavBar() {
  return (
    <header className="navbar">
      <div className="navbar-brand">
        <span className="navbar-dot" />
        RAGInsight
      </div>
      <nav className="navbar-links">
        <NavLink to="/" end className={({ isActive }) => (isActive ? "active" : "")}>
          Chat
        </NavLink>
        <NavLink to="/dashboard" className={({ isActive }) => (isActive ? "active" : "")}>
          Ops dashboard
        </NavLink>
      </nav>
    </header>
  );
}
