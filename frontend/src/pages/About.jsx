import { FiGithub, FiTwitter, FiLinkedin, FiYoutube, FiInstagram } from 'react-icons/fi';
import '../styles/content-pages.css';

export default function About() {
    return (
        <main className="content-page">
            <div className="container">
                <header className="content-header">
                    <h1 className="content-header__title">About PDFsIn5</h1>
                    <p className="content-header__subtitle">
                        Empowering users with fast, secure, and intuitive document tools since 2024.
                    </p>
                </header>

                <div className="about-card glass-card card">
                    <section className="about-section">
                        <h2 className="about-section__title">Our Story</h2>
                        <p className="about-section__text">
                            PDFsIn5 was born from a simple realization: document management shouldn't be a chore. 
                            Many people need to merge, compress, or convert PDF files but often have to install heavy software or navigate complex sign-ups.
                        </p>
                        <p className="about-section__text">
                            We removed that friction. By providing essential document tools that work directly in your browser, we ensure that your tasks are completed in seconds—private, secure, and hassle-free.
                        </p>
                    </section>

                    <section className="about-section">
                        <h2 className="about-section__title">Our Mission</h2>
                        <p className="about-section__text">
                            We believe productivity tools should be "Zero Thinking" experiences. Our mission is to build tools that are:
                        </p>
                        <ul className="about-list">
                            <li><strong>Blazing Fast:</strong> Results in under 5 seconds for most tasks.</li>
                            <li><strong>Privacy First:</strong> Files never leave your browser context for many operations.</li>
                            <li><strong>100% Free:</strong> No hidden costs or mandatory accounts.</li>
                            <li><strong>Universal:</strong> Works perfectly on any device, from anywhere.</li>
                        </ul>
                    </section>

                    <section className="about-section">
                        <h2 className="about-section__title">Privacy & Security</h2>
                        <p className="about-section__text">
                            Your security is non-negotiable. Unlike other platforms that store your files on cloud servers, PDFsIn5 prioritizes local-first processing.
                        </p>
                        <p className="about-section__text">
                            Uploaded files are processed only for the requested operation and are automatically purged. We don't track your content or sell your data—ever.
                        </p>
                    </section>

                    <section className="about-section" style={{ borderTop: '1px solid var(--glass-border)', paddingTop: '40px' }}>
                        <h2 className="about-section__title">Connect With Us</h2>
                        <p className="about-section__text">
                            Stay updated with new tool releases and PDF tips through our social channels.
                        </p>
                        <div className="social-links">
                            <a href="https://github.com/Om-Rajpure" target="_blank" rel="noopener noreferrer" className="social-link" aria-label="GitHub"><FiGithub /></a>
                            <a href="https://www.linkedin.com/in/om-rajpure/" target="_blank" rel="noopener noreferrer" className="social-link" aria-label="LinkedIn"><FiLinkedin /></a>
                            <a href="https://www.youtube.com/@conceptsin5" target="_blank" rel="noopener noreferrer" className="social-link" aria-label="YouTube"><FiYoutube /></a>
                            <a href="https://www.instagram.com/conceptsin5" target="_blank" rel="noopener noreferrer" className="social-link" aria-label="Instagram"><FiInstagram /></a>
                        </div>
                    </section>
                </div>
            </div>
        </main>
    );
}

