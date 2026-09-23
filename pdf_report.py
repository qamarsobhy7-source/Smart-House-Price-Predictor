"""PDF Report Generator for Smart House Price Predictor"""
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT


def generate_pdf_report(prediction_data, property_data, model_metadata):
    """Generate a PDF report for a property prediction.

    Args:
        prediction_data: dict with price, lower_bound, upper_bound, price_per_sqm
        property_data: dict with area, bedrooms, bathrooms, city, town, district, etc.
        model_metadata: dict with r2, mape, model_name

    Returns:
        BytesIO buffer containing PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle', parent=styles['Title'],
        fontSize=24, textColor=colors.HexColor('#667eea'),
        spaceAfter=30, alignment=TA_CENTER,
    )
    heading_style = ParagraphStyle(
        'CustomHeading', parent=styles['Heading1'],
        fontSize=14, textColor=colors.HexColor('#764ba2'),
        spaceBefore=15, spaceAfter=10,
    )
    body_style = ParagraphStyle(
        'CustomBody', parent=styles['BodyText'],
        fontSize=11, leading=16,
    )

    story = []

    # Header
    story.append(Paragraph("Smart House Price Predictor", title_style))
    story.append(Paragraph("AI-Powered Property Valuation Report", styles['Heading2']))
    story.append(Spacer(1, 20))

    # Date
    story.append(Paragraph(
        f"<b>Report Date:</b> {datetime.now().strftime('%B %d, %Y')}",
        body_style
    ))
    story.append(Spacer(1, 20))

    # Price section
    story.append(Paragraph("Estimated Property Price", heading_style))
    price = prediction_data['price']

    price_table = Table([
        ['Estimated Price', f"{price:,.0f} EGP"],
        ['In Millions', f"{price/1_000_000:.2f}M EGP"],
        ['Confidence Lower Bound', f"{prediction_data['lower_bound']:,.0f} EGP"],
        ['Confidence Upper Bound', f"{prediction_data['upper_bound']:,.0f} EGP"],
        ['Price per m²', f"{prediction_data['price_per_sqm']:,.0f} EGP/m²"],
    ], colWidths=[7*cm, 8*cm])
    price_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(price_table)
    story.append(Spacer(1, 20))

    # Property details
    story.append(Paragraph("Property Details", heading_style))
    prop_table = Table([
        ['Area', f"{property_data['area']} m²"],
        ['Bedrooms', str(property_data['bedrooms'])],
        ['Bathrooms', str(property_data['bathrooms'])],
        ['City', property_data['city']],
        ['Town', property_data['town']],
        ['District', property_data['district']],
        ['Subdistrict', property_data['subdistrict']],
        ['Furnished', property_data['furnished']],
        ['Completion Status', property_data['completion_status']],
    ], colWidths=[7*cm, 8*cm])
    prop_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.lightgrey),
    ]))
    story.append(prop_table)
    story.append(Spacer(1, 20))

    # Model info
    story.append(Paragraph("Model Information", heading_style))
    model_table = Table([
        ['Model Type', model_metadata.get('model_name', 'N/A')],
        ['R² Score', f"{model_metadata.get('r2', 0):.4f}"],
        ['MAPE (avg error)', f"{model_metadata.get('mape', 0):.2f}%"],
        ['Training Samples', f"{model_metadata.get('n_train', 0):,}"],
    ], colWidths=[7*cm, 8*cm])
    model_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.lightgrey),
    ]))
    story.append(model_table)
    story.append(Spacer(1, 30))

    # Disclaimer
    story.append(Paragraph(
        "<i>⚠️ Disclaimer: This is an AI-generated estimation for educational purposes. "
        "It does not constitute a professional real estate appraisal. "
        "Actual market prices may vary based on factors not captured by the model.</i>",
        body_style
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer
