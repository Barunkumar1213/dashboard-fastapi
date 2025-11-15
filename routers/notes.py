from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import uuid
from datetime import datetime

from models.note import NoteCreate, NoteUpdate, NoteResponse
from models.user import UserResponse
from routers.auth import get_current_user
from database.db_file import db

router = APIRouter()

def check_note_access(current_user: dict, note: dict, action: str = "read"):
    """Check if user can access note based on role"""
    # Admin can access any note
    if current_user.get("role") == "admin":
        return True
    
    # Regular users can only access their own notes
    if note["user_id"] == current_user["id"]:
        return True
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"Access denied: Cannot {action} this note"
    )

@router.post("/", response_model=NoteResponse)
def create_note(note: NoteCreate, current_user: dict = Depends(get_current_user)):
    new_note = {
        "id": str(uuid.uuid4()),
        "title": note.title,
        "description": note.description,
        "user_id": current_user["id"],
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    created_note = db.add_note(new_note)
    return NoteResponse(**created_note)

@router.get("/", response_model=List[NoteResponse])
def get_notes(current_user: dict = Depends(get_current_user)):
    notes = db.get_notes()
    
    if current_user["role"] == "admin":
        # Admin can see all notes
        return [NoteResponse(**note) for note in notes]
    else:
        # Regular users can only see their own notes
        user_notes = [note for note in notes if note["user_id"] == current_user["id"]]
        return [NoteResponse(**note) for note in user_notes]

@router.get("/{note_id}", response_model=NoteResponse)
def get_note(note_id: str, current_user: dict = Depends(get_current_user)):
    note = db.get_note_by_id(note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    check_note_access(current_user, note, "read")
    return NoteResponse(**note)

@router.put("/{note_id}", response_model=NoteResponse)
def update_note(note_id: str, note_update: NoteUpdate, current_user: dict = Depends(get_current_user)):
    note = db.get_note_by_id(note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    check_note_access(current_user, note, "update")
    
    # Update note with new data
    updated_data = note_update.dict(exclude_unset=True)
    updated_data["updated_at"] = datetime.now()
    
    updated_note = db.update_note(note_id, updated_data)
    if not updated_note:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update note"
        )
    
    return NoteResponse(**updated_note)

@router.delete("/{note_id}")
def delete_note(note_id: str, current_user: dict = Depends(get_current_user)):
    note = db.get_note_by_id(note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    check_note_access(current_user, note, "delete")
    
    success = db.delete_note(note_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete note"
        )
    
    return {"message": "Note deleted successfully"}