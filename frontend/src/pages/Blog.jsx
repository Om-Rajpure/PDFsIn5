import { Link } from 'react-router-dom';
import '../styles/global.css';

export const BLOG_POSTS = [
    {
        slug: 'merge-pdf-guide',
        title: 'How to Merge PDF Files Online',
        desc: 'Combine multiple PDFs into a single document without complex software.',
        content: `PDF files are commonly used for sharing documents because they maintain formatting across different devices. However, users often end up with multiple PDF files that need to be combined into a single document.\n\nMerging PDF files allows you to organize documents, create reports, and combine multiple files into one structured file.\n\nSteps to merge PDF files online:\n\n1. Upload the PDF files you want to combine\n2. Arrange the files in the desired order\n3. Start the merging process\n4. Wait a few seconds while the files are combined\n5. Download the final merged document\n\nUsing an online tool removes the need to install heavy PDF software and allows the process to be completed quickly from any device.`
    },
    {
        slug: 'compress-pdf-guide',
        title: 'How to Compress PDF Files Without Losing Quality',
        desc: 'Reduce file sizes effectively to make sharing and emailing easier.',
        content: `Large PDF files can be difficult to share through email or upload to websites. Compressing a PDF helps reduce its file size while maintaining readable document quality.\n\nPDF compression works by optimizing images, removing unnecessary data, and reducing file complexity.\n\nSteps to compress a PDF:\n\n1. Upload the PDF file\n2. Start the compression process\n3. Wait while the system reduces the file size\n4. Download the smaller PDF\n\nCompression is especially useful when sharing documents online or submitting files with size limits.`
    },
    {
        slug: 'images-to-pdf-guide',
        title: 'How to Convert Images to PDF',
        desc: 'Bundle your images, scans, and photos into a structured PDF binder.',
        content: `Many users store documents as images such as JPG or PNG files. Converting these images into a PDF file makes them easier to organize and share.\n\nA PDF document can contain multiple images arranged in a structured format.\n\nSteps to convert images to PDF:\n\n1. Upload your image files\n2. Arrange the images in the correct order\n3. Start the conversion process\n4. Download the generated PDF document\n\nThis is useful for creating reports, scanned documents, and digital records.`
    },
    {
        slug: 'pdf-to-word-guide',
        title: 'How to Convert PDF to Word',
        desc: 'Turn uneditable PDFs back into editable DOCX format.',
        content: `PDF files are excellent for sharing documents but are difficult to edit. Converting a PDF into a Word document allows users to modify text, update information, and reuse content.\n\nSteps to convert PDF to Word:\n\n1. Upload the PDF file\n2. Start the conversion process\n3. Wait while the system extracts the text and layout\n4. Download the editable Word document\n\nThis method saves time compared to manually retyping document content.`
    }
];

export default function Blog() {
    return (
        <div className="container" style={{ maxWidth: '800px', margin: '0 auto', padding: 'var(--section-py) 24px' }}>
            <h1 style={{ fontSize: 'var(--text-3xl)', fontWeight: '800', marginBottom: '8px', color: 'var(--clr-text)', textAlign: 'center' }}>Blog</h1>
            <p style={{ fontSize: 'var(--text-base)', lineHeight: '1.6', color: 'var(--clr-text-muted)', marginBottom: '32px', textAlign: 'center' }}>
                Helpful guides and tutorials for working with PDF files.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                {BLOG_POSTS.map((post) => (
                    <div key={post.slug} className="card" style={{ padding: '24px' }}>
                        <h2 style={{ fontSize: 'var(--text-xl)', fontWeight: '700', marginBottom: '8px', color: 'var(--clr-text)' }}>{post.title}</h2>
                        <p style={{ fontSize: 'var(--text-base)', lineHeight: '1.6', color: 'var(--clr-text-muted)', marginBottom: '16px' }}>{post.desc}</p>

                        <Link to={`/blog/${post.slug}`} className="btn btn--primary" style={{ display: 'inline-flex', padding: '10px 20px', fontSize: 'var(--text-sm)', fontWeight: '600', textDecoration: 'none', borderRadius: 'var(--radius-md)' }}>
                            Read More →
                        </Link>
                    </div>
                ))}
            </div>
        </div>
    );
}
