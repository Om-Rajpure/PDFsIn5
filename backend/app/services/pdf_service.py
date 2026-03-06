"""
pdf_service.py
--------------
Stub module for PDF processing operations.
Each function will be implemented as the corresponding tool page is built.
"""


def merge_pdfs(input_paths: list[str], output_path: str) -> str:
    """
    Merge multiple PDFs into a single file.
    TODO: implement with pypdf or PyMuPDF.
    """
    raise NotImplementedError("merge_pdfs is not yet implemented.")


def split_pdf(input_path: str, output_dir: str, pages: list[int] | None = None) -> list[str]:
    """
    Split a PDF into individual pages or specified page ranges.
    TODO: implement with pypdf.
    """
    raise NotImplementedError("split_pdf is not yet implemented.")


def compress_pdf(input_path: str, output_path: str, quality: str = "medium") -> str:
    """
    Reduce the file size of a PDF.
    TODO: implement with Ghostscript or PyMuPDF.
    """
    raise NotImplementedError("compress_pdf is not yet implemented.")


def rotate_pdf(input_path: str, output_path: str, degrees: int = 90) -> str:
    """
    Rotate all pages of a PDF by the specified degree.
    TODO: implement with pypdf.
    """
    raise NotImplementedError("rotate_pdf is not yet implemented.")


def protect_pdf(input_path: str, output_path: str, password: str) -> str:
    """
    Add password protection to a PDF.
    TODO: implement with pypdf.
    """
    raise NotImplementedError("protect_pdf is not yet implemented.")


def unlock_pdf(input_path: str, output_path: str, password: str) -> str:
    """
    Remove password from a PDF.
    TODO: implement with pypdf.
    """
    raise NotImplementedError("unlock_pdf is not yet implemented.")


def images_to_pdf(image_paths: list[str], output_path: str) -> str:
    """
    Convert a list of images (JPG/PNG) into a single PDF.
    TODO: implement with Pillow.
    """
    raise NotImplementedError("images_to_pdf is not yet implemented.")


def pdf_to_images(input_path: str, output_dir: str, fmt: str = "jpg") -> list[str]:
    """
    Convert PDF pages to images.
    TODO: implement with PyMuPDF (fitz).
    """
    raise NotImplementedError("pdf_to_images is not yet implemented.")
