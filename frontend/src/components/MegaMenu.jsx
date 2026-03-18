import { useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import '../styles/dropdown.css';

/* ─────────────────────────────────────────────────────────────
   MegaMenu — positioned dropdown panel for the "All Tools" button.

   Props:
     isOpen   — boolean
     onClose  — fn()  called on click-outside, Escape, or link click
───────────────────────────────────────────────────────────── */

export const TOOL_CATEGORIES = [
    {
        label: 'Organize',
        tools: [
            { id: 'merge-pdf', name: 'Merge PDF' },
            { id: 'split-pdf', name: 'Split PDF' },
            { id: 'rotate-pdf', name: 'Rotate PDF' },
            { id: 'organize-pages', name: 'Organize Pages' },
            { id: 'add-page-numbers', name: 'Add Page Numbers' },
        ],
    },
    {
        label: 'Convert',
        tools: [
            { id: 'pdf-to-word', name: 'PDF to Word' },
            { id: 'pdf-to-excel', name: 'PDF to Excel' },
            { id: 'pdf-to-jpg', name: 'PDF to JPG' },
            { id: 'word-to-pdf', name: 'Word to PDF' },
            { id: 'excel-to-pdf', name: 'Excel to PDF' },
        ],
    },
    {
        label: 'Optimize',
        tools: [
            { id: 'compress-pdf', name: 'Compress PDF' },
            { id: 'repair-pdf', name: 'Repair PDF' },
            { id: 'flatten-pdf', name: 'Flatten PDF' },
        ],
    },
    {
        label: 'Security',
        tools: [
            { id: 'protect-pdf', name: 'Protect PDF' },
            { id: 'unlock-pdf', name: 'Unlock PDF' },
            { id: 'watermark-pdf', name: 'Watermark PDF' },
            { id: 'redact-pdf', name: 'Redact PDF' },
        ],
    },
    {
        label: 'Image Tools',
        tools: [
            { id: 'jpg-to-pdf', name: 'JPG to PDF' },
            { id: 'png-to-pdf', name: 'PNG to PDF' },
            { id: 'image-to-text', name: 'Image to Text' },
            { id: 'remove-bg', name: 'Remove Background' },
        ],
    },
    {
        label: 'AI Tools',
        tools: [
            { id: 'chat-with-pdf', name: 'Chat with PDF' },
            { id: 'summarize-pdf', name: 'Summarize PDF' },
            { id: 'ai-detector', name: 'AI Detector' },
            { id: 'translate-pdf', name: 'Translate PDF' },
        ],
    },
];

const panelVariants = {
    hidden: {
        opacity: 0,
        y: -10,
        scale: 0.98,
        transition: { duration: 0.15, ease: 'easeOut' },
    },
    visible: {
        opacity: 1,
        y: 0,
        scale: 1,
        transition: { 
            duration: 0.3, 
            ease: [0.16, 1, 0.3, 1],
            staggerChildren: 0.05
        },
    },
};

const itemVariants = {
    hidden: { opacity: 0, x: -5 },
    visible: { opacity: 1, x: 0 },
};

export default function MegaMenu({ isOpen, onClose }) {
    const panelRef = useRef(null);

    /* Escape to close */
    useEffect(() => {
        if (!isOpen) return;
        const onKey = (e) => { if (e.key === 'Escape') onClose(); };
        document.addEventListener('keydown', onKey);
        return () => document.removeEventListener('keydown', onKey);
    }, [isOpen, onClose]);

    return (
        <AnimatePresence>
            {isOpen && (
                <motion.div
                    ref={panelRef}
                    className="mega-menu"
                    role="dialog"
                    aria-label="All PDF Tools"
                    variants={panelVariants}
                    initial="hidden"
                    animate="visible"
                    exit="hidden"
                >
                    {/* Tool columns */}
                    {TOOL_CATEGORIES.map((cat) => (
                        <div key={cat.label} className="mega-menu__col">
                            <h4 className="mega-menu__cat">{cat.label}</h4>
                            {cat.tools.map((tool) => (
                                <motion.div key={tool.id} variants={itemVariants}>
                                    <Link
                                        to={`/tool/${tool.id}`}
                                        className="mega-menu__link"
                                        onClick={onClose}
                                    >
                                        {tool.name}
                                    </Link>
                                </motion.div>
                            ))}
                        </div>
                    ))}

                    {/* Footer */}
                    <div className="mega-menu__footer">
                        <span className="mega-menu__footer-text">
                            ✨ 20+ Free AI-Powered PDF Tools — No signup required
                        </span>
                        <Link to="/" className="mega-menu__view-all" onClick={onClose}>
                            Browse all tools →
                        </Link>
                    </div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}

