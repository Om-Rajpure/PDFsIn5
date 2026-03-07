import { useState, useCallback, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import {
    FiChevronRight, FiZap, FiFilePlus, FiScissors, FiLock,
    FiUnlock, FiDroplet, FiFileText, FiImage, FiRefreshCw,
    FiSearch, FiTool, FiArrowRight, FiList,
} from 'react-icons/fi';

import FileUploader from '../components/FileUploader';
import ProcessingLoader from '../components/ProcessingLoader';
import DownloadResult from '../components/DownloadResult';
import OrganizeWorkspace from '../components/OrganizeWorkspace';
import RelatedTools from '../components/RelatedTools';
import Button from '../components/Button';
import SEO from '../components/SEO';
import AdPlaceholder from '../components/AdPlaceholder';
import '../styles/toolpage.css';

/* ─────────────────────────────────────────────────────
   Tool metadata registry — drives title, description,
   accept string, multiple-upload flag, icon, options.
───────────────────────────────────────────────────── */
const TOOL_META = {
    'merge-pdf': {
        title: 'Merge PDF',
        desc: 'Combine multiple PDF files into one document. Drag to reorder pages before merging.',
        accept: '.pdf,application/pdf',
        multiple: true,
        icon: FiFilePlus,
        color: '#6366f1',
        options: [
            {
                id: 'order', label: 'Page Order', type: 'select',
                choices: ['Keep original order', 'Reverse order']
            },
        ],
    },
    'split-pdf': {
        title: 'Split PDF',
        desc: 'Extract one or more pages from a PDF file or split every page into separate files.',
        accept: '.pdf,application/pdf',
        multiple: false,
        icon: FiScissors,
        color: '#ec4899',
        options: [
            {
                id: 'mode', label: 'Split Mode', type: 'select',
                choices: ['Split every page', 'Extract range']
            },
            { id: 'range', label: 'Page Range (e.g. 1-3,5)', type: 'text', placeholder: '1-3,5' },
        ],
    },
    'compress-pdf': {
        title: 'Compress PDF',
        desc: 'Reduce PDF file size while maintaining the best possible quality.',
        accept: '.pdf,application/pdf',
        multiple: false,
        icon: FiZap,
        color: '#10b981',
        options: [
            {
                id: 'quality', label: 'Compression Level', type: 'select',
                choices: ['Extreme compression (smallest)', 'Recommended', 'Less compression (best quality)']
            },
        ],
    },
    'pdf-to-word': {
        title: 'PDF to Word',
        desc: 'Convert PDF documents to editable Word (.docx) files with formatting preserved.',
        accept: '.pdf,application/pdf',
        multiple: false,
        icon: FiFileText,
        color: '#3b82f6',
        options: [
            { id: 'format', label: 'Output Format', type: 'select', choices: ['.docx (Word)', '.doc (Older Word)'] },
        ],
    },
    'word-to-pdf': {
        title: 'Word to PDF',
        desc: 'Convert Microsoft Word documents (.docx, .doc) to PDF format.',
        accept: '.docx,.doc,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        multiple: false,
        icon: FiFileText,
        color: '#3b82f6',
        options: [],
    },
    'pdf-to-jpg': {
        title: 'PDF to JPG',
        desc: 'Convert each page of your PDF into a high-quality image file.',
        accept: '.pdf,application/pdf',
        multiple: false,
        icon: FiImage,
        color: '#f97316',
        options: [
            { id: 'quality', label: 'Image Quality', type: 'select', choices: ['High (300 DPI)', 'Medium (150 DPI)', 'Low (72 DPI)'] },
        ],
    },
    'images-to-pdf': {
        title: 'Images to PDF',
        desc: 'Combine multiple images (JPG, PNG, WEBP) into a single PDF document.',
        accept: 'image/jpeg,image/png,image/webp,.jpg,.jpeg,.png,.webp',
        multiple: true,
        icon: FiImage,
        color: '#8b5cf6',
        options: [
            { id: 'orientation', label: 'Orientation', type: 'select', choices: ['Portrait', 'Landscape'] },
            { id: 'margin', label: 'Page Margin', type: 'select', choices: ['No margin', 'Small margin', 'Large margin'] },
        ],
    },
    'protect-pdf': {
        title: 'Protect PDF',
        desc: 'Add a password to your PDF file to prevent unauthorized access.',
        accept: '.pdf,application/pdf',
        multiple: false,
        icon: FiLock,
        color: '#0ea5e9',
        options: [
            { id: 'password', label: 'Set Password', type: 'text', placeholder: 'Enter a strong password' },
        ],
    },
    'unlock-pdf': {
        title: 'Unlock PDF',
        desc: 'Remove password protection from a PDF file you have permission to access.',
        accept: '.pdf,application/pdf',
        multiple: false,
        icon: FiUnlock,
        color: '#6366f1',
        options: [
            { id: 'password', label: 'Current Password', type: 'text', placeholder: 'Enter the PDF password' },
        ],
    },
    'watermark-pdf': {
        title: 'Watermark PDF',
        desc: 'Add a custom text or image watermark to your PDF pages.',
        accept: '.pdf,application/pdf',
        multiple: false,
        icon: FiDroplet,
        color: '#06b6d4',
        options: [
            { id: 'text', label: 'Watermark Text', type: 'text', placeholder: 'e.g. CONFIDENTIAL' },
            { id: 'opacity', label: 'Opacity', type: 'select', choices: ['25%', '50%', '75%', '100%'] },
            { id: 'position', label: 'Position', type: 'select', choices: ['Center (diagonal)', 'Center', 'Bottom right'] },
        ],
    },
    'ocr-pdf': {
        title: 'OCR PDF',
        desc: 'Make scanned PDFs searchable by extracting text using optical character recognition.',
        accept: '.pdf,application/pdf',
        multiple: false,
        icon: FiSearch,
        color: '#fbbf24',
        options: [
            {
                id: 'lang', label: 'Document Language', type: 'select',
                choices: ['English', 'Spanish', 'French', 'German', 'Hindi', 'Arabic', 'Chinese']
            },
        ],
    },
    'repair-pdf': {
        title: 'Repair PDF',
        desc: 'Try to recover and repair a corrupted or damaged PDF file.',
        accept: '.pdf,application/pdf',
        multiple: false,
        icon: FiTool,
        color: '#ef4444',
        options: [],
    },
    'rotate-pdf': {
        title: 'Rotate PDF',
        desc: 'Rotate all or specific pages of a PDF to fix orientation.',
        accept: '.pdf,application/pdf',
        multiple: false,
        icon: FiRefreshCw,
        color: '#14b8a6',
        options: [
            { id: 'angle', label: 'Rotation', type: 'select', choices: ['90° clockwise', '180°', '270° clockwise'] },
            { id: 'apply_to', label: 'Apply to', type: 'select', choices: ['All pages', 'Specific page range'] },
            { id: 'range', label: 'Page Range (e.g. 1-3,5)', type: 'text', placeholder: '1-3,5' },
        ],
    },
    'organize-pages': {
        title: 'Organize Pages',
        desc: 'Sort, add and delete PDF pages. Drag and drop the page thumbnails to rearrange them.',
        accept: '.pdf,application/pdf',
        multiple: false,
        icon: FiList,
        color: '#f59e0b',
        options: [],
    },
};

/* fallback for unknown tool slugs */
const fallbackMeta = (slug) => {
    const safeSlug = typeof slug === 'string' ? slug : 'unknown-tool';
    return {
        title: safeSlug.split('-').map((w) => w[0].toUpperCase() + w.slice(1)).join(' '),
        desc: 'Upload your file and process it instantly in the browser.',
        accept: '.pdf,application/pdf',
        multiple: false,
        icon: FiZap,
        color: '#6366f1',
        options: [],
    };
};

/* ─────────────────────────────────────────────────────
   SEO article content per tool
───────────────────────────────────────────────────── */
const SEO_CONTENT = {
    'merge-pdf': {
        articleTitle: 'How to Merge PDF Files Online for Free',
        body: `Combining multiple PDFs into a single document is one of the most common document tasks.
           Whether you're assembling a report, combining contracts, or merging scanned pages,
           PDFsIn5 makes it effortless. Simply upload your files, reorder them by dragging, and
           download a perfectly merged PDF in seconds — no software installation required.`,
    },
    'compress-pdf': {
        articleTitle: 'How to Compress a PDF Without Losing Quality',
        body: `Large PDF files are hard to share via email or upload to portals. PDFsIn5's smart
           compression reduces file sizes by up to 80% while preserving readability. Choose your
           compression level — from extreme (smallest size) to light (best quality) — and download
           your optimised file in moments.`,
    },
    'images-to-pdf': {
        articleTitle: 'Convert Images to PDF Online in Seconds',
        body: `Need to combine JPG, PNG, or WEBP images into a single PDF? Upload your images,
           choose your page orientation and margins, and PDFsIn5 will bundle them into a
           clean, ready-to-share PDF document. Perfect for creating photo albums, document
           scans, and visual reports.`,
    },
    'organize-pages': {
        articleTitle: 'How to Organize PDF Pages Online',
        body: `Delete, reorder, and arrange PDF pages easily. Upload your document and visually sort pages using our drag-and-drop tool to create the perfect PDF file.`,
    },
};

/* page-level animation */
const pageFade = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { duration: 0.35 } },
};

