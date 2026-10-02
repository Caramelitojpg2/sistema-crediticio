from pathlib import Path
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)

BASE_DIR = Path(__file__).resolve().parent
REPORTS_DIR = BASE_DIR / "reports"

def generate_pdf(client):
    REPORTS_DIR.mkdir(exist_ok=True)

    filename = f"reporte_{client['dni']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    output = REPORTS_DIR / filename

    doc = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "TitleCustom",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=18,
        spaceAfter=16
    )

    small = ParagraphStyle(
        "Small",
        parent=styles["Normal"],
        fontSize=8,
        textColor=colors.grey
    )

    story = []
    story.append(Paragraph("REPORTE DE HISTORIAL CREDITICIO", title))
    story.append(Paragraph(
        "DOCUMENTO DE DEMOSTRACIÓN — DATOS FICTICIOS",
        ParagraphStyle("warning", parent=styles["Normal"], alignment=TA_CENTER,
                       textColor=colors.red, fontSize=10)
    ))
    story.append(Spacer(1, 15))

    client_data = [
        ["DNI", client["dni"]],
        ["Nombres", client["nombres"]],
        ["Apellidos", client["apellidos"]],
        ["Resultado", client["resultado"]],
        ["Fecha de consulta", datetime.now().strftime("%d/%m/%Y %H:%M")],
    ]

    info_table = Table(client_data, colWidths=[130, 360])
    info_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,0), (0,-1), colors.lightgrey),
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("PADDING", (0,0), (-1,-1), 7),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 20))

    story.append(Paragraph("DETALLE DE OBLIGACIONES", styles["Heading2"]))

    data = [["Entidad", "Tipo", "Estado", "Monto (S/.)", "Fecha"]]
    for item in client["obligaciones"]:
        data.append([
            item["entidad"],
            item["tipo"],
            item["estado"],
            f"{item['monto']:.2f}",
            item["fecha"]
        ])

    if len(data) == 1:
        data.append(["Sin registros", "-", "-", "0.00", "-"])

    table = Table(data, colWidths=[105, 105, 85, 75, 90], repeatRows=1)
    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#dddddd")),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("ALIGN", (3,1), (3,-1), "RIGHT"),
        ("PADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(table)
    story.append(Spacer(1, 25))

    story.append(Paragraph(
        "Este reporte pertenece a una versión de demostración del sistema. "
        "Los datos son ficticios y no constituyen un reporte real de una central "
        "de riesgo ni de Equifax/Infocorp.",
        small
    ))

    doc.build(story)
    return str(output)
