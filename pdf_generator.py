"""PDF generation for JewelCalc invoices"""
from io import BytesIO
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
import base64


def create_invoice_pdf(invoice, items_df, customer):
    """Generate PDF for invoice"""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    x_margin = 40
    y = height - 50
    
    # Title
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, y, "💎 JewelCalc Invoice")
    y -= 40
    
    # Invoice details
    c.setFont("Helvetica", 11)
    c.drawString(x_margin, y, f"Invoice No: {invoice['invoice_no']}")
    c.drawString(width - 200, y, f"Date: {invoice['date']}")
    y -= 20
    
    # Customer details
    if customer:
        c.drawString(x_margin, y, f"Account: {customer.get('account_no', '')}")
        y -= 16
        c.drawString(x_margin, y, f"Customer: {customer.get('name', '')}")
        y -= 16
        c.drawString(x_margin, y, f"Phone: {customer.get('phone', '')}")
        y -= 16
        if customer.get('address'):
            c.drawString(x_margin, y, f"Address: {customer.get('address', '')}")
            y -= 16
    
    y -= 10
    
    # Table header
    c.setFont("Helvetica-Bold", 10)
    headers = ["No", "Metal", "Weight(g)", "Rate", "Item Val", "Wastage", "Making", "Total"]
    positions = [x_margin, x_margin+35, x_margin+100, x_margin+170, x_margin+230, x_margin+300, x_margin+370, x_margin+440]
    
    for i, header in enumerate(headers):
        c.drawString(positions[i], y, header)
    
    y -= 16
    c.line(x_margin, y, width - x_margin, y)
    y -= 16
    
    # Table rows
    c.setFont("Helvetica", 10)
    for _, row in items_df.iterrows():
        if y < 80:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 10)
        
        c.drawString(positions[0], y, str(int(row['item_no'])))
        c.drawString(positions[1], y, str(row['metal']))
        c.drawRightString(positions[2]+40, y, f"{row['weight']:.2f}")
        c.drawRightString(positions[3]+40, y, f"{row['rate']:.2f}")
        c.drawRightString(positions[4]+50, y, f"{row['item_value']:.2f}")
        c.drawRightString(positions[5]+50, y, f"{row['wastage_amount']:.2f}")
        c.drawRightString(positions[6]+50, y, f"{row['making_amount']:.2f}")
        c.drawRightString(positions[7]+60, y, f"{row['line_total']:.2f}")
        y -= 14
    
    y -= 10
    c.line(x_margin, y, width - x_margin, y)
    y -= 20
    
    # Summary
    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(width - x_margin, y, f"Subtotal: ₹{invoice['subtotal']:.2f}")
    y -= 18
    
    if invoice.get('discount_percent', 0) > 0:
        c.drawRightString(width - x_margin, y, 
                         f"Discount ({invoice['discount_percent']:.2f}%): ₹{invoice['discount_amount']:.2f}")
        y -= 18
    
    c.drawRightString(width - x_margin, y, 
                     f"CGST ({invoice['cgst_percent']:.2f}%): ₹{invoice['cgst_amount']:.2f}")
    y -= 18
    c.drawRightString(width - x_margin, y, 
                     f"SGST ({invoice['sgst_percent']:.2f}%): ₹{invoice['sgst_amount']:.2f}")
    y -= 18
    
    c.line(width - 200, y, width - x_margin, y)
    y -= 20
    
    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(width - x_margin, y, f"Total: ₹{invoice['total']:.2f}")
    
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


def get_pdf_download_link(pdf_buffer, filename="invoice.pdf"):
    """Generate download link for PDF"""
    b64 = base64.b64encode(pdf_buffer.read()).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}">📄 Download PDF</a>'
    return href


