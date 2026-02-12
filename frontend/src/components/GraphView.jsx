import { useState, useEffect, useRef, useCallback } from 'react';
import CytoscapeComponent from 'react-cytoscapejs';
import { motion, AnimatePresence } from 'framer-motion';

const NODE_COLORS = {
    Company: { main: '#3b82f6', border: '#60a5fa', highlight: '#93c5fd' },
    Product: { main: '#a855f7', border: '#c084fc', highlight: '#d8b4fe' },
    Partner: { main: '#10b981', border: '#34d399', highlight: '#6ee7b7' },
    Region: { main: '#f59e0b', border: '#fbbf24', highlight: '#fde68a' },
    Investment: { main: '#ef4444', border: '#f87171', highlight: '#fca5a5' },
};

const INFOSYS_COLOR = { main: '#0066cc', border: '#3399ff', highlight: '#66b2ff' };

const cytoscapeStylesheet = [
    {
        selector: 'node',
        style: {
            label: 'data(name)',
            'text-valign': 'bottom',
            'text-halign': 'center',
            'font-size': '11px',
            color: '#cbd5e1',
            'text-margin-y': 8,
            'text-outline-width': 2,
            'text-outline-color': '#0a0a14',
            width: 45,
            height: 45,
            'background-opacity': 0.9,
            'border-width': 2,
            'transition-property': 'background-color, border-color, width, height',
            'transition-duration': '0.3s',
        },
    },
    ...Object.entries(NODE_COLORS).map(([label, colors]) => ({
        selector: `node[label="${label}"]`,
        style: {
            'background-color': colors.main,
            'border-color': colors.border,
        },
    })),
    {
        selector: 'node[name="Infosys"]',
        style: {
            'background-color': INFOSYS_COLOR.main,
            'border-color': INFOSYS_COLOR.border,
            width: 65,
            height: 65,
            'font-size': '13px',
            'font-weight': 'bold',
            'border-width': 3,
        },
    },
    {
        selector: 'edge',
        style: {
            width: 1.5,
            'line-color': 'rgba(124 ,58, 237, 0.3)',
            'target-arrow-color': 'rgba(124, 58, 237, 0.5)',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            label: 'data(relationship)',
            'font-size': '8px',
            color: '#64748b',
            'text-rotation': 'autorotate',
            'text-outline-width': 1.5,
            'text-outline-color': '#0a0a14',
            'transition-property': 'line-color, width',
            'transition-duration': '0.3s',
        },
    },
    {
        selector: 'edge:hover, node:hover',
        style: {},
    },
    {
        selector: 'node:active',
        style: {
            'overlay-opacity': 0,
        },
    },
];

const EDGE_COLORS = {
    COMPETES_WITH: '#ef4444',
    PARTNERS_WITH: '#10b981',
    INVESTS_IN: '#f59e0b',
    OFFERS: '#a855f7',
    USES: '#3b82f6',
    OPERATES_IN: '#64748b',
};

export default function GraphView({ graphData, onNodeClick }) {
    const [hoveredNode, setHoveredNode] = useState(null);
    const cyRef = useRef(null);

    const elements = buildElements(graphData);

    const handleCyReady = useCallback((cy) => {
        cyRef.current = cy;

        cy.on('mouseover', 'node', (evt) => {
            const node = evt.target;
            setHoveredNode(node.data());
            node.style({ width: 60, height: 60, 'border-width': 3, 'border-color': '#c084fc' });
            node.connectedEdges().style({ width: 3, 'line-color': '#a855f7', 'target-arrow-color': '#a855f7' });
        });

        cy.on('mouseout', 'node', (evt) => {
            const node = evt.target;
            setHoveredNode(null);
            const label = node.data('label');
            const name = node.data('name');
            const colors = name === 'Infosys' ? INFOSYS_COLOR : (NODE_COLORS[label] || NODE_COLORS.Company);
            const sz = name === 'Infosys' ? 65 : 45;
            node.style({ width: sz, height: sz, 'border-width': name === 'Infosys' ? 3 : 2, 'border-color': colors.border });
            node.connectedEdges().forEach((edge) => {
                const rel = edge.data('relationship');
                edge.style({ width: 1.5, 'line-color': EDGE_COLORS[rel] || 'rgba(124,58,237,0.3)', 'target-arrow-color': EDGE_COLORS[rel] || 'rgba(124,58,237,0.5)' });
            });
        });

        cy.on('tap', 'node', (evt) => {
            onNodeClick?.(evt.target.data());
        });

        // Apply edge colors
        cy.edges().forEach((edge) => {
            const rel = edge.data('relationship');
            if (EDGE_COLORS[rel]) {
                edge.style({ 'line-color': EDGE_COLORS[rel], 'target-arrow-color': EDGE_COLORS[rel] });
            }
        });

        // Layout — stable, non-physics config
        cy.layout({
            name: 'cose',
            animate: false,
            randomize: false,
            fit: true,
            padding: 60,
            nodeRepulsion: () => 400000,
            idealEdgeLength: () => 120,
            gravity: 0,
            numIter: 1000,
        }).run();

        // Lock nodes so they don't jump on hover/drag
        cy.nodes().ungrabify();
        cy.autolock(true);
    }, [onNodeClick]);

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            className="relative w-full h-full"
        >
            <CytoscapeComponent
                elements={elements}
                stylesheet={cytoscapeStylesheet}
                style={{ width: '100%', height: '100%', borderRadius: '12px' }}
                cy={handleCyReady}
                wheelSensitivity={0.3}
            />

            {/* Legend */}
            <div className="absolute bottom-4 left-4 flex flex-wrap gap-3">
                {Object.entries(NODE_COLORS).map(([label, colors]) => (
                    <div key={label} className="flex items-center gap-1.5 text-xs" style={{ color: '#94a3b8' }}>
                        <div className="w-3 h-3 rounded-full" style={{ backgroundColor: colors.main }} />
                        {label}
                    </div>
                ))}
            </div>

            {/* Hover tooltip */}
            <AnimatePresence>
                {hoveredNode && (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 10 }}
                        className="absolute top-4 right-4 glass-card !p-3"
                        style={{ minWidth: 160 }}
                    >
                        <div className="text-sm font-semibold" style={{ color: NODE_COLORS[hoveredNode.label]?.main || '#a855f7' }}>
                            {hoveredNode.name}
                        </div>
                        <div className="text-xs mt-1" style={{ color: '#94a3b8' }}>
                            Type: {hoveredNode.label}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
}

function buildElements(graphData) {
    if (!graphData) return [];
    const nodes = (graphData.nodes || []).map((n) => ({
        data: { id: n.id || n.name, name: n.name, label: n.label },
    }));
    const edges = (graphData.edges || []).map((e, i) => ({
        data: { id: `e${i}`, source: e.source, target: e.target, relationship: e.relationship },
    }));
    return [...nodes, ...edges];
}
