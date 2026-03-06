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
        label: 'Organize PDF',
        tools: [
            { id: 'merge-pdf', name: 'Merge PDF' },
            { id: 'split-pdf', name: 'Split PDF' },
            { id: 'rotate-pdf', name: 'Rotate PDF' },
            { id: 'organize-pages', name: 'Organize Pages' },
            { id: 'add-page-numbers', name: 'Add Page Numbers' },
            { id: 'crop-pdf', name: 'Crop PDF' },
        ],
    },
    {
        label: 'Convert PDF',
        tools: [
            { id: 'pdf-to-word', name: 'PDF to Word' },
            { id: 'pdf-to-excel', name: 'PDF to Excel' },
            { id: 'pdf-to-jpg', name: 'PDF to JPG' },
            { id: 'word-to-pdf', name: 'Word to PDF' },
            { id: 'excel-to-pdf', name: 'Excel to PDF' },
            { id: 'images-to-pdf', name: 'Images to PDF' },
        ],
    },
    {
        label: 'Optimize PDF',
        tools: [
            { id: 'compress-pdf', name: 'Compress PDF' },
            { id: 'repair-pdf', name: 'Repair PDF' },
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
        label: 'Advanced',
        tools: [
            { id: 'ocr-pdf', name: 'OCR PDF' },
            { id: 'compare-pdf', name: 'Compare PDF' },
            { id: 'scan-to-pdf', name: 'Scan to PDF' },
            { id: 'translate-pdf', name: 'Translate PDF' },
        ],
    },
];

const panelVariants = {
    hidden: {
        opacity: 0,
        y: -14,
        scale: 0.975,
        transition: { duration: 0.14, ease: 'easeIn' },
    },
    visible: {
        opacity: 1,
        y: 0,
        scale: 1,
        transition: { duration: 0.2, ease: [0.16, 1, 0.3, 1] },
    },
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
                            <p className="mega-menu__cat">{cat.label}</p>
                            {cat.tools.map((tool) => (
                                <Link
                                    key={tool.id}
                                    to={`/tool/${tool.id}`}
                                    className="mega-menu__link"
                                    onClick={onClose}
                                >
                                    {tool.name}
                                </Link>
                            ))}
                        </div>
                    ))}

                    {/* Footer */}
                    <div className="mega-menu__footer">
                        <span className="mega-menu__footer-text">
                            23 free tools — no sign-up required
                        </span>
                        <Link to="/" className="mega-menu__view-all" onClick={onClose}>
                            Browse all →
                        </Link>
                    </div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
