import { motion } from 'framer-motion';
import { FiShield, FiTrendingUp, FiTrendingDown, FiAlertTriangle, FiTarget } from 'react-icons/fi';

const riskStyles = {
    low: { class: 'risk-low', icon: FiTrendingUp },
    medium: { class: 'risk-medium', icon: FiAlertTriangle },
    'medium-high': { class: 'risk-high', icon: FiAlertTriangle },
    high: { class: 'risk-high', icon: FiTrendingDown },
    critical: { class: 'risk-critical', icon: FiShield },
};

export default function ExecutiveSummary({ summary, reasoning }) {
    if (!summary) return null;

    const risk = summary.risk_outlook || {};
    const riskKey = (risk.overall_risk || 'medium').toLowerCase().replace(' ', '-');
    const riskInfo = riskStyles[riskKey] || riskStyles.medium;
    const RiskIcon = riskInfo.icon;

    return (
        <motion.div
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, ease: 'easeOut' }}
            className="glass-card space-y-5"
        >
            {/* Header */}
            <div>
                <h3 className="text-lg font-bold gradient-text mb-1">Executive Summary</h3>
                <p className="text-xs" style={{ color: '#64748b' }}>Generated: {summary.generated_at || 'Live'}</p>
            </div>

            {/* Risk Score */}
            <motion.div
                initial={{ scale: 0.9 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.3, type: 'spring' }}
                className="flex items-center gap-4 p-4 rounded-xl"
                style={{ background: 'rgba(124, 58, 237, 0.08)', border: '1px solid rgba(124, 58, 237, 0.15)' }}
            >
                <div className="relative">
                    <svg width="64" height="64" viewBox="0 0 64 64">
                        <circle cx="32" cy="32" r="28" fill="none" stroke="rgba(124,58,237,0.15)" strokeWidth="4" />
                        <circle
                            cx="32" cy="32" r="28"
                            fill="none"
                            stroke={riskKey.includes('high') || riskKey === 'critical' ? '#ef4444' : riskKey === 'medium' ? '#f59e0b' : '#10b981'}
                            strokeWidth="4"
                            strokeDasharray={`${(risk.risk_score || 0) * 1.76} 176`}
                            strokeLinecap="round"
                            transform="rotate(-90 32 32)"
                        />
                        <text x="32" y="36" textAnchor="middle" fill="#f1f5f9" fontSize="16" fontWeight="bold">
                            {risk.risk_score || 0}
                        </text>
                    </svg>
                </div>
                <div>
                    <div className="text-sm font-semibold" style={{ color: '#f1f5f9' }}>Competitive Risk Score</div>
                    <span className={`risk-badge ${riskInfo.class} mt-1`}>
                        <RiskIcon size={12} /> {risk.overall_risk || 'Medium'}
                    </span>
                </div>
            </motion.div>

            {/* Strategic Positioning */}
            <Section title="Strategic Positioning" icon={<FiTarget size={14} />} delay={0.4}>
                <p className="text-sm leading-relaxed" style={{ color: '#94a3b8' }}>
                    {summary.strategic_positioning}
                </p>
            </Section>

            {/* Strengths */}
            <Section title="Strengths" icon={<FiTrendingUp size={14} />} delay={0.5} accentColor="#10b981">
                <ul className="space-y-1.5">
                    {(summary.strengths || []).map((s, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm" style={{ color: '#94a3b8' }}>
                            <span style={{ color: '#10b981', marginTop: 2 }}>✦</span>
                            {s}
                        </li>
                    ))}
                </ul>
            </Section>

            {/* Weaknesses */}
            <Section title="Weaknesses" icon={<FiTrendingDown size={14} />} delay={0.6} accentColor="#f59e0b">
                <ul className="space-y-1.5">
                    {(summary.weaknesses || []).map((w, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm" style={{ color: '#94a3b8' }}>
                            <span style={{ color: '#f59e0b', marginTop: 2 }}>⚠</span>
                            {w}
                        </li>
                    ))}
                </ul>
            </Section>

            {/* Threats */}
            <Section title="Primary Threats" icon={<FiAlertTriangle size={14} />} delay={0.7} accentColor="#ef4444">
                <ul className="space-y-1.5">
                    {(risk.primary_threats || []).map((t, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm" style={{ color: '#94a3b8' }}>
                            <span style={{ color: '#ef4444', marginTop: 2 }}>●</span>
                            {t}
                        </li>
                    ))}
                </ul>
            </Section>

            {/* Reasoning (if available) */}
            {reasoning && reasoning.explanation && (
                <Section title="AI Analysis" icon={<FiShield size={14} />} delay={0.8} accentColor="#a855f7">
                    <p className="text-sm leading-relaxed" style={{ color: '#94a3b8' }}>
                        {reasoning.explanation}
                    </p>
                    {reasoning.recommendations && (
                        <div className="mt-3">
                            <div className="text-xs font-semibold mb-2" style={{ color: '#a855f7' }}>Recommendations</div>
                            <ul className="space-y-1">
                                {reasoning.recommendations.map((r, i) => (
                                    <li key={i} className="flex items-start gap-2 text-sm" style={{ color: '#94a3b8' }}>
                                        <span style={{ color: '#a855f7', marginTop: 2 }}>→</span>
                                        {r}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                </Section>
            )}
        </motion.div>
    );
}

function Section({ title, icon, delay = 0, accentColor = '#a855f7', children }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay, duration: 0.4 }}
        >
            <div className="flex items-center gap-2 mb-2">
                <span style={{ color: accentColor }}>{icon}</span>
                <h4 className="text-sm font-semibold" style={{ color: '#f1f5f9' }}>{title}</h4>
            </div>
            {children}
        </motion.div>
    );
}
