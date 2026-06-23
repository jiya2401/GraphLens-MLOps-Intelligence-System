/**
 * Dashboard Layout — main application shell with sidebar navigation.
 *
 * This is a "layout component" — it wraps all page content and provides
 * consistent navigation. React Router renders the active page inside
 * the <Outlet /> component.
 *
 * Interview Q: "What is a layout component in React?"
 * Answer: A component that provides shared UI (navigation, sidebar)
 * across multiple pages. Combined with React Router's nested routes,
 * only the page content changes — the layout stays mounted.
 */

import { NavLink, Outlet } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useUIStore } from '../stores/uiStore';
import {
  Network, BarChart3, Clock, Zap, Brain, Target,
  Database, Activity, Menu, X, ChevronRight
} from 'lucide-react';

const navItems = [
  { path: '/', icon: Network, label: 'Graph Explorer', id: 'graph-explorer' },
  { path: '/analytics', icon: BarChart3, label: 'Analytics', id: 'analytics' },
  { path: '/temporal', icon: Clock, label: 'Temporal Replay', id: 'temporal' },
  { path: '/failure', icon: Zap, label: 'Failure Propagation', id: 'failure' },
  { path: '/explainability', icon: Brain, label: 'Explainability', id: 'explainability' },
  { path: '/predictions', icon: Target, label: 'Predictions', id: 'predictions' },
  { path: '/datasets', icon: Database, label: 'Dataset Manager', id: 'datasets' },
  { path: '/system', icon: Activity, label: 'System Metrics', id: 'system' },
];

export function DashboardLayout() {
  const { sidebarOpen, toggleSidebar } = useUIStore();

  return (
    <div className="flex h-screen overflow-hidden" style={{ background: 'var(--bg-primary)' }}>
      {/* Sidebar */}
      <AnimatePresence mode="wait">
        {sidebarOpen && (
          <motion.aside
            initial={{ x: -260, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -260, opacity: 0 }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="glass-strong flex flex-col h-full z-30"
            style={{ width: 'var(--sidebar-width)', minWidth: 'var(--sidebar-width)' }}
          >
            {/* Logo */}
            <div className="flex items-center justify-between p-5 border-b" style={{ borderColor: 'var(--border-subtle)' }}>
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: 'var(--accent-gradient)' }}>
                  <Network size={18} className="text-white" />
                </div>
                <div>
                  <h1 className="text-base font-bold gradient-text">GraphLens</h1>
                  <p className="text-[10px] font-medium" style={{ color: 'var(--text-muted)' }}>MLOps Intelligence</p>
                </div>
              </div>
              <button onClick={toggleSidebar} className="p-1.5 rounded-lg hover:bg-white/5 transition-colors">
                <X size={16} style={{ color: 'var(--text-muted)' }} />
              </button>
            </div>

            {/* Navigation */}
            <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
              {navItems.map((item) => (
                <NavLink
                  key={item.id}
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 group ${
                      isActive
                        ? 'text-white'
                        : 'hover:bg-white/5'
                    }`
                  }
                  style={({ isActive }) =>
                    isActive
                      ? { background: 'var(--accent-gradient)', boxShadow: 'var(--shadow-glow)' }
                      : { color: 'var(--text-secondary)' }
                  }
                >
                  <item.icon size={18} />
                  <span>{item.label}</span>
                  <ChevronRight size={14} className="ml-auto opacity-0 group-hover:opacity-100 transition-opacity" />
                </NavLink>
              ))}
            </nav>

            {/* Footer */}
            <div className="p-4 border-t" style={{ borderColor: 'var(--border-subtle)' }}>
              <div className="flex items-center gap-2 px-2">
                <div className="w-2 h-2 rounded-full" style={{ background: 'var(--status-healthy)', boxShadow: '0 0 8px var(--status-healthy)' }} />
                <span className="text-xs" style={{ color: 'var(--text-muted)' }}>System Operational</span>
              </div>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <header
          className="flex items-center justify-between px-6 border-b shrink-0"
          style={{ height: 'var(--topbar-height)', borderColor: 'var(--border-subtle)', background: 'var(--bg-secondary)' }}
        >
          <div className="flex items-center gap-4">
            {!sidebarOpen && (
              <button onClick={toggleSidebar} className="p-2 rounded-lg hover:bg-white/5 transition-colors">
                <Menu size={18} style={{ color: 'var(--text-secondary)' }} />
              </button>
            )}
            <div>
              <h2 className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>Dashboard</h2>
              <p className="text-xs" style={{ color: 'var(--text-muted)' }}>MLOps Pipeline Intelligence</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg" style={{ background: 'var(--bg-card)', border: '1px solid var(--border-subtle)' }}>
              <div className="w-1.5 h-1.5 rounded-full" style={{ background: 'var(--status-healthy)' }} />
              <span className="text-xs font-medium" style={{ color: 'var(--text-secondary)' }}>API Connected</span>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
