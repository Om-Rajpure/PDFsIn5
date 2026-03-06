import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import SEO from '../components/SEO';
import BlogCard from '../components/BlogCard';
import AdPlaceholder from '../components/AdPlaceholder';
import { BLOG_POSTS } from '../data/blog';
import '../styles/blog.css';

export default function Blog() {
    return (
        <motion.div
            className="blog-index"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
        >
            <SEO
                title="Blog & PDF Guides"
                description="Read helpful guides, tips, and tutorials on how to manage, merge, and optimize your PDF documents efficiently."
                url="/blog"
            />

            <section className="blog-hero">
                <div className="container">
                    <h1>PDFsIn5 Blog</h1>
                    <p>Helpful guides, tips, and tutorials to master your document workflow.</p>
                </div>
            </section>

            <div className="container" style={{ margin: '2rem auto' }}>
                <AdPlaceholder format="horizontal" />
            </div>

            <section className="blog-list container">
                <div className="blog-grid">
                    {BLOG_POSTS.map((post, i) => (
                        <BlogCard key={post.id} post={post} delay={i * 0.1} />
                    ))}
                </div>
            </section>

            <div className="container" style={{ margin: '4rem auto' }}>
                <AdPlaceholder format="horizontal" />
            </div>
        </motion.div>
    );
}
