import '../styles/global.css';

export default function Terms() {
    return (
        <div className="container" style={{ maxWidth: '800px', margin: '0 auto', padding: 'var(--section-py) 24px' }}>
            <div className="card" style={{ padding: '40px', display: 'flex', flexDirection: 'column', gap: '32px' }}>

                <section>
                    <h1 style={{ fontSize: 'var(--text-3xl)', fontWeight: '800', marginBottom: '24px', color: 'var(--clr-text)', textAlign: 'center' }}>Terms of Service</h1>

                    <h2 style={{ fontSize: 'var(--text-xl)', fontWeight: '700', marginBottom: '12px', color: 'var(--clr-text)', marginTop: '24px' }}>Introduction</h2>
                    <p style={{ fontSize: 'var(--text-base)', lineHeight: '1.6', color: 'var(--clr-text-muted)' }}>
                        By accessing or using PDFsIn5, you agree to the following terms and conditions.
                    </p>

                    <h2 style={{ fontSize: 'var(--text-xl)', fontWeight: '700', marginBottom: '12px', color: 'var(--clr-text)', marginTop: '24px' }}>Usage</h2>
                    <p style={{ fontSize: 'var(--text-base)', lineHeight: '1.6', color: 'var(--clr-text-muted)' }}>
                        The platform provides online utility tools for processing, formatting, compiling, and securing document files without downloading native software.
                    </p>

                    <h2 style={{ fontSize: 'var(--text-xl)', fontWeight: '700', marginBottom: '12px', color: 'var(--clr-text)', marginTop: '24px' }}>User Responsibility</h2>
                    <p style={{ fontSize: 'var(--text-base)', lineHeight: '1.6', color: 'var(--clr-text-muted)' }}>
                        Users must ensure that the files uploaded to this platform do not violate local or international laws, breach intellectual property protections, or contain malicious software architectures. We hold no responsibility for the contents passed through this processor.
                    </p>

                    <h2 style={{ fontSize: 'var(--text-xl)', fontWeight: '700', marginBottom: '12px', color: 'var(--clr-text)', marginTop: '24px' }}>Service Availability</h2>
                    <p style={{ fontSize: 'var(--text-base)', lineHeight: '1.6', color: 'var(--clr-text-muted)' }}>
                        The service is provided entirely free for general use but may be updated, rate-limited, modified, or become temporarily unavailable at any time due to necessary maintenance or infrastructural adjustments.
                    </p>

                    <h2 style={{ fontSize: 'var(--text-xl)', fontWeight: '700', marginBottom: '12px', color: 'var(--clr-text)', marginTop: '24px' }}>Limitation of Liability</h2>
                    <p style={{ fontSize: 'var(--text-base)', lineHeight: '1.6', color: 'var(--clr-text-muted)' }}>
                        PDFsIn5 is provided "as-is". We cannot fully guarantee uninterrupted service, completely bug-free implementations, or 100% data fidelity on heavily corrupted original files. You use the service parameters entirely at your own discretion and risk.
                    </p>
                </section>
            </div>
        </div>
    );
}
