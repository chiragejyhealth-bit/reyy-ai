from models.perplexity import PerplexityFeedItem

from fpdf import FPDF

def save_item_as_pdf(item: PerplexityFeedItem, pdf_path: str) -> None:
    """
    Convert the item to PDF and save it at the specified path.
    """
    
    # Create PDF with Unicode support
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=clean_text(item.title), ln=True, align='C')
    pdf.ln(10)
    pdf.multi_cell(0, 10, txt=clean_text(item.bullet_summary_preload))
    
    pdf.output(pdf_path)

    # Clean text to handle any problematic characters
def clean_text(text):
    if not text:
        return ""
    # Replace problematic Unicode characters with ASCII equivalents
    return (text.replace('\u2014', '-')  # em dash
                .replace('\u2013', '-')   # en dash
                .replace('\u2018', "'")   # left single quote
                .replace('\u2019', "'")   # right single quote
                .replace('\u201c', '"')   # left double quote
                .replace('\u201d', '"'))  # right double quote