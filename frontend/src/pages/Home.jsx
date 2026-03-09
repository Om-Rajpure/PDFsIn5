import { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
    FiFilePlus, FiScissors, FiRefreshCw, FiList, FiHash, FiCrop,
    FiFileText, FiGrid, FiImage, FiFile, FiTable, FiMonitor, FiCamera,
    FiZap, FiTool,
    FiLock, FiUnlock, FiDroplet, FiEyeOff,
    FiSearch,
    FiArrowRight, FiSend, FiShield, FiDollarSign,
} from 'react-icons/fi';
import ToolCard from '../components/ToolCard';
import SectionTitle from '../components/SectionTitle';
import Button from '../components/Button';
import SEO from '../components/SEO';
import AdPlaceholder from '../components/AdPlaceholder';
import './Home.css';

/* ─── Tool data ─── */
const TOOLS = [
    // Organize
    { id: 'merge-pdf', title: 'Merge PDF', desc: 'Combine multiple PDF files into a single, unified document.', icon: FiFilePlus, color: '#6366f1', cat: 'Organize' },
    { id: 'split-pdf', title: 'Split PDF', desc: 'Separate one page or an entire set for easy conversion into independent PDF files.', icon: FiScissors, color: '#ec4899', cat: 'Organize' },
    { id: 'rotate-pdf', title: 'Rotate PDF', desc: 'Rotate your PDFs the way you need them. You can even rotate multiple PDFs at once!', icon: FiRefreshCw, color: '#14b8a6', cat: 'Organize' },
    { id: 'organize-pages', title: 'Organize Pages', desc: 'Sort, add and delete PDF pages. Drag and drop the page thumbnails to rearrange them.', icon: FiList, color: '#f59e0b', cat: 'Organize' },
    { id: 'add-page-numbers', title: 'Add Page Numbers', desc: 'Add page numbers into PDFs with ease. Choose your positions, dimensions, typography.', icon: FiHash, color: '#a855f7', cat: 'Organize' },
    { id: 'crop-pdf', title: 'Crop PDF', desc: 'Trim PDF margins, change PDF page size and crop out specific areas across multiple pages.', icon: FiCrop, color: '#f43f5e', cat: 'Organize' },
    // Convert
    { id: 'pdf-to-word', title: 'PDF to Word', desc: 'Easily convert your PDF files into an easy to edit DOC and DOCX formats.', icon: FiFileText, color: '#3b82f6', cat: 'Convert' },
    { id: 'pdf-to-excel', title: 'PDF to Excel', desc: 'Extract spreadsheet tables from a PDF document to an EXCEL spreadsheet.', icon: FiGrid, color: '#22c55e', cat: 'Convert' },
    { id: 'pdf-to-jpg', title: 'PDF to JPG', desc: 'Extract all images that are embedded in your PDF or convert each page to a JPG file.', icon: FiImage, color: '#f97316', cat: 'Convert' },
    { id: 'word-to-pdf', title: 'Word to PDF', desc: 'Make DOC and DOCX files easy to read by converting them to PDF format.', icon: FiFile, color: '#3b82f6', cat: 'Convert' },
    { id: 'excel-to-pdf', title: 'Excel to PDF', desc: 'Make your EXCEL spreadsheets easy to read by converting them to PDF.', icon: FiTable, color: '#22c55e', cat: 'Convert' },
    { id: 'ppt-to-pdf', title: 'PowerPoint to PDF', desc: 'Convert your POWERPOINT presentations to PDF to make them easy to share.', icon: FiMonitor, color: '#f97316', cat: 'Convert' },
    { id: 'images-to-pdf', title: 'Images to PDF', desc: 'Convert your images into a single PDF document. We support JPG, PNG, TIFF, GIF, and BMP.', icon: FiCamera, color: '#8b5cf6', cat: 'Convert' },
    // Optimize
    { id: 'compress-pdf', title: 'Compress PDF', desc: 'Reduce the file size of your PDF documents while keeping their native visual quality.', icon: FiZap, color: '#10b981', cat: 'Optimize' },
    { id: 'repair-pdf', title: 'Repair PDF', desc: 'Upload a corrupt or broken PDF and we will try to fix it and recover your data.', icon: FiTool, color: '#ef4444', cat: 'Optimize' },
    // Security
    { id: 'protect-pdf', title: 'Protect PDF', desc: 'Encrypt your PDF with a password to keep sensitive data perfectly secure.', icon: FiLock, color: '#0ea5e9', cat: 'Security' },
    { id: 'unlock-pdf', title: 'Unlock PDF', desc: 'Remove PDF password security, granting you the freedom to easily use your PDFs as you want.', icon: FiUnlock, color: '#6366f1', cat: 'Security' },
    { id: 'watermark-pdf', title: 'Watermark PDF', desc: 'Stamp an image or text over your PDF in seconds. Choose the typography, transparency and position.', icon: FiDroplet, color: '#06b6d4', cat: 'Security' },
    { id: 'redact-pdf', title: 'Redact PDF', desc: 'Permanently remove classified, confidential, or sensitive content from your PDF files.', icon: FiEyeOff, color: '#dc2626', cat: 'Security' },
    // Advanced
    { id: 'ocr-pdf', title: 'OCR PDF', desc: 'Convert any scanned document into a searchable and selectable text PDF.', icon: FiSearch, color: '#fbbf24', cat: 'Advanced' },
];

