import { useParams, Navigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import { FiCalendar, FiClock, FiUser, FiArrowLeft, FiTag } from 'react-icons/fi';
import SEO from '../components/SEO';
import AdPlaceholder from '../components/AdPlaceholder';
import { BLOG_POSTS } from '../data/blog';
import '../styles/blog.css';

export default function BlogPost() {
    const { slug } = useParams();
    const post = BLOG_POSTS.find(p => p.slug === slug);

    if (!post) {
        return <Navigate to="/blog" replace />;
    }

    /* SEO Structured Data */
    const articleSchema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": post.title,
        "description": post.excerpt,
        "author": {
            "@type": "Person",
            "name": post.author
        },
        "datePublished": post.date,
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": `https://pdfsin5.com/blog/${post.slug}`
        }
    };

    return (
        <motion.article
            className="blog-post"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
        >
            <SEO
                title={post.title}
                description={post.excerpt}
                url={`/blog/${post.slug}`}
                type="article"
                schema={[articleSchema]}
            />

            <div className="container">
                <div className="blog-post__header">
                    <Link to="/blog" className="blog-post__back">
                        <FiArrowLeft /> Back to Blog
                    </Link>

                    <div className="blog-post__tags">
                        {post.tags?.map(t => (
                            <span key={t} className="blog-tag"><FiTag /> {t}</span>
                        ))}
                    </div>

                    <h1 className="blog-post__title">{post.title}</h1>

                    <div className="blog-post__meta">
                        <span><FiUser /> {post.author}</span>
                        <span><FiCalendar /> {post.date}</span>
                        <span><FiClock /> {post.readTime}</span>
                    </div>
                </div>

                <div className="blog-post__layout">
                    {/* Main Content */}
                    <div className="blog-post__content-wrapper">
                        {/* Top inline ad */}
                        <AdPlaceholder format="fluid" className="blog-post__ad-top" />

                        <div className="blog-post__markdown">
                            <ReactMarkdown>{post.content}</ReactMarkdown>
                        </div>

                        {/* Bottom inline ad */}
                        <AdPlaceholder format="fluid" className="blog-post__ad-bottom" />

                        {/* Author/Share block could go here */}
                    </div>

                    {/* Sidebar */}
                    <aside className="blog-post__sidebar">
                        <div className="blog-post__sidebar-stick">
                            <AdPlaceholder format="rectangle" />

                            {post.relatedTools?.length > 0 && (
                                <div className="blog-sidebar-tools">
                                    <h3>Related Tools</h3>
                                    <ul>
                                        {post.relatedTools.map(slug => (
                                            <li key={slug}>
                                                <Link to={`/tool/${slug}`}>
                                                    Try {slug.split('-').join(' ')}
                                                </Link>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            <AdPlaceholder format="rectangle" />
                        </div>
                    </aside>
                </div>
            </div>
        </motion.article>
    );
}
