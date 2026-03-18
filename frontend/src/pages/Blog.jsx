import { Link } from 'react-router-dom';
import '../styles/content-pages.css';

export const BLOG_POSTS = [
    {
        slug: 'merge-pdf-guide',
        title: 'How to Merge PDF Files Online',
        desc: 'Combine multiple PDFs into a single document without complex software.',
        content: `PDF files are commonly used for sharing documents because they maintain formatting across different devices. However, users often end up with multiple PDF files that need to be combined into a single document.\n\nMerging PDF files allows you to organize documents, create reports, and combine multiple files into one structured file.\n\nSteps to merge PDF files online:\n\n1. Upload the PDF files you want to combine\n2. Arrange the files in the desired order\n3. Start the merging process\n4. Wait a few seconds while the files are combined\n5. Download the final merged document\n\nUsing an online tool removes the need to install heavy PDF software and allows the process to be completed quickly from any device.`
    },
    {
        slug: 'compress-pdf-guide',
        title: 'How to Compress PDF Files Without Quality Loss',
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
        <main className="content-page">
            <div className="container">
                <header className="content-header">
                    <h1 className="content-header__title">Blog & Guides</h1>
                    <p className="content-header__subtitle">
                        Master your documents with our expert tutorials and PDF productivity tips.
                    </p>
                </header>

                <div className="blog-grid">
                    {BLOG_POSTS.map((post) => (
                        <article key={post.slug} className="blog-card glass-card card">
                            <h2 className="blog-card__title">{post.title}</h2>
                            <p className="blog-card__desc">{post.desc}</p>
                            <Link to={`/blog/${post.slug}`} className="btn btn--primary">
                                Read Guide →
                            </Link>
                        </article>
                    ))}
                </div>
            </div>
        </main>
    );
}

