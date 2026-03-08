import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
    FiFilePlus, FiScissors, FiZap, FiLock, FiUnlock, FiFileText,
    FiImage, FiDroplet, FiRefreshCw, FiGrid, FiSearch, FiGlobe,
} from 'react-icons/fi';

/**
 * RelatedTools — shows a small grid of other tool shortcuts.
 *
 * Props:
 *   currentTool — slug of the current tool (to exclude from list)
 *   count       — max cards to show (default 4)
 */

const ALL_TOOLS = [
    { id: 'merge-pdf', name: 'Merge PDF', icon: FiFilePlus, color: '#6366f1' },
    { id: 'split-pdf', name: 'Split PDF', icon: FiScissors, color: '#ec4899' },
    { id: 'compress-pdf', name: 'Compress PDF', icon: FiZap, color: '#10b981' },
    { id: 'pdf-to-word', name: 'PDF to Word', icon: FiFileText, color: '#3b82f6' },
    { id: 'pdf-to-excel', name: 'PDF to Excel', icon: FiGrid, color: '#22c55e' },
    { id: 'word-to-pdf', name: 'Word to PDF', icon: FiGrid, color: '#3b82f6' },
    { id: 'pdf-to-jpg', name: 'PDF to JPG', icon: FiImage, color: '#f97316' },
    { id: 'images-to-pdf', name: 'Images to PDF', icon: FiImage, color: '#8b5cf6' },
    { id: 'protect-pdf', name: 'Protect PDF', icon: FiLock, color: '#0ea5e9' },
    { id: 'unlock-pdf', name: 'Unlock PDF', icon: FiUnlock, color: '#6366f1' },
    { id: 'watermark-pdf', name: 'Watermark PDF', icon: FiDroplet, color: '#06b6d4' },
    { id: 'rotate-pdf', name: 'Rotate PDF', icon: FiRefreshCw, color: '#14b8a6' },
    { id: 'ocr-pdf', name: 'OCR PDF', icon: FiSearch, color: '#fbbf24' },
    { id: 'translate-pdf', name: 'Translate PDF', icon: FiGlobe, color: '#34d399' },
];

export default function RelatedTools({ currentTool = '', count = 4 }) {
    const tools = ALL_TOOLS.filter((t) => t.id !== currentTool).slice(0, count);

    return (
        <section className="related-tools">
            <h2 className="related-tools__heading">Related Tools</h2>
            <div className="related-tools__grid">
                {tools.map((tool, i) => {
                    const Icon = tool.icon;
                    return (
                        <motion.div
                            key={tool.id}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true, margin: '-20px' }}
                            transition={{ duration: 0.35, delay: i * 0.07 }}
                            whileHover={{ y: -4, transition: { type: 'spring', stiffness: 350, damping: 22 } }}
                        >
                            <Link to={`/tool/${tool.id}`} className="related-tool-card">
                                {/* Icon badge */}
                                <div
                                    className="related-tool-card__icon"
                                    style={{
                                        background: `${tool.color}18`,
                                        color: tool.color,
                                    }}
                                >
                                    <Icon />
                                </div>
                                <span className="related-tool-card__name">{tool.name}</span>
                            </Link>
                        </motion.div>
                    );
                })}
            </div>
        </section>
    );
}
