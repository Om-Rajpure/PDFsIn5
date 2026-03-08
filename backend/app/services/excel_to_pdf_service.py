import io
import time
import logging
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

logger = logging.getLogger(__name__)

def excel_to_pdf_service(file_bytes: bytes) -> io.BytesIO:
    """
    Convert an Excel file to PDF using pandas and reportlab.
    
    Args:
        file_bytes (bytes): The raw bytes of the Excel file (.xlsx or .xls).
        
    Returns:
        io.BytesIO: The generated PDF buffer.
    """
    t_load_start = time.time()
    try:
        # Load the entire workbook into a dictionary of DataFrames
        workbook = pd.read_excel(io.BytesIO(file_bytes), sheet_name=None)
    except Exception as e:
        logger.error(f"Failed to parse Excel file: {e}")
        raise ValueError("Failed to read Excel file. Please ensure it is a valid .xlsx or .xls file.")

    t_parse = time.time() - t_load_start
    logger.info(f"Excel to PDF: Excel parsed in {t_parse:.3f}s")

    if not workbook:
        raise ValueError("The Excel file contains no sheets.")

    t_gen_start = time.time()
    
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )
    
    elements = []
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    
    # Process each sheet
    for i, (sheet_name, df) in enumerate(workbook.items()):
        # Add a page break between sheets, except for the first one
        if i > 0:
            elements.append(PageBreak())
            
        # Add sheet title
        elements.append(Paragraph(f"Sheet: {sheet_name}", title_style))
        elements.append(Spacer(1, 10))
        
        # If the sheet is empty, add a small placeholder
        if df.empty:
            elements.append(Paragraph("<i>This sheet is empty.</i>", styles['Normal']))
            continue

        # Get the headers
        columns = df.columns.tolist()
        
        # Convert DataFrame to list of lists, handling NaNs
        # Fill NaN values with an empty string so they render nicely in ReportLab
        data = [columns] + df.fillna("").values.tolist()
        
        # Convert all cell values to strings to prevent ReportLab rendering errors
        data = [[str(cell) for cell in row] for row in data]
        
        # Create ReportLab Table
        # Auto-sizing is generally fine for small sheets. 
        # For larger sheets, we let ReportLab split the table across pages.
        t = Table(data, repeatRows=1)
        
        # Apply basic styling
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            
            # Content styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d0d0d0')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(t)

    # Build PDF
    try:
        doc.build(elements)
    except Exception as e:
        logger.error(f"Failed to generate PDF: {e}")
        raise ValueError(f"Failed to generate PDF. The file may be too large or complex.")

    t_gen = time.time() - t_gen_start
    logger.info(f"Excel to PDF: PDF generated in {t_gen:.3f}s")
    logger.info(f"Excel to PDF: Total processing time: {t_parse + t_gen:.3f}s")

    pdf_buffer.seek(0)
    return pdf_buffer