const CATEGORIES = ['All', 'Organize', 'Convert', 'Optimize', 'Security', 'Advanced'];

const FEATURES = [
    { icon: '🔒', title: 'Private & Secure', desc: 'Files deleted automatically after processing.' },
    { icon: '⚡', title: 'Blazing Fast', desc: 'Most operations complete in seconds.' },
    { icon: '🆓', title: '100% Free', desc: 'No account needed for core tools.' },
    { icon: '🌐', title: 'Any Device', desc: 'Works in any browser — nothing to install.' },
];

/* ─── Page-level fade-in ─── */
const pageFade = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { duration: 0.5 } },
};

export default function Home() {
    const [activeCategory, setActiveCategory] = useState('All');
    const filtered = activeCategory === 'All'
        ? TOOLS
        : TOOLS.filter((t) => t.cat === activeCategory);

    return (
        <motion.div className="home" variants={pageFade} initial="hidden" animate="visible">
            <SEO
                title="Every PDF task, done in 5 steps"
                description="Merge, split, compress, convert and protect PDF files directly in your browser. 100% Free and Secure online PDF tools."
                url="/"
            />

            {/* ── HERO ── */}
            <section className="hero">
                <div className="container hero__inner">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.05 }}
                    >
                        <span className="badge hero__badge">⚡ 20 Free PDF Tools — No sign-up required</span>
                    </motion.div>

                    <motion.h1
                        className="hero__title"
                        initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.55, delay: 0.12 }}
                    >
                        Every PDF task,<br />done in{' '}
                        <span className="hero__title-accent">5 steps</span>.
                    </motion.h1>

                    <motion.p
                        className="hero__sub"
                        initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.22 }}
                    >
                        Merge, split, compress, convert and protect PDF files —
                        directly in your browser, completely free and private.
                    </motion.p>

                    <motion.div
                        className="hero__cta"
                        initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.45, delay: 0.32 }}
                    >
                        <Button
                            as={Link}
                            size="lg"
                            icon={<FiFilePlus />}
                            iconEnd={<FiArrowRight />}
                            onClick={() => window.location.href = '/tool/merge-pdf'}
                        >
                            Start Merging PDFs
                        </Button>
                        <Button
                            size="lg"
                            variant="secondary"
                            onClick={() => document.getElementById('tools')?.scrollIntoView({ behavior: 'smooth' })}
                        >
                            Browse All Tools
                        </Button>
                    </motion.div>

                    {/* Stat pills */}
                    <motion.div
                        className="hero__stats"
                        initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6, delay: 0.5, staggerChildren: 0.1 }}
                    >
                        {[
                            { icon: <FiZap />, n: '20', l: 'Powerful PDF Tools' },
                            { icon: <FiSend />, n: '<5s', l: 'File Processing Time' },
                            { icon: <FiShield />, n: 'Secure', l: '& Private Processing' },
                            { icon: <FiDollarSign />, n: '100% Free', l: 'No Sign-Up Required' },
                        ].map((s, idx) => (
                            <motion.div
                                key={idx}
                                className="hero__stat"
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.5 + (idx * 0.1) }}
                            >
                                <div className="hero__stat-icon">
                                    <div className="hero__stat-icon-inner">{s.icon}</div>
                                </div>
                                <div className="hero__stat-content">
                                    <span className="hero__stat-num">{s.n}</span>
                                    <span className="hero__stat-label">{s.l}</span>
                                </div>
                            </motion.div>
                        ))}
                    </motion.div>
                </div>

                {/* Background: gradient + decorative orbs + glow + dot grid */}
                <div className="hero__bg" aria-hidden="true">
                    <div className="hero__glow" />
                    <div className="hero__dots" />
                    <div className="hero__orb hero__orb--1" />
                    <div className="hero__orb hero__orb--2" />
                    <div className="hero__orb hero__orb--3" />
                </div>
            </section>

            {/* ── ADVERTISEMENT SLOT ── */}
            <div className="container" style={{ margin: '2rem auto' }}>
                <AdPlaceholder format="horizontal" />
            </div>

            {/* ── TOOL GRID ── */}
            <section className="section tools-section" id="tools">
                <div className="container">
                    <SectionTitle
                        badge="📋 All Tools"
                        title="Everything you need for PDF"
                        subtitle="Pick a tool and get started in seconds. All processing happens securely on our servers."
                    />

                    {/* Category tabs */}
                    <div className="tools-section__tabs" role="tablist">
                        {CATEGORIES.map((cat) => (
                            <motion.button
                                key={cat}
                                role="tab"
                                aria-selected={activeCategory === cat}
                                className={`tools-section__tab ${activeCategory === cat ? 'active' : ''}`}
                                onClick={() => setActiveCategory(cat)}
                                whileHover={{ scale: 1.04 }}
                                whileTap={{ scale: 0.97 }}
                                transition={{ type: 'spring', stiffness: 380, damping: 22 }}
                            >
                                {cat}
                            </motion.button>
                        ))}
                    </div>

                    {/* Grid */}
                    <motion.div
                        className="tools-grid"
                        layout
                        transition={{ duration: 0.25 }}
                    >
                        {filtered.map((tool, i) => (
                            <ToolCard
                                key={tool.id}
                                icon={tool.icon}
                                title={tool.title}
                                description={tool.desc}
                                color={tool.color}
                                to={`/tool/${tool.id}`}
                                index={i}
                            />
                        ))}
                    </motion.div>
                </div>
            </section>

            {/* ── AD BANNER 1 — below tools grid ── */}
            <div className="container">
                <div className="ad-banner" aria-label="Advertisement">
                    <span className="ad-banner__label">Advertisement</span>
                    <p className="ad-banner__placeholder">Google AdSense — 728×90 Leaderboard</p>
                </div>
            </div>

            {/* ── FEATURES ── */}
            <section className="section features-section">
                <div className="container">
                    <SectionTitle
                        badge="✅ Why PDFsIn5"
                        title="Built for speed and privacy"
                        subtitle="We handle your files securely and delete them automatically — no data is ever stored."
                    />

                    <div className="features-grid">
                        {FEATURES.map((f, i) => (
                            <motion.div
                                key={f.title}
                                className="feature-card card"
                                initial={{ opacity: 0, y: 28 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true, margin: '-40px' }}
                                transition={{ duration: 0.4, delay: i * 0.1 }}
                                whileHover={{ y: -4, transition: { type: 'spring', stiffness: 300, damping: 20 } }}
                            >
                                <span className="feature-card__icon">{f.icon}</span>
                                <h3 className="feature-card__title">{f.title}</h3>
                                <p className="feature-card__desc">{f.desc}</p>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            {/* ── AD BANNER 2 — before SEO article ── */}
            <div className="container">
                <div className="ad-banner" aria-label="Advertisement">
                    <span className="ad-banner__label">Advertisement</span>
                    <p className="ad-banner__placeholder">Google AdSense — 728×90 Leaderboard</p>
                </div>
            </div>

            {/* ── SEO ARTICLE PREVIEW ── */}
            <section className="section seo-section">
                <div className="container">
                    <SectionTitle
                        badge="📖 PDF Guides"
                        title="Free Online PDF Tools for Every Document Task"
                        subtitle="Learn how to merge, compress, convert, and secure your PDFs — right in the browser, for free."
                        align="left"
                    />

                    <div className="seo-grid">

                        {/* Article 1 */}
                        <motion.article
                            className="seo-card"
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true, margin: '-30px' }}
                            transition={{ duration: 0.4 }}
                            whileHover={{ y: -3, transition: { type: 'spring', stiffness: 300, damping: 22 } }}
                        >
                            <div className="seo-card__tag">Merge &amp; Organize</div>
                            <h3 className="seo-card__title">How to Merge Multiple PDFs Into One File</h3>
                            <p className="seo-card__body">
                                Combining PDFs manually is time-consuming. PDFsIn5 lets you drag and drop multiple files,
                                reorder pages, and download a single merged document in seconds — completely free,
                                with no software to install.
                            </p>
                            <a href="/blog/merge-pdf-guide" className="seo-card__link">
                                Read more <FiArrowRight style={{ display: 'inline', verticalAlign: 'middle' }} />
                            </a>
                        </motion.article>

                        {/* Article 2 */}
                        <motion.article
                            className="seo-card"
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true, margin: '-30px' }}
                            transition={{ duration: 0.4, delay: 0.1 }}
                            whileHover={{ y: -3, transition: { type: 'spring', stiffness: 300, damping: 22 } }}
                        >
                            <div className="seo-card__tag">Compression</div>
                            <h3 className="seo-card__title">Reduce PDF File Size Without Losing Quality</h3>
                            <p className="seo-card__body">
                                Large PDFs slow down email attachments and uploads. Our smart compression engine
                                reduces file sizes by up to 80% while preserving readability — ideal for
                                students, professionals, and businesses.
                            </p>
                            <a href="/blog/compress-pdf-guide" className="seo-card__link">
                                Read more <FiArrowRight style={{ display: 'inline', verticalAlign: 'middle' }} />
                            </a>
                        </motion.article>

                        {/* Article 3 */}
                        <motion.article
                            className="seo-card"
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true, margin: '-30px' }}
                            transition={{ duration: 0.4, delay: 0.2 }}
                            whileHover={{ y: -3, transition: { type: 'spring', stiffness: 300, damping: 22 } }}
                        >
                            <div className="seo-card__tag">Convert</div>
                            <h3 className="seo-card__title">Convert PDF to Word, Excel, and Images Instantly</h3>
                            <p className="seo-card__body">
                                Need to edit a PDF in Microsoft Word or extract data into Excel? PDFsIn5 converts
                                your documents accurately and preserves formatting — no account required.
                                Simply upload and download in seconds.
                            </p>
                            <a href="/blog/convert-pdf-guide" className="seo-card__link">
                                Read more <FiArrowRight style={{ display: 'inline', verticalAlign: 'middle' }} />
                            </a>
                        </motion.article>

                    </div>

                    {/* Browse all articles */}
                    <div className="seo-section__cta">
                        <a href="/blog" className="seo-section__browse">
                            Browse all PDF guides <FiArrowRight style={{ display: 'inline', verticalAlign: 'middle' }} />
                        </a>
                    </div>
                </div>
            </section>

            {/* ── CTA BANNER ── */}
            <section className="cta-banner">
                <div className="container cta-banner__inner">
                    <div>
                        <h2 className="cta-banner__title">Ready to get started?</h2>
                        <p className="cta-banner__sub">Choose any tool and process your first file in under 30 seconds.</p>
                    </div>
                    <Button
                        size="lg"
                        iconEnd={<FiArrowRight />}
                        onClick={() => document.getElementById('tools')?.scrollIntoView({ behavior: 'smooth' })}
                    >
                        Get started — it&apos;s free
                    </Button>
                </div>
            </section>

        </motion.div>
    );
}
