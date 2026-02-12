import { useState } from 'react';
import { motion } from 'framer-motion';
import { FiDownload, FiChevronUp, FiChevronDown } from 'react-icons/fi';

export default function ComparisonTable({ data, onExportCSV }) {
    const [sortKey, setSortKey] = useState(null);
    const [sortDir, setSortDir] = useState('asc');

    if (!data || data.length === 0) return null;

    const columns = Object.keys(data[0]);
    const companies = columns.filter((c) => c !== 'category');

    const handleSort = (col) => {
        if (sortKey === col) {
            setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
        } else {
            setSortKey(col);
            setSortDir('asc');
        }
    };

    const sorted = [...data].sort((a, b) => {
        if (!sortKey) return 0;
        const va = a[sortKey] || '';
        const vb = b[sortKey] || '';
        return sortDir === 'asc' ? va.localeCompare(vb) : vb.localeCompare(va);
    });

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="glass-card"
        >
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold gradient-text">Competitive Comparison</h3>
                <button
                    onClick={onExportCSV}
                    className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all"
                    style={{
                        background: 'rgba(124, 58, 237, 0.15)',
                        color: '#a855f7',
                        border: '1px solid rgba(124, 58, 237, 0.3)',
                    }}
                    onMouseEnter={(e) => { e.target.style.background = 'rgba(124, 58, 237, 0.25)'; }}
                    onMouseLeave={(e) => { e.target.style.background = 'rgba(124, 58, 237, 0.15)'; }}
                >
                    <FiDownload size={14} /> Export CSV
                </button>
            </div>

            <div className="overflow-x-auto" style={{ maxHeight: '400px', overflowY: 'auto' }}>
                <table className="intel-table">
                    <thead>
                        <tr>
                            {columns.map((col) => (
                                <th
                                    key={col}
                                    onClick={() => handleSort(col)}
                                    style={{ cursor: 'pointer', userSelect: 'none' }}
                                >
                                    <div className="flex items-center gap-1">
                                        {col === 'category' ? 'Category' : col}
                                        {sortKey === col && (
                                            sortDir === 'asc' ? <FiChevronUp size={12} /> : <FiChevronDown size={12} />
                                        )}
                                    </div>
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {sorted.map((row, i) => (
                            <motion.tr
                                key={i}
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: i * 0.03 }}
                            >
                                {columns.map((col) => (
                                    <td
                                        key={col}
                                        style={{
                                            fontWeight: col === 'category' ? 600 : 400,
                                            color: col === 'category' ? '#c084fc' : undefined,
                                            whiteSpace: 'nowrap',
                                        }}
                                    >
                                        {col === 'Infosys' ? (
                                            <span style={{ color: '#60a5fa', fontWeight: 600 }}>{row[col]}</span>
                                        ) : (
                                            row[col]
                                        )}
                                    </td>
                                ))}
                            </motion.tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </motion.div>
    );
}
