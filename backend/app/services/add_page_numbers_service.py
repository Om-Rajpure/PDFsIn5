import io
import logging
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

logger = logging.getLogger(__name__)

def add_page_numbers_in_memory(
    pdf_bytes: bytes,
    position: str = "Bottom Center",
    format_str: str = "{n}",
    start_num: int = 1,
    margin: str = "Medium",
    font_size: str = "Medium"
) -> io.BytesIO:
    """
    Overlays page numbers onto a PDF in-memory.

    Args:
        pdf_bytes: Raw bytes of the original PDF.
        position: Where to place the number ("Top Left", "Top Center", "Top Right",
                  "Bottom Left", "Bottom Center", "Bottom Right").
        format_str: Format template string (e.g., "{n}", "Page {n}", "Page {n} of {total}").
        start_num: The starting number for the first page.
        margin: "Small", "Medium", or "Large". Sets the distance from the edge.
        font_size: "Small" (9), "Medium" (12), or "Large" (16).

    Returns:
        io.BytesIO containing the numbered PDF.
    """
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        writer = PdfWriter()
        total_pages = len(reader.pages)

        # Map string inputs to numerical values
        margin_map = {"Small": 20, "Medium": 40, "Large": 70}
        font_map = {"Small": 9, "Medium": 12, "Large": 16}
        
        m_val = margin_map.get(margin, 40)
        f_size = font_map.get(font_size, 12)

        for i, page in enumerate(reader.pages):
            current_num = start_num + i

            # Create a string using the selected format
            text = format_str.replace("{n}", str(current_num)).replace("{total}", str(total_pages))

            # Determine page dimensions
            # Some PDFs have origin not at 0,0 - getting upperRight and lowerLeft handles this
            ll_x = float(page.mediabox.lower_left[0])
            ll_y = float(page.mediabox.lower_left[1])
            ur_x = float(page.mediabox.upper_right[0])
            ur_y = float(page.mediabox.upper_right[1])
            
            width = ur_x - ll_x
            height = ur_y - ll_y

            # Determine coordinates based on position
            x, y = 0, 0
            if "Top" in position:
                y = height - m_val
            else:  # Bottom
                y = m_val

            if "Left" in position:
                x = m_val
            elif "Right" in position:
                x = width - m_val
            else:  # Center
                x = width / 2

            # Generate overlay PDF with just the page number using reportlab
            packet = io.BytesIO()
            # We must set pagesize carefully to match the original doc
            c = canvas.Canvas(packet, pagesize=(width, height))
            c.setFont("Helvetica", f_size)
            
            # Adjust alignment based on position
            if "Right" in position:
                c.drawRightString(x, y, text)
            elif "Center" in position:
                c.drawCentredString(x, y, text)
            else:
                c.drawString(x, y, text)
                
            c.save()
            packet.seek(0)

            # Read the overlay packet as a PDF
            overlay_pdf = PdfReader(packet)
            overlay_page = overlay_pdf.pages[0]

            # Merge the overlay onto the original page
            page.merge_page(overlay_page)
            writer.add_page(page)

        out_io = io.BytesIO()
        writer.write(out_io)
        out_io.seek(0)
        return out_io

    except Exception as exc:
        raise RuntimeError(f"Failed to add page numbers: {exc}") from exc