/* ═══════════════════════════════════════════════════════
   ToolPage
═══════════════════════════════════════════════════════ */
export default function ToolPage() {
    const { toolName = '' } = useParams();
    const meta = TOOL_META[toolName] ?? fallbackMeta(toolName);
    const Icon = meta.icon;

    /* state */
    const [files, setFiles] = useState([]);
    const [options, setOptions] = useState({});
    const [status, setStatus] = useState('idle'); // idle | processing | done | error
    const [downloadUrl, setDownloadUrl] = useState(null);
    const [resultName, setResultName] = useState('');
    const [errorMsg, setErrorMsg] = useState('');

    const [pagePreviews, setPagePreviews] = useState([]);
    const [pageOrder, setPageOrder] = useState([]);

    useEffect(() => {
        if (toolName === 'organize-pages' && files.length > 0 && status === 'idle') {
            const fetchPreviews = async () => {
                setStatus('processing');
                try {
                    const formData = new FormData();
                    formData.append('file', files[0]);
                    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
                    const res = await axios.post(`${apiUrl}/api/pdf-pages-preview`, formData);
                    setPagePreviews(res.data.previews);
                    setPageOrder(Array.from({ length: res.data.page_count }, (_, i) => i + 1));
                    setStatus('organizing');
                } catch (err) {
                    setErrorMsg(err?.response?.data?.detail ?? 'Failed to load previews.');
                    setStatus('error');
                }
            };
            fetchPreviews();
        }
    }, [files, toolName, status]);

    const seo = SEO_CONTENT[toolName] ?? {
        articleTitle: `How to Use the ${meta.title} Tool Online`,
        body: `The ${meta.title} tool lets you process your PDF documents entirely online, without
           installing any software. Simply upload your file, choose your settings, and download
           the result in seconds. All files are automatically deleted after one hour for your privacy.`,
    };

    /* Process handler */
    const handleProcess = useCallback(async () => {
        if (!files.length) return;
        setStatus('processing');
        setErrorMsg('');

        try {
            const formData = new FormData();
            files.forEach((f) => formData.append('files', f));
            Object.entries(options).forEach(([k, v]) => formData.append(k, v));

            if (toolName === 'organize-pages') {
                formData.delete('files');
                formData.append('file', files[0]);
                formData.append('page_order', JSON.stringify(pageOrder));
            }

            const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
            const res = await axios.post(
                `${apiUrl}/api/tools/${toolName}`,
                formData,
                { responseType: 'blob' },
            );

            const blob = new Blob([res.data], { type: res.headers['content-type'] ?? 'application/pdf' });
            const url = URL.createObjectURL(blob);
            const disposition = res.headers['content-disposition'] ?? '';
            const match = disposition.match(/filename="?([^"]+)"?/);
            const isZip = res.headers['content-type'] === 'application/zip';
            const name = match?.[1] ?? (isZip ? `${toolName}-result.zip` : `${toolName}-result.pdf`);

            setDownloadUrl(url);
            setResultName(name);
            setStatus('done');
        } catch (err) {
            setErrorMsg(err?.response?.data?.detail ?? 'An error occurred. Please try again.');
            setStatus('error');
        }
    }, [files, options, toolName]);

    const reset = () => {
        setFiles([]);
        setOptions({});
        setStatus('idle');
        if (downloadUrl) URL.revokeObjectURL(downloadUrl);
        setDownloadUrl(null);
        setResultName('');
        setErrorMsg('');
        setPagePreviews([]);
        setPageOrder([]);
    };

    const setOption = (id, val) => setOptions((prev) => ({ ...prev, [id]: val }));

    /* SEO Structured Data */
    const softwareAppSchema = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": `${meta.title} - PDFsIn5`,
        "operatingSystem": "Any",
        "applicationCategory": "UtilitiesApplication",
        "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "USD"
        },
        "description": seo.body.substring(0, 150).trim() + "..."
    };

    const faqSchema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": "Is this tool free?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Yes — all core tools on PDFsIn5 are completely free with no account required."
                }
            },
            {
                "@type": "Question",
                "name": "Are my files safe?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Absolutely. Your files are processed securely and deleted automatically within 1 hour."
                }
            }
        ]
    };

    return (
        <motion.div className="tool-page" variants={pageFade} initial="hidden" animate="visible">
            <SEO
                title={`${seo.articleTitle} — Free Online Tool`}
                description={seo.body.substring(0, 150).trim() + "..."}
                url={`/tool/${toolName}`}
                schema={[softwareAppSchema, faqSchema]}
            />

            {/* ══ HERO HEADER ══ */}
            <section className="tool-page__hero">
                <div className="tool-page__hero-bg" aria-hidden="true" />
                <div className="container tool-page__hero-inner">
                    {/* Breadcrumb */}
                    <nav className="tool-page__breadcrumb" aria-label="Breadcrumb">
                        <Link to="/">Home</Link>
                        <FiChevronRight />
                        <Link to="/#tools">All Tools</Link>
                        <FiChevronRight />
                        <span>{meta.title}</span>
                    </nav>

                    {/* Icon badge */}
                    <motion.div
                        className="tool-page__icon-badge"
                        style={{ background: `${meta.color}1A` }}
                        initial={{ scale: 0.8, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        transition={{ type: 'spring', stiffness: 260, damping: 18 }}
                    >
                        <Icon style={{ color: meta.color, fontSize: '1.8rem' }} />
                    </motion.div>

                    <motion.h1
                        className="tool-page__title"
                        initial={{ opacity: 0, y: 18 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.4, delay: 0.08 }}
                    >
                        {meta.title}
                    </motion.h1>
                    <motion.p
                        className="tool-page__sub"
                        initial={{ opacity: 0, y: 12 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.38, delay: 0.16 }}
                    >
                        {meta.desc}
                    </motion.p>
                </div>
            </section>

            {/* ══ MAIN CONTENT ── */}
            <div className="container">
                <div className="tool-page__main">

                    {/* ── LEFT AD COLUMN ── */}
                    <aside className="tool-page-ads left-col">
                        <AdPlaceholder format="vertical" style={{ height: '300px' }} />
                        <AdPlaceholder format="vertical" style={{ height: '300px' }} />
                    </aside>

                    {/* ── PRIMARY COLUMN ── */}
                    <div className="tool-page__primary">

                        <AnimatePresence mode="wait">

                            {/* IDLE / ERROR / ORGANIZING STATE */}
                            {(status === 'idle' || status === 'error' || status === 'organizing') && (
                                <motion.div
                                    key="upload"
                                    initial={{ opacity: 0, y: 12 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -8 }}
                                    transition={{ duration: 0.28 }}
                                    style={{ display: 'flex', flexDirection: 'column', gap: 20 }}
                                >
                                    {/* Upload drop zone */}
                                    {(status === 'idle' || status === 'error') && (
                                        <div className="tool-section">
                                            <p className="tool-section__heading">Upload File{meta.multiple ? 's' : ''}</p>
                                            <FileUploader
                                                accept={meta.accept}
                                                multiple={meta.multiple}
                                                files={files}
                                                onChange={setFiles}
                                            />

                                            {/* Trust Indicators directly beneath Upload */}
                                            <div style={{ marginTop: '16px', display: 'flex', flexWrap: 'wrap', gap: '16px', justifyContent: 'center', fontSize: 'var(--text-xs)', color: 'var(--clr-text-muted)' }}>
                                                <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><FiLock style={{ color: 'var(--clr-primary)' }} /> Files encrypted during transfer</span>
                                                <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><FiZap style={{ color: 'var(--clr-primary)' }} /> Auto-deleted after processing</span>
                                                <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><FiTool style={{ color: 'var(--clr-primary)' }} /> No account required</span>
                                            </div>
                                        </div>
                                    )}

                                    {/* Organize Workspace */}
                                    {status === 'organizing' && (
                                        <OrganizeWorkspace
                                            pageOrder={pageOrder}
                                            setPageOrder={setPageOrder}
                                            pagePreviews={pagePreviews}
                                        />
                                    )}

                                    {/* Options panel — only if tool has options & files selected */}
                                    {(files.length > 0 && meta.options.length > 0) && (
                                        <motion.div
                                            className="tool-section tool-page__options"
                                            initial={{ opacity: 0, height: 0 }}
                                            animate={{ opacity: 1, height: 'auto' }}
                                        >
                                            <p className="tool-section__heading">Options</p>
                                            <div className="tool-page__options-grid">
                                                {meta.options.map((opt) => {
                                                    // Condition: Only show "range" text input if "Extract range" mode is selected for Split PDF
                                                    if (toolName === 'split-pdf' && opt.id === 'range') {
                                                        const currentMode = options['mode'] ?? 'Split every page';
                                                        if (currentMode !== 'Extract range') return null;
                                                    }

                                                    // Condition: Only show "range" text input if "Specific page range" mode is selected for Rotate PDF
                                                    if (toolName === 'rotate-pdf' && opt.id === 'range') {
                                                        const currentApplyTo = options['apply_to'] ?? 'All pages';
                                                        if (currentApplyTo !== 'Specific page range') return null;
                                                    }

                                                    return (
                                                        <div key={opt.id} className="tool-option">
                                                            <label className="tool-option__label" htmlFor={`opt-${opt.id}`}>
                                                                {opt.label}
                                                            </label>
                                                            {opt.type === 'select' ? (
                                                                <select
                                                                    id={`opt-${opt.id}`}
                                                                    className="tool-option__select"
                                                                    value={options[opt.id] ?? ''}
                                                                    onChange={(e) => setOption(opt.id, e.target.value)}
                                                                >
                                                                    {opt.choices.map((c) => (
                                                                        <option key={c} value={c}>{c}</option>
                                                                    ))}
                                                                </select>
                                                            ) : (
                                                                <input
                                                                    id={`opt-${opt.id}`}
                                                                    type="text"
                                                                    className="tool-option__input"
                                                                    placeholder={opt.placeholder ?? ''}
                                                                    value={options[opt.id] ?? ''}
                                                                    onChange={(e) => setOption(opt.id, e.target.value)}
                                                                />
                                                            )}
                                                        </div>
                                                    );
                                                })}
                                            </div>
                                        </motion.div>
                                    )}

                                    {/* Error banner */}
                                    {status === 'error' && (
                                        <motion.div
                                            className="tool-page__error-banner"
                                            initial={{ opacity: 0, y: -8 }}
                                            animate={{ opacity: 1, y: 0 }}
                                        >
                                            ⚠️ {errorMsg}
                                        </motion.div>
                                    )}

                                    {/* Process button */}
                                    {((files.length > 0 && status === 'idle') || status === 'organizing') && (
                                        <motion.div
                                            className="tool-page__action"
                                            initial={{ opacity: 0, scale: 0.95 }}
                                            animate={{ opacity: 1, scale: 1 }}
                                            style={{ marginTop: '16px' }}
                                        >
                                            <Button
                                                size="lg"
                                                icon={<Icon />}
                                                iconEnd={<FiArrowRight />}
                                                disabled={false}
                                                onClick={handleProcess}
                                                style={{ width: '100%', justifyContent: 'center', padding: '16px', fontSize: 'var(--text-lg)' }}
                                            >
                                                Process {meta.title}
                                            </Button>
                                            <span className="tool-page__file-count">
                                                {files.length} file{files.length > 1 ? 's' : ''} ready
                                            </span>
                                        </motion.div>
                                    )}
                                </motion.div>
                            )}

                            {/* PROCESSING STATE */}
                            {status === 'processing' && (
                                <motion.div
                                    key="processing"
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    exit={{ opacity: 0 }}
                                    transition={{ duration: 0.22 }}
                                >
                                    <div className="tool-section">
                                        <ProcessingLoader
                                            message={`Processing your ${meta.title.toLowerCase()}…`}
                                        />
                                    </div>
                                </motion.div>
                            )}

                            {/* DONE STATE */}
                            {status === 'done' && (
                                <motion.div
                                    key="done"
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    exit={{ opacity: 0 }}
                                    transition={{ duration: 0.22 }}
                                >
                                    <div className="tool-section">
                                        <div style={{ textAlign: 'center', marginBottom: '16px' }}>
                                            <div style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', background: 'color-mix(in srgb, var(--color-success, #10b981) 15%, transparent)', color: 'var(--color-success, #10b981)', padding: '12px', borderRadius: '50%', marginBottom: '16px', fontSize: '2rem' }}>
                                                ✓
                                            </div>
                                            <h2 style={{ fontSize: 'var(--text-xl)', fontWeight: '700', color: 'var(--clr-text)' }}>Success! Result File Ready</h2>
                                            <p style={{ color: 'var(--clr-text-muted)', fontSize: '1rem', marginTop: 8 }}>Your document has been successfully processed.</p>
                                        </div>
                                        <DownloadResult
                                            downloadUrl={downloadUrl}
                                            filename={resultName}
                                            onReset={reset}
                                        />
                                    </div>
                                </motion.div>
                            )}

                        </AnimatePresence>
                    </div>

                    {/* ── RIGHT AD COLUMN ── */}
                    <aside className="tool-page-ads right-col">
                        <AdPlaceholder format="vertical" style={{ height: '300px' }} />
                        <AdPlaceholder format="vertical" style={{ height: '300px' }} />
                    </aside>

                </div>
            </div>

            {/* ── SEO SECTION & RELATED TOOLS ── */}
            <div className="tool-page__content-wrapper">
                <section className="tool-page__seo-article tool-page__article">
                    <AdPlaceholder format="fluid" className="tool-page__article-ad" />

                    <div className="tool-page__article-header">
                        <h2>{seo.articleTitle}</h2>
                        <p>{seo.body}</p>
                    </div>

                    <div className="tool-page__article-block">
                        <h3>How to use {meta.title}</h3>
                        <ol className="tool-page__how-to-list">
                            <li>Click <strong>"Upload File"</strong> or drag your file into the drop zone above.</li>
                            {meta.options.length > 0 && <li>Adjust the tool options to match your requirements.</li>}
                            <li>Click <strong>"Process File"</strong> to start the operation.</li>
                            <li>Download your result using the <strong>"Download"</strong> button.</li>
                            <li>Your file is automatically deleted within 1 hour for privacy.</li>
                        </ol>
                    </div>

                    <div className="tool-page__article-block">
                        <h3>Frequently Asked Questions</h3>
                        <div className="tool-page__faq-list">
                            <details>
                                <summary>Is this tool free?</summary>
                                <p>Yes — all core tools on PDFsIn5 are completely free with no account required.</p>
                            </details>
                            <details>
                                <summary>Are my files private?</summary>
                                <p>Absolutely. Files are stored temporarily only for processing and auto-deleted after 1 hour.</p>
                            </details>
                            <details>
                                <summary>What is the maximum file size?</summary>
                                <p>We support files up to 100 MB. For larger files, please contact us.</p>
                            </details>
                        </div>
                    </div>
                </section>

                <RelatedTools currentTool={toolName} count={4} />
            </div>

        </motion.div>
    );
}
