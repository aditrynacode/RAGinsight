import { Routes, Route } from "react-router-dom";
import NavBar from "./components/NavBar";
import ChatPage from "./pages/ChatPage";
import DashboardPage from "./pages/DashboardPage";

export default function App() {
  return (
    <div className="app-shell">
      <NavBar />
      <Routes>
        <Route path="/" element={<ChatPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
      </Routes>
    </div>
  );
}
