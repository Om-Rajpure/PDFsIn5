import '../styles/global.css';

export default function Privacy() {
    return (
        <div className="container" style={{ maxWidth: '800px', margin: '0 auto', padding: 'var(--section-py) 24px' }}>
            <div className="card" style={{ padding: '40px', display: 'flex', flexDirection: 'column', gap: '32px' }}>

                <section>
                    <h1 style={{ fontSize: 'var(--text-3xl)', fontWeight: '800', marginBottom: '24px', color: 'var(--clr-text)', textAlign: 'center' }}>Privacy Policy</h1>

                    <h2 style={{ fontSize: 'var(--text-xl)', fontWeight: '700', marginBottom: '12px', color: 'var(--clr-text)', marginTop: '24px' }}>Introduction</h2>
                    <p style={{ fontSize: 'var(--text-base)', lineHeight: '1.6', color: 'var(--clr-text-muted)' }}>
                        PDFsIn5 respects user privacy and is designed from the ground up to process your files securely.
                    </p>

                    <h2 style={{ fontSize: 'var(--text-xl)', fontWeight: '700', marginBottom: '12px', color: 'var(--clr-text)', marginTop: '24px' }}>File Handling</h2>
                    <p style={{ fontSize: 'var(--text-base)', lineHeight: '1.6', color: 'var(--clr-text-muted)' }}>
                        Uploaded files are used only for processing the requested task. We do not index, search, or retain ownership curves over your documents.
                    </p>

                    <h2 style={{ fontSize: 'var(--text-xl)', fontWeight: '700', marginBottom: '12px', color: 'var(--clr-text)', marginTop: '24px' }}>Temporary Storage</h2>
                    <p style={{ fontSize: 'var(--text-base)', lineHeight: '1.6', color: 'var(--clr-text-muted)' }}>
                        Files may be stored temporarily on our processing servers during the operation. They are <strong>automatically deleted</strong> immediately after the operation is completed and your download is served.
                    </p>

                    <h2 style={{ fontSize: 'var(--text-xl)', fontWeight: '700', marginBottom: '12px', color: 'var(--clr-text)', marginTop: '24px' }}>No Personal Data Collection</h2>
                    <p style={{ fontSize: 'var(--text-base)', lineHeight: '1.6', color: 'var(--clr-text-muted)' }}>
                        PDFsIn5 does not require users to create accounts, provide emails, or submit personal information to use the primary tools.
                    </p>

                    <h2 style={{ fontSize: 'var(--text-xl)', fontWeight: '700', marginBottom: '12px', color: 'var(--clr-text)', marginTop: '24px' }}>Security</h2>
                    <p style={{ fontSize: 'var(--text-base)', lineHeight: '1.6', color: 'var(--clr-text-muted)' }}>
                        Reasonable industry-standard security practices, including TLS/SSL encryption in transit, are implemented to protect your uploaded files while they travel to and from our service.
                    </p>
                </section>
            </div>
        </div>
    );
}
