import { Helmet } from 'react-helmet-async';

/**
 * SEO Component
 * Manages document head (title, meta description, standard OG tags).
 * 
 * Props:
 *   title (string)       - Page title (e.g. "Merge PDF Online Free")
 *   description (string) - Meta description
 *   url (string)         - Canonical URL path (e.g. "/tool/merge-pdf")
 *   type (string)        - OG type, default 'website', can be 'article' for blogs
 *   schema (array)       - Array of JSON-LD objects for structured data
 */
export default function SEO({ title, description, url = '', type = 'website', schema = [] }) {
    const siteName = 'PDFsIn5';
    const fullTitle = `${title} | ${siteName}`;
    const fullUrl = `https://pdfsin5.com${url}`;

    return (
        <Helmet>
            <title>{fullTitle}</title>
            <meta name="description" content={description} />

            {/* Open Graph / Facebook */}
            <meta property="og:type" content={type} />
            <meta property="og:url" content={fullUrl} />
            <meta property="og:title" content={fullTitle} />
            <meta property="og:description" content={description} />
            <meta property="og:site_name" content={siteName} />

            {/* Twitter */}
            <meta name="twitter:card" content="summary_large_image" />
            <meta name="twitter:url" content={fullUrl} />
            <meta name="twitter:title" content={fullTitle} />
            <meta name="twitter:description" content={description} />

            {/* Canonical link */}
            <link rel="canonical" href={fullUrl} />

            {/* Google Structured Data (JSON-LD) */}
            {schema.map((schemaObj, index) => (
                <script type="application/ld+json" key={index}>
                    {JSON.stringify(schemaObj)}
                </script>
            ))}
        </Helmet>
    );
}
