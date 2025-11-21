# app/routes/notes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas, database
from ..auth import get_current_user

router = APIRouter(
    prefix="/notes",
    tags=["Notes"]
)

get_db = database.get_db


@router.post("/", response_model=schemas.NoteOut)
def create_note(
    note: schemas.NoteCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    new_note = models.Note(
        titulo=note.titulo,
        contenido=note.contenido,
        estado=note.estado or "pendiente",
        creador_id=current_user.id,
        destinatario_id=note.destinatario_id or current_user.id
    )
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note


@router.get("/", response_model=List[schemas.NoteOut])
def get_all_notes(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.rol != "administrador":  # 👈 CORREGIDO
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para ver todas las notas"
        )
    notes = db.query(models.Note).all()
    return notes


@router.get("/my", response_model=List[schemas.NoteOut])
def get_my_notes(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Trae notas donde el usuario es creador o destinatario
    notes = db.query(models.Note).filter(
        (models.Note.creador_id == current_user.id) |
        (models.Note.destinatario_id == current_user.id)
    ).all()
    return notes


@router.put("/{note_id}", response_model=schemas.NoteOut)
def update_note(
    note_id: int,
    updated_note: schemas.NoteCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    note = db.query(models.Note).filter(models.Note.id == note_id).first()

    if not note:
        raise HTTPException(status_code=404, detail="Nota no encontrada")

    if note.creador_id != current_user.id and current_user.rol != "administrador":  # 👈 CORREGIDO
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para modificar esta nota"
        )

    note.titulo = updated_note.titulo
    note.contenido = updated_note.contenido
    note.estado = updated_note.estado
    if updated_note.destinatario_id is not None:
        note.destinatario_id = updated_note.destinatario_id

    db.commit()
    db.refresh(note)
    return note


@router.delete("/{note_id}")
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    note = db.query(models.Note).filter(models.Note.id == note_id).first()

    if not note:
        raise HTTPException(status_code=404, detail="Nota no encontrada")

    if note.creador_id != current_user.id and current_user.rol != "administrador":  # 👈 CORREGIDO
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para eliminar esta nota"
        )

    db.delete(note)
    db.commit()
    return {"detail": "Nota eliminada correctamente"}


@router.get("/export/excel")
def export_notes_excel(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.rol == "administrador":  # 👈 CORREGIDO
        notes = db.query(models.Note).all()
        filename = "todas_las_notas.xlsx"
    else:
        notes = db.query(models.Note).filter(
            (models.Note.creador_id == current_user.id) |
            (models.Note.destinatario_id == current_user.id)
        ).all()
        filename = f"notas_usuario_{current_user.id}.xlsx"

    if not notes:
        raise HTTPException(status_code=404, detail="No hay notas para exportar")

    from ..utils.export_excel import export_notes_to_excel
    return export_notes_to_excel(notes, filename)


@router.get("/export/pdf")
def export_notes_pdf(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.rol == "administrador":  # 👈 CORREGIDO
        notes = db.query(models.Note).all()
        filename = "todas_las_notas.pdf"
    else:
        notes = db.query(models.Note).filter(
            (models.Note.creador_id == current_user.id) |
            (models.Note.destinatario_id == current_user.id)
        ).all()
        filename = f"notas_usuario_{current_user.id}.pdf"

    if not notes:
        raise HTTPException(status_code=404, detail="No hay notas para exportar")

    from ..utils.export_pdf import export_notes_to_pdf
    return export_notes_to_pdf(notes, filename)


@router.get("/admin/users_with_notes")
def get_users_with_notes(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.rol != "administrador":  # 👈 CORREGIDO
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos de administrador"
        )

    users = db.query(models.User).all()
    result = []
    for user in users:
        notas = db.query(models.Note).filter(
            (models.Note.creador_id == user.id) |
            (models.Note.destinatario_id == user.id)
        ).all()
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "rol": user.rol,
            "notas": [
                {
                    "id": note.id,
                    "titulo": note.titulo,
                    "contenido": note.contenido,
                    "estado": note.estado
                } for note in notas
            ]
        }
        result.append(user_data)
    return result