import { Link } from 'react-router-dom';
import { FiGithub, FiTwitter, FiLinkedin, FiYoutube, FiInstagram } from 'react-icons/fi';
import './Footer.css';

const TOOLS = [
    { label: 'Merge PDF', to: '/tool/merge-pdf' },
    { label: 'Split PDF', to: '/tool/split-pdf' },
    { label: 'Compress PDF', to: '/tool/compress-pdf' },
    { label: 'PDF to Word', to: '/tool/pdf-to-word' },
    { label: 'Images to PDF', to: '/tool/images-to-pdf' },
    { label: 'Protect PDF', to: '/tool/protect-pdf' },
];

export default function Footer() {
    return (
        <footer className="footer">
            <div className="container footer__inner">
                {/* Brand */}
                <div className="footer__brand">
                    <span className="footer__logo">⚡ PDFsIn<span>5</span></span>
                    <p className="footer__tagline">Complete PDF toolkit — free, fast, and private.</p>
                    <div className="footer__socials">
                        <a href="https://github.com/Om-Rajpure" target="_blank" rel="noopener noreferrer" aria-label="GitHub"><FiGithub /></a>
                        <a href="https://www.linkedin.com/in/om-rajpure/" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn"><FiLinkedin /></a>
                        <a href="https://www.youtube.com/@conceptsin5" target="_blank" rel="noopener noreferrer" aria-label="YouTube"><FiYoutube /></a>
                        <a href="https://www.instagram.com/conceptsin5" target="_blank" rel="noopener noreferrer" aria-label="Instagram"><FiInstagram /></a>
                    </div>
                </div>

                {/* Quick Links */}
                <div className="footer__links">
                    <p className="footer__links-heading">Popular Tools</p>
                    {TOOLS.map((t) => (
                        <Link key={t.to} to={t.to} className="footer__link">{t.label}</Link>
                    ))}
                </div>

                {/* Company */}
                <div className="footer__links">
                    <p className="footer__links-heading">Company</p>
                    <Link to="/about" className="footer__link">About</Link>
                    <Link to="/blog" className="footer__link">Blog</Link>
                    <Link to="/privacy-policy" className="footer__link">Privacy Policy</Link>
                    <Link to="/terms" className="footer__link">Terms of Service</Link>
                </div>
            </div>

            <div className="footer__bottom">
                <p>&copy; {new Date().getFullYear()} PDFsIn5. All rights reserved.</p>
            </div>
        </footer>
    );
}
