import { FiGithub, FiTwitter, FiLinkedin, FiYoutube, FiInstagram } from 'react-icons/fi';
import '../styles/global.css';

export default function About() {
    return (
        <div className="container" style={{ maxWidth: '800px', margin: '0 auto', padding: 'var(--section-py) 24px' }}>
            <div className="card" style={{ padding: '40px', display: 'flex', flexDirection: 'column', gap: '32px' }}>

                <section>
                    <h1 style={{ fontSize: 'var(--text-3xl)', fontWeight: '800', marginBottom: '16px', color: 'var(--clr-text)', textAlign: 'center' }}>About PDFsIn5</h1>
                    <p style={{ fontSize: 'var(--text-base)', lineHeight: '1.6', color: 'var(--clr-text-muted)', marginBottom: '16px' }}>
                        PDFsIn5 is an online platform designed to make working with PDF documents fast, simple, and accessible for everyone. Many people need to merge, compress, convert, or organize PDF files but often have to install large software programs or sign up for complicated services.
                    </p>
                    <p style={{ fontSize: 'var(--text-base)', lineHeight: '1.6', color: 'var(--clr-text-muted)', marginBottom: '16px' }}>
                        PDFsIn5 removes that friction by providing essential document tools that work directly in the browser. Users can upload their files, process them in seconds, and download the result without installing anything or creating an account.
                    </p>
                    <p style={{ fontSize: 'var(--text-base)', lineHeight: '1.6', color: 'var(--clr-text-muted)' }}>
                        The goal of the platform is to ensure that most document tasks can be completed in just a few simple steps.
                    </p>
                </section>

                <section>
                    <h2 style={{ fontSize: 'var(--text-xl)', fontWeight: '700', marginBottom: '16px', color: 'var(--clr-text)' }}>Our Mission</h2>
                    <p style={{ fontSize: 'var(--text-base)', lineHeight: '1.6', color: 'var(--clr-text-muted)', marginBottom: '16px' }}>
                        Our mission is to simplify everyday document tasks by building tools that are:
                    </p>
                    <ul style={{ listStylePosition: 'inside', fontSize: 'var(--text-base)', lineHeight: '1.6', color: 'var(--clr-text-muted)', display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '16px', marginLeft: '16px' }}>
                        <li>Fast</li>
                        <li>Simple to use</li>
                        <li>Secure</li>
                        <li>Accessible from any device</li>
                    </ul>
                    <p style={{ fontSize: 'var(--text-base)', lineHeight: '1.6', color: 'var(--clr-text-muted)' }}>
                        We believe that productivity tools should be available to everyone without unnecessary complexity. PDFsIn5 focuses on creating a clean interface and efficient tools so users can complete tasks quickly and move on with their work.
                    </p>
                </section>

                <section>
                    <h2 style={{ fontSize: 'var(--text-xl)', fontWeight: '700', marginBottom: '16px', color: 'var(--clr-text)' }}>What You Can Do With PDFsIn5</h2>
                    <p style={{ fontSize: 'var(--text-base)', lineHeight: '1.6', color: 'var(--clr-text-muted)', marginBottom: '16px' }}>
                        The platform includes several tools that help users manage and convert PDF documents. Examples include:
                    </p>
                    <ul style={{ listStylePosition: 'inside', fontSize: 'var(--text-base)', lineHeight: '1.6', color: 'var(--clr-text-muted)', display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '16px', marginLeft: '16px' }}>
                        <li>Merge multiple PDF files into one document</li>
                        <li>Compress large PDF files to reduce file size</li>
                        <li>Convert images such as JPG or PNG into PDF documents</li>
                        <li>Convert PDF files into editable Word documents</li>
                        <li>Split PDFs into smaller files</li>
                        <li>Rotate and organize PDF pages</li>
                    </ul>
                    <p style={{ fontSize: 'var(--text-base)', lineHeight: '1.6', color: 'var(--clr-text-muted)' }}>
                        New tools will continue to be added as the platform grows.
                    </p>
                </section>

                <section>
                    <h2 style={{ fontSize: 'var(--text-xl)', fontWeight: '700', marginBottom: '16px', color: 'var(--clr-text)' }}>Privacy and Security</h2>
                    <p style={{ fontSize: 'var(--text-base)', lineHeight: '1.6', color: 'var(--clr-text-muted)', marginBottom: '16px' }}>
                        User privacy is an important priority for PDFsIn5.
                    </p>
                    <p style={{ fontSize: 'var(--text-base)', lineHeight: '1.6', color: 'var(--clr-text-muted)', marginBottom: '16px' }}>
                        Uploaded files are processed only for the requested operation. Files are stored temporarily during processing and automatically removed after the task is completed.
                    </p>
                    <p style={{ fontSize: 'var(--text-base)', lineHeight: '1.6', color: 'var(--clr-text-muted)' }}>
                        The platform does not require account creation or personal data to use the tools.
                    </p>
                </section>

                <section style={{ paddingTop: '16px', borderTop: '1px solid var(--clr-border)' }}>
                    <h2 style={{ fontSize: 'var(--text-xl)', fontWeight: '700', marginBottom: '16px', color: 'var(--clr-text)' }}>Connect With Us</h2>
                    <p style={{ fontSize: 'var(--text-base)', lineHeight: '1.6', color: 'var(--clr-text-muted)', marginBottom: '16px' }}>
                        Users can connect with the creator and follow updates through the following platforms.
                    </p>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', fontSize: '1.25rem' }}>
                        <a href="https://github.com/Om-Rajpure" target="_blank" rel="noopener noreferrer" aria-label="GitHub" style={{ color: 'var(--clr-text-muted)', transition: 'color var(--transition-fast)' }} onMouseOver={(e) => e.target.style.color = 'var(--clr-primary)'} onMouseOut={(e) => e.target.style.color = 'var(--clr-text-muted)'}><FiGithub /></a>
                        <a href="https://www.linkedin.com/in/om-rajpure/" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn" style={{ color: 'var(--clr-text-muted)', transition: 'color var(--transition-fast)' }} onMouseOver={(e) => e.target.style.color = 'var(--clr-primary)'} onMouseOut={(e) => e.target.style.color = 'var(--clr-text-muted)'}><FiLinkedin /></a>
                        <a href="https://www.youtube.com/@conceptsin5" target="_blank" rel="noopener noreferrer" aria-label="YouTube" style={{ color: 'var(--clr-text-muted)', transition: 'color var(--transition-fast)' }} onMouseOver={(e) => e.target.style.color = 'var(--clr-primary)'} onMouseOut={(e) => e.target.style.color = 'var(--clr-text-muted)'}><FiYoutube /></a>
                        <a href="https://www.instagram.com/conceptsin5" target="_blank" rel="noopener noreferrer" aria-label="Instagram" style={{ color: 'var(--clr-text-muted)', transition: 'color var(--transition-fast)' }} onMouseOver={(e) => e.target.style.color = 'var(--clr-primary)'} onMouseOut={(e) => e.target.style.color = 'var(--clr-text-muted)'}><FiInstagram /></a>
                    </div>
                </section>
            </div>
        </div>
    );
}
