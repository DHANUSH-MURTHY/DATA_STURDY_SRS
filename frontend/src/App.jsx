import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FiGrid, FiGlobe } from 'react-icons/fi';
import Dashboard from './pages/Dashboard';

function Navbar() {
  return (
    <motion.nav
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="sticky top-0 z-50 px-6 py-3 flex items-center justify-between"
      style={{
        background: 'rgba(10, 10, 20, 0.85)',
        backdropFilter: 'blur(16px)',
        borderBottom: '1px solid rgba(124, 58, 237, 0.12)',
      }}
    >
      <div className="flex items-center gap-3 flex-1">
        <div
          className="w-8 h-8 rounded-lg flex items-center justify-center"
          style={{
            background: 'linear-gradient(135deg, #7c3aed, #a855f7)',
            boxShadow: '0 2px 12px rgba(124, 58, 237, 0.4)',
          }}
        >
          <FiGlobe size={16} className="text-white" />
        </div>
        <span className="text-sm font-bold gradient-text tracking-wide">INTEL ORCHESTRATOR</span>
      </div>

      <div className="flex items-center gap-1 justify-center">
        <NavLink to="/" end className={({ isActive }) => `nav-link flex items-center gap-2 ${isActive ? 'active' : ''}`}>
          <FiGrid size={14} /> Dashboard
        </NavLink>
      </div>

      <div className="flex items-center gap-2 flex-1 justify-end">
        <div className="w-2 h-2 rounded-full" style={{ background: '#10b981', boxShadow: '0 0 8px #10b98180' }} />
        <span className="text-xs" style={{ color: '#94a3b8' }}>System Online</span>
      </div>
    </motion.nav>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen" style={{ background: '#0a0a14' }}>
        <Navbar />
        <Routes>
          <Route path="/" element={<Dashboard />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
