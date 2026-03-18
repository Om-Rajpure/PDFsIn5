import React from 'react';
import { Link } from 'react-router-dom';
import './BlogHighlightStrip.css';

const BLOG_HIGHLIGHTS = [
    { title: "How to summarize long PDFs with AI", link: "/blog/ai-pdf-summary" },
    { title: "Convert JPG to PDF in 5 seconds", link: "/blog/jpg-to-pdf-guide" },
    { title: "Improving productivity with AI document tools", link: "/blog/productivity-ai" },
    { title: "Merge 50+ PDFs instantly without loss", link: "/blog/merge-pdf-tips" },
    { title: "Secure your documents with zero-trust encryption", link: "/blog/secure-pdfs" },
];

export default function BlogHighlightStrip() {
    return (
        <div className="blog-strip">
            <div className="blog-strip__content">
                {/* Double the list for seamless looping */}
                {[...BLOG_HIGHLIGHTS, ...BLOG_HIGHLIGHTS].map((item, idx) => (
                    <Link key={idx} to={item.link} className="blog-strip__item">
                        <span className="blog-strip__dot"></span>
                        {item.title}
                    </Link>
                ))}
            </div>
        </div>
    );
}
