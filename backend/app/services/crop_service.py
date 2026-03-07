import io
import logging
from pypdf import PdfReader, PdfWriter

logger = logging.getLogger(__name__)

def parse_page_ranges(ranges_str: str, max_pages: int) -> set[int]:
    """
    Parses a string like "1-3, 5, 7-9" into a set of 0-based indices.
    """
    target_pages = set()
    if not ranges_str:
        return target_pages
        
    parts = [p.strip() for p in ranges_str.split(',')]
    for part in parts:
        if not part:
            continue
        if '-' in part:
            subparts = part.split('-')
            if len(subparts) == 2:
                try:
                    start = max(1, int(subparts[0].strip()))
                    end = min(max_pages, int(subparts[1].strip()))
                    if start <= end:
                        for p in range(start - 1, end):
                            target_pages.add(p)
                except ValueError:
                    pass
        else:
            try:
                page = int(part)
                if 1 <= page <= max_pages:
                    target_pages.add(page - 1)
            except ValueError:
                pass
                
    return target_pages


def crop_pdf_in_memory(
    pdf_bytes: bytes,
    top_margin: float = 0.0,
    bottom_margin: float = 0.0,
    left_margin: float = 0.0,
    right_margin: float = 0.0,
    unit: str = "Points",
    apply_to: str = "All pages",
    range_str: str = ""
) -> io.BytesIO:
    """
    Crops the PDF by adjusting the mediabox and cropbox of the pages.

    Args:
        pdf_bytes: Raw bytes of the original PDF.
        top_margin: Points to remove from the top.
        bottom_margin: Points to remove from the bottom.
        left_margin: Points to remove from the left.
        right_margin: Points to remove from the right.
        apply_to: "All pages" or "Specific page range".
        range_str: Comma-separated or dash-separated page ranges (1-indexed).

    Returns:
        io.BytesIO containing the cropped PDF.
    """
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        writer = PdfWriter()
        total_pages = len(reader.pages)

        # Determine which pages to crop (0-indexed)
        target_pages = set(range(total_pages))
        if apply_to == "Specific page range" and range_str:
            parsed = parse_page_ranges(range_str, total_pages)
            if parsed:
                target_pages = parsed

        for i, page in enumerate(reader.pages):
            if i in target_pages:
                # pypdf RectangleObjects are mutable but we need to update coordinates carefully.
                # Origin (lower_left) is usually (0, 0), but not always.
                # upper_right is usually (width, height)
                
                # Fetch current bounds
                ll_x = float(page.mediabox.lower_left[0])
                ll_y = float(page.mediabox.lower_left[1])
                ur_x = float(page.mediabox.upper_right[0])
                ur_y = float(page.mediabox.upper_right[1])
                
                width_pts = ur_x - ll_x
                height_pts = ur_y - ll_y

                t_pts = top_margin
                b_pts = bottom_margin
                l_pts = left_margin
                r_pts = right_margin

                if unit == "Millimeters":
                    mm_to_pts = 2.83465
                    t_pts *= mm_to_pts
                    b_pts *= mm_to_pts
                    l_pts *= mm_to_pts
                    r_pts *= mm_to_pts
                elif unit == "Percentage":
                    t_pts = height_pts * (top_margin / 100.0)
                    b_pts = height_pts * (bottom_margin / 100.0)
                    l_pts = width_pts * (left_margin / 100.0)
                    r_pts = width_pts * (right_margin / 100.0)

                new_ll_x = max(ll_x, ll_x + l_pts)
                new_ll_y = max(ll_y, ll_y + b_pts)
                new_ur_x = min(ur_x, ur_x - r_pts)
                new_ur_y = min(ur_y, ur_y - t_pts)

                # Ensure dimensions don't become negative or inverted
                if new_ll_x >= new_ur_x or new_ll_y >= new_ur_y:
                    logger.warning(f"Margins too large on page {i + 1}, skipping crop for this page.")
                else:
                    page.mediabox.lower_left = (new_ll_x, new_ll_y)
                    page.mediabox.upper_right = (new_ur_x, new_ur_y)
                    
                    page.cropbox.lower_left = (new_ll_x, new_ll_y)
                    page.cropbox.upper_right = (new_ur_x, new_ur_y)

            writer.add_page(page)

        out_io = io.BytesIO()
        writer.write(out_io)
        out_io.seek(0)
        return out_io

    except Exception as exc:
        raise RuntimeError(f"Failed to crop PDF: {exc}") from exc
