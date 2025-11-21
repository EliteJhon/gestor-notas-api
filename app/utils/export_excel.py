# app/utils/export_excel.py

import openpyxl
from io import BytesIO
from fastapi.responses import StreamingResponse

def export_notes_to_excel(notes, filename="notas.xlsx"):
    """
    Exporta una lista de notas a un archivo Excel y lo devuelve como StreamingResponse.
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Notas"

    # Encabezados
    ws.append(["ID", "Título", "Contenido", "Estado", "Creador ID", "Destinatario ID", "Creado En"])

    # Agregar las notas
    for note in notes:
        ws.append([
            note.id,
            note.titulo,  # 👈 CORREGIDO
            note.contenido,  # 👈 CORREGIDO
            note.estado,  # 👈 CORREGIDO
            note.creador_id,
            note.destinatario_id,
            note.creado_en.strftime("%Y-%m-%d %H:%M:%S") if note.creado_en else ""
        ])

    # Guardar en memoria
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    # Devolver archivo descargable
    headers = {"Content-Disposition": f"attachment; filename={filename}"}
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers
    )