def create_thermal_invoice_pdf(invoice, items_df, customer):
    """Generate thermal printer optimized PDF (80mm width) with enhanced details"""
    buffer = BytesIO()
    # Thermal printer paper is typically 80mm (about 226 points)
    page_width = 226
    
    # First, calculate required height
    y_tracking = 20  # Start from top
    line_height = 11  # Standard line height
    
    # Title
    y_tracking += 18
    # Invoice details
    y_tracking += 12 + 12  # Invoice no + Date
    y_tracking += 15
    # Customer details
    if customer:
        y_tracking += 11  # Account
        y_tracking += 11  # Name
        y_tracking += 11  # Phone
        if customer.get('address'):
            y_tracking += 11  # Address
    y_tracking += 5 + 12  # Line + Item Details header
    
    # Items
    for _, row in items_df.iterrows():
        y_tracking += 10  # Item number and metal
        y_tracking += 10  # Weight and rate
        y_tracking += 10  # Item value
        y_tracking += 10  # Wastage
        y_tracking += 10  # Making
        y_tracking += 10  # Line total
        y_tracking += 12  # Spacing
    
    # Summary section
    y_tracking += 5 + 12  # Line + Subtotal
    y_tracking += 11  # Each tax line
    if invoice.get('discount_percent', 0) > 0:
        y_tracking += 11
    y_tracking += 11  # CGST
    y_tracking += 11  # SGST
    y_tracking += 13 + 13  # Line + Total
    y_tracking += 20  # Thank you message
    
    # Add some padding at the end
    page_height = y_tracking + 20
    
    c = canvas.Canvas(buffer, pagesize=(page_width, page_height))
    x_margin = 10
    y = page_height - 20
    center = page_width / 2
    
    # Title - smaller for thermal
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(center, y, "JewelCalc")
    y -= 18
    
    # Invoice details
    c.setFont("Helvetica", 8)
    c.drawCentredString(center, y, f"Invoice: {invoice['invoice_no']}")
    y -= 12
    c.drawCentredString(center, y, f"Date: {invoice['date']}")
    y -= 15
    
    # Customer details
    if customer:
        c.drawString(x_margin, y, f"A/c: {customer.get('account_no', '')}")
        y -= 11
        c.drawString(x_margin, y, f"Name: {customer.get('name', '')}")
        y -= 11
        c.drawString(x_margin, y, f"Ph: {customer.get('phone', '')}")
        y -= 11
        if customer.get('address'):
            c.drawString(x_margin, y, f"Addr: {customer.get('address', '')}")
            y -= 11
    
    y -= 5
    c.line(x_margin, y, page_width - x_margin, y)
    y -= 12
    
    # Items - enhanced with more details
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x_margin, y, "Item Details")
    y -= 12
    
    c.setFont("Helvetica", 7)
    for _, row in items_df.iterrows():
        c.setFont("Helvetica-Bold", 7)
        c.drawString(x_margin, y, f"{int(row['item_no'])}. {row['metal']}")
        y -= 10
        c.setFont("Helvetica", 7)
        c.drawString(x_margin + 5, y, f"Weight: {row['weight']:.3f}g @ ₹{row['rate']:.2f}/g")
        y -= 10
        c.drawString(x_margin + 5, y, f"Item Value: ₹{row['item_value']:.2f}")
        y -= 10
        c.drawString(x_margin + 5, y, f"Wastage ({row['wastage_percent']:.1f}%): ₹{row['wastage_amount']:.2f}")
        y -= 10
        c.drawString(x_margin + 5, y, f"Making ({row['making_percent']:.1f}%): ₹{row['making_amount']:.2f}")
        y -= 10
        c.setFont("Helvetica-Bold", 7)
        c.drawString(x_margin + 5, y, f"Line Total: ₹{row['line_total']:.2f}")
        y -= 12
        c.setFont("Helvetica", 7)
    
    y -= 5
    c.line(x_margin, y, page_width - x_margin, y)
    y -= 12
    
    # Summary
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x_margin, y, "Subtotal:")
    c.drawRightString(page_width - x_margin, y, f"₹{invoice['subtotal']:.2f}")
    y -= 11
    
    if invoice.get('discount_percent', 0) > 0:
        c.setFont("Helvetica", 8)
        c.drawString(x_margin, y, f"Discount ({invoice['discount_percent']:.1f}%):")
        c.drawRightString(page_width - x_margin, y, f"-₹{invoice['discount_amount']:.2f}")
        y -= 11
    
    c.setFont("Helvetica", 8)
    c.drawString(x_margin, y, f"CGST ({invoice['cgst_percent']:.1f}%):")
    c.drawRightString(page_width - x_margin, y, f"₹{invoice['cgst_amount']:.2f}")
    y -= 11
    c.drawString(x_margin, y, f"SGST ({invoice['sgst_percent']:.1f}%):")
    c.drawRightString(page_width - x_margin, y, f"₹{invoice['sgst_amount']:.2f}")
    y -= 11
    
    c.line(x_margin, y, page_width - x_margin, y)
    y -= 13
    
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x_margin, y, "TOTAL:")
    c.drawRightString(page_width - x_margin, y, f"₹{invoice['total']:.2f}")
    
    y -= 20
    c.setFont("Helvetica", 7)
    c.drawCentredString(center, y, "Thank you for your business!")
    
    # End PDF here - don't add more pages
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
