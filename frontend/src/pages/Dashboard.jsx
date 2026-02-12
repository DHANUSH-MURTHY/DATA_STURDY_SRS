import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import GraphView from '../components/GraphView';
import ComparisonTable from '../components/ComparisonTable';
import ExecutiveSummary from '../components/ExecutiveSummary';
import { runAnalysis, getGraph, getComparison, getSummary, exportData } from '../api';
import { FiSearch, FiZap, FiActivity, FiDownload } from 'react-icons/fi';

const QUICK_QUERIES = [
    "How is Infosys positioning differently than TCS in GenAI for 2026?",
    "If Accenture increases investment in NVIDIA-based centers, how does that threaten Infosys Topaz?",
    "Common partners between Infosys and Accenture",
    "Which company is expanding fastest in Nordics?",
    "Who has more NVIDIA exposure?",
];

export default function Dashboard() {
    const [query, setQuery] = useState('');
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState(null);
    const [graphData, setGraphData] = useState(null);
    const [comparison, setComparison] = useState(null);
    const [summary, setSummary] = useState(null);
    const [activeTab, setActiveTab] = useState('graph');

    const handleAnalyze = async () => {
        if (!query.trim()) return;
        setLoading(true);
        try {
            const [analysisRes, graphRes, compRes, summRes] = await Promise.all([
                runAnalysis(query),
                getGraph(),
                getComparison(),
                getSummary(),
            ]);
            setResults(analysisRes.data);
            setGraphData(graphRes.data);
            setComparison(compRes.data.comparison);
            setSummary(summRes.data);
        } catch (err) {
            console.error('Analysis failed:', err);
            // Load demo data on error
            try {
                const [graphRes, compRes, summRes] = await Promise.all([
                    getGraph(),
                    getComparison(),
                    getSummary(),
                ]);
                setGraphData(graphRes.data);
                setComparison(compRes.data.comparison);
                setSummary(summRes.data);
                setResults({ status: 'complete' });
            } catch (e2) {
                console.error('Failed to load even demo data:', e2);
            }
        } finally {
            setLoading(false);
        }
    };

    const handleExportCSV = async () => {
        try {
            const res = await exportData('csv');
            const blob = new Blob([JSON.stringify(res.data)], { type: 'text/csv' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'comparison_table.csv';
            a.click();
            URL.revokeObjectURL(url);
        } catch (err) {
            // Fallback: generate CSV from local data
            if (comparison) {
                const headers = Object.keys(comparison[0]);
                const csv = [headers.join(','), ...comparison.map(row => headers.map(h => `"${row[h]}"`).join(','))].join('\n');
                const blob = new Blob([csv], { type: 'text/csv' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'comparison_table.csv';
                a.click();
                URL.revokeObjectURL(url);
            }
        }
    };

    const handleExportPDF = async () => {
        try {
            const res = await exportData('pdf');
            const blob = new Blob([res.data], { type: 'application/pdf' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'executive_summary.pdf';
            a.click();
            URL.revokeObjectURL(url);
        } catch (err) {
            console.error('PDF export failed:', err);
        }
    };

    return (
        <div className="min-h-screen grid-bg">
            {/* Hero Section */}
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="pt-8 pb-6"
            >
                <div className="flex flex-col items-center px-6">
                    <div className="w-full max-w-3xl">
                        <div className="text-center mb-8">
                            <motion.h1
                                className="text-4xl font-bold gradient-text mb-3"
                                initial={{ opacity: 0, scale: 0.9 }}
                                animate={{ opacity: 1, scale: 1 }}
                                transition={{ delay: 0.2 }}
                            >
                                Competitive Intelligence Orchestrator
                            </motion.h1>
                            <p className="text-sm" style={{ color: '#64748b' }}>
                                Autonomous AI-powered competitive analysis for the IT services industry
                            </p>
                        </div>

                        {/* Query Input */}
                        <motion.div
                            className="glass-card max-w-3xl mx-auto"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.3 }}
                        >
                            <div className="flex gap-3">
                                <div className="relative flex-1">
                                    <FiSearch className="absolute left-4 top-1/2 -translate-y-1/2" style={{ color: '#64748b' }} size={18} />
                                    <input
                                        type="text"
                                        value={query}
                                        onChange={(e) => setQuery(e.target.value)}
                                        onKeyDown={(e) => e.key === 'Enter' && handleAnalyze()}
                                        placeholder="Ask a strategic question... e.g. How is Infosys positioning vs TCS in GenAI?"
                                        className="intel-input !pl-12"
                                    />
                                </div>
                                <button
                                    onClick={handleAnalyze}
                                    disabled={loading || !query.trim()}
                                    className="glow-btn flex items-center gap-2"
                                >
                                    {loading ? (
                                        <div className="loading-spinner !w-5 !h-5 !border-2" />
                                    ) : (
                                        <>
                                            <FiZap size={16} /> Analyze
                                        </>
                                    )}
                                </button>
                            </div>

                            {/* Quick Queries */}
                            <div className="flex flex-wrap justify-center gap-2 mt-3">
                                {QUICK_QUERIES.map((q, i) => (
                                    <button
                                        key={i}
                                        onClick={() => setQuery(q)}
                                        className="text-xs px-3 py-1.5 rounded-full transition-all"
                                        style={{
                                            background: 'rgba(124, 58, 237, 0.08)',
                                            color: '#94a3b8',
                                            border: '1px solid rgba(124, 58, 237, 0.15)',
                                        }}
                                        onMouseEnter={(e) => {
                                            e.target.style.background = 'rgba(124, 58, 237, 0.18)';
                                            e.target.style.color = '#c084fc';
                                        }}
                                        onMouseLeave={(e) => {
                                            e.target.style.background = 'rgba(124, 58, 237, 0.08)';
                                            e.target.style.color = '#94a3b8';
                                        }}
                                    >
                                        {q.length > 50 ? q.slice(0, 47) + '...' : q}
                                    </button>
                                ))}
                            </div>
                        </motion.div>
                    </div>
                </div>
            </motion.div>

            {/* Loading State */}
            <AnimatePresence>
                {loading && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="flex flex-col items-center gap-4 py-12"
                    >
                        <div className="loading-spinner" />
                        <div className="flex items-center gap-2 text-sm" style={{ color: '#a855f7' }}>
                            <FiActivity className="animate-pulse" />
                            <span>Running intelligence pipeline...</span>
                        </div>
                        <div className="flex gap-2 mt-2">
                            {['Crawling', 'Extracting', 'Building Graph', 'Reasoning', 'Summarizing'].map((step, i) => (
                                <motion.span
                                    key={step}
                                    initial={{ opacity: 0.3 }}
                                    animate={{ opacity: [0.3, 1, 0.3] }}
                                    transition={{ delay: i * 0.8, duration: 2, repeat: Infinity }}
                                    className="text-xs px-2 py-1 rounded"
                                    style={{ background: 'rgba(124,58,237,0.1)', color: '#94a3b8' }}
                                >
                                    {step}
                                </motion.span>
                            ))}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Results */}
            {!loading && (graphData || comparison || summary) && (
                <div className="w-full flex justify-center px-6 pb-8 mt-8">
                    <div className="w-full max-w-6xl">
                        {/* Tab Bar Results Header */}
                        <div className="flex justify-center mb-8 results-header">
                            <div className="inline-flex items-center gap-0.5 p-1 rounded-xl"
                                style={{ background: 'rgba(124,58,237,0.08)', border: '1px solid rgba(124,58,237,0.15)' }}>
                                {[
                                    { id: 'graph', label: 'Knowledge Graph', icon: '🕸️' },
                                    { id: 'summary', label: 'Executive Summary', icon: '📊' },
                                    { id: 'table', label: 'Comparison Table', icon: '📋' },
                                ].map((tab) => (
                                    <button
                                        key={tab.id}
                                        onClick={() => setActiveTab(tab.id)}
                                        className="px-3 py-1.5 rounded-lg text-xs font-semibold tracking-wide transition-all"
                                        style={{
                                            background: activeTab === tab.id ? 'rgba(124,58,237,0.3)' : 'transparent',
                                            color: activeTab === tab.id ? '#c084fc' : '#64748b',
                                            boxShadow: activeTab === tab.id ? '0 2px 8px rgba(124,58,237,0.2)' : 'none',
                                        }}
                                    >
                                        {tab.icon} {tab.label}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Content */}
                        <AnimatePresence mode="wait">
                            {activeTab === 'graph' && (
                                <motion.div
                                    key="graph"
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -10 }}
                                    className="grid grid-cols-1 lg:grid-cols-12 gap-6"
                                >
                                    {/* Graph - 2 columns */}
                                    <div className="col-span-12 lg:col-span-8 glass-card !p-2" style={{ height: '600px' }}>
                                        <GraphView graphData={graphData} onNodeClick={(n) => console.log('Node clicked:', n)} />
                                    </div>
                                    {/* Summary - 1 column */}
                                    <div className="col-span-12 lg:col-span-4 overflow-y-auto" style={{ maxHeight: '600px' }}>
                                        <ExecutiveSummary summary={summary} reasoning={results?.reasoning} />
                                    </div>
                                </motion.div>
                            )}

                            {activeTab === 'summary' && (
                                <motion.div
                                    key="summary"
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -10 }}
                                    className="w-full flex justify-center"
                                >
                                    <div className="w-full max-w-6xl">
                                        <ExecutiveSummary summary={summary} reasoning={results?.reasoning} />
                                        <div className="flex justify-center gap-3 mt-6">
                                            <button onClick={handleExportPDF} className="glow-btn flex items-center gap-2 text-sm">
                                                <FiDownload size={14} /> Export PDF
                                            </button>
                                            <button
                                                onClick={async () => {
                                                    try {
                                                        const res = await exportData('json');
                                                        const blob = new Blob([JSON.stringify(res.data, null, 2)], { type: 'application/json' });
                                                        const url = URL.createObjectURL(blob);
                                                        const a = document.createElement('a');
                                                        a.href = url;
                                                        a.download = 'intelligence_report.json';
                                                        a.click();
                                                        URL.revokeObjectURL(url);
                                                    } catch (err) { console.error(err); }
                                                }}
                                                className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium transition-all"
                                                style={{ background: 'rgba(124,58,237,0.15)', color: '#a855f7', border: '1px solid rgba(124,58,237,0.3)' }}
                                            >
                                                <FiDownload size={14} /> Export JSON
                                            </button>
                                        </div>
                                    </div>
                                </motion.div>
                            )}

                            {activeTab === 'table' && (
                                <motion.div
                                    key="table"
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -10 }}
                                >
                                    <ComparisonTable data={comparison} onExportCSV={handleExportCSV} />
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>
                </div>
            )}

            {/* Metrics Bar (always visible) */}
            {!loading && !graphData && !comparison && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.6 }}
                    className="mt-24 pb-12"
                >
                    <div className="flex justify-center px-6">
                        <div className="w-full max-w-3xl grid grid-cols-2 md:grid-cols-5 gap-4">
                            {[
                                { label: 'Companies Tracked', value: '5', color: '#3b82f6' },
                                { label: 'Graph Nodes', value: '34', color: '#a855f7' },
                                { label: 'Relationships', value: '42', color: '#10b981' },
                                { label: 'AI Brands', value: '5', color: '#f59e0b' },
                                { label: 'Risk Score', value: '68', color: '#ef4444' },
                            ].map((m, i) => (
                                <motion.div
                                    key={m.label}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 0.7 + i * 0.1 }}
                                    className="glass-card text-center"
                                >
                                    <div className="text-3xl font-bold mb-1" style={{ color: m.color }}>{m.value}</div>
                                    <div className="text-xs" style={{ color: '#94a3b8' }}>{m.label}</div>
                                </motion.div>
                            ))}
                        </div>
                    </div>
                </motion.div>
            )}
        </div>
    );
}
