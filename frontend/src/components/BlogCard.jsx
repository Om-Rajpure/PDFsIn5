import { Link } from 'react-router-dom';
import { FiArrowRight, FiCalendar, FiClock } from 'react-icons/fi';
import { motion } from 'framer-motion';

/**
 * BlogCard Component
 * Displays a preview of a blog post in the list view.
 */
export default function BlogCard({ post, delay = 0 }) {
    return (
        <motion.article
            className="blog-card"
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay }}
        >
            <div className="blog-card__image" style={{ backgroundColor: `color-mix(in srgb, ${post.color || '#3b82f6'} 15%, transparent)` }}>
                {post.icon && <post.icon style={{ color: post.color || 'var(--color-primary)', fontSize: '3rem' }} />}
            </div>
            <div className="blog-card__content">
                <div className="blog-card__meta">
                    <span className="blog-card__tag">{post.tags?.[0] || 'Guides'}</span>
                    <span className="blog-card__date"><FiCalendar /> {post.date}</span>
                    <span className="blog-card__time"><FiClock /> {post.readTime}</span>
                </div>
                <h3 className="blog-card__title">
                    <Link to={`/blog/${post.slug}`}>{post.title}</Link>
                </h3>
                <p className="blog-card__excerpt">{post.excerpt}</p>
                <Link to={`/blog/${post.slug}`} className="blog-card__read-more">
                    Read Article <FiArrowRight />
                </Link>
            </div>
        </motion.article>
    );
}
