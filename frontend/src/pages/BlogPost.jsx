import { useParams, Link, Navigate } from 'react-router-dom';
import { BLOG_POSTS } from './Blog';
import '../styles/global.css';

export default function BlogPost() {
    const { slug } = useParams();
    const post = BLOG_POSTS.find((p) => p.slug === slug);

    if (!post) {
        return <Navigate to="/blog" replace />;
    }

    // Split content by double newlines into paragraphs
    const paragraphs = post.content.split('\n\n');

    return (
        <div className="container" style={{ maxWidth: '800px', margin: '0 auto', padding: 'var(--section-py) 24px' }}>

            <div style={{ marginBottom: '24px' }}>
                <Link to="/blog" style={{ color: 'var(--clr-primary)', textDecoration: 'none', fontWeight: '600', fontSize: 'var(--text-sm)' }}>
                    ← Back to Blog
                </Link>
            </div>

            <article className="card" style={{ padding: '40px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
                <header style={{ marginBottom: '16px', borderBottom: '1px solid var(--clr-border)', paddingBottom: '24px' }}>
                    <h1 style={{ fontSize: 'var(--text-3xl)', fontWeight: '800', color: 'var(--clr-text)', lineHeight: '1.2', textAlign: 'center' }}>
                        {post.title}
                    </h1>
                </header>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', fontSize: 'var(--text-base)', lineHeight: '1.8', color: 'var(--clr-text-muted)' }}>
                    {paragraphs.map((p, index) => {
                        // Check if paragraph looks like a numbered list
                        if (p.startsWith('1.') || p.startsWith('1 ')) {
                            const steps = p.split('\n');
                            return (
                                <ol key={index} style={{ listStylePosition: 'inside', display: 'flex', flexDirection: 'column', gap: '8px', marginLeft: '16px', color: 'var(--clr-text)' }}>
                                    {steps.map((step, sIdx) => {
                                        // Remove the leading number and dot/space for visual cleanliness if rendering an actual <ol>
                                        const cleanText = step.replace(/^\d+[\.\s]+/, '');
                                        return <li key={sIdx}>{cleanText}</li>;
                                    })}
                                </ol>
                            );
                        }
                        return <p key={index}>{p}</p>;
                    })}
                </div>
            </article>

        </div>
    );
}
