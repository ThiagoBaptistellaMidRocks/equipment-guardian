import {
  Bell,
  BarChart3,
  Grid3X3,
  HelpCircle,
  Hexagon,
  Map,
  Settings,
  SlidersHorizontal,
  Wrench
} from "lucide-react";

interface TopBarProps {
  onCopilotOpen?: () => void;
}

export function TopBar({ onCopilotOpen }: TopBarProps) {
  return (
    <header className="top-bar">
      <div className="brand-lockup">
        <Hexagon aria-hidden="true" className="brand-mark" fill="currentColor" />
        <span>EQUIPMENT GUARDIAN</span>
      </div>
      <div className="site-pills">
        <span><b>Site</b> Pilbara Iron Mine</span>
        <span><b>Pit</b> Pit Alpha</span>
        <span><b>Shift</b> Day 06:00-18:00</span>
      </div>
      <time className="shift-clock">14:32:07</time>
      <div className="system-state">
        <span className="online-dot" />
        <span>System Online</span>
        {onCopilotOpen && (
          <button className="copilot-trigger-topbar" type="button" onClick={onCopilotOpen}>
            Ask AI Copilot
          </button>
        )}
        <span className="bell-wrap"><Bell size={18} /><small>3</small></span>
        <span className="avatar">JM</span>
      </div>
    </header>
  );
}

const navItems = [
  { label: "Map", icon: Map, active: true },
  { label: "Alerts", icon: Bell },
  { label: "Assets", icon: Grid3X3 },
  { label: "Systems", icon: SlidersHorizontal },
  { label: "Maintenance", icon: Wrench },
  { label: "Analytics", icon: BarChart3 }
];

export function SideNav() {
  return (
    <aside className="side-nav" aria-label="Primary navigation">
      <div className="nav-stack">
        {navItems.map(({ label, icon: Icon, active }) => (
          <button className={`nav-button ${active ? "active" : ""}`} key={label} type="button" aria-label={label}>
            <Icon size={21} />
          </button>
        ))}
      </div>
      <div className="nav-stack">
        <button className="nav-button" type="button" aria-label="Settings"><Settings size={20} /></button>
        <button className="nav-button" type="button" aria-label="Help"><HelpCircle size={20} /></button>
      </div>
    </aside>
  );
}
