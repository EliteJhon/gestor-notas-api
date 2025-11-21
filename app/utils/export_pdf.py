# app/utils/export_pdf.py

from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from fastapi.responses import StreamingResponse

def export_notes_to_pdf(notes, filename="notas.pdf"):
    """
    Exporta una lista de notas a un archivo PDF y lo devuelve como StreamingResponse.
    """
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Título
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, height - 50, "Reporte de Notas")

    y = height - 100
    p.setFont("Helvetica", 12)

    if not notes:
        p.drawString(100, y, "No hay notas disponibles.")
    else:
        for note in notes:
            p.drawString(80, y, f"ID: {note.id}")
            y -= 15
            p.drawString(80, y, f"Título: {note.titulo}")  # 👈 CORREGIDO
            y -= 15
            p.drawString(80, y, f"Contenido: {note.contenido}")  # 👈 CORREGIDO
            y -= 15
            p.drawString(80, y, f"Estado: {note.estado}")  # 👈 CORREGIDO
            y -= 15
            p.drawString(80, y, f"Creador ID: {note.creador_id}")
            y -= 15
            p.drawString(80, y, f"Destinatario ID: {note.destinatario_id}")
            y -= 30

            # Si se acaba la página
            if y < 100:
                p.showPage()
                p.setFont("Helvetica", 12)
                y = height - 100

    p.save()
    buffer.seek(0)

    headers = {"Content-Disposition": f"attachment; filename={filename}"}
    return StreamingResponse(buffer, media_type="application/pdf", headers=headers)