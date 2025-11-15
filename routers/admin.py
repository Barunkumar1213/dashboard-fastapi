from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from models.note import NoteResponse, NoteUpdate
from models.user import UserResponse
from routers.auth import get_current_user
from database.db_file import db
from datetime import datetime

router = APIRouter()

def require_admin(current_user: dict = Depends(get_current_user)):
    """Dependency to require admin role"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

@router.get("/notes", response_model=List[NoteResponse])
def get_all_notes(admin_user: dict = Depends(require_admin)):
    """Get all notes from all users (admin only)"""
    notes = db.get_notes()
    return [NoteResponse(**note) for note in notes]

@router.put("/notes/{note_id}", response_model=NoteResponse)
def update_any_note(note_id: str, note_update: NoteUpdate, admin_user: dict = Depends(require_admin)):
    """Update any note (admin only)"""
    note = db.get_note_by_id(note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
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

@router.delete("/notes/{note_id}")
def delete_any_note(note_id: str, admin_user: dict = Depends(require_admin)):
    """Delete any note (admin only)"""
    note = db.get_note_by_id(note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    success = db.delete_note(note_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete note"
        )
    
    return {"message": "Note deleted successfully"}

@router.get("/users", response_model=List[UserResponse])
def get_all_users(admin_user: dict = Depends(require_admin)):
    """Get all users (admin only)"""
    users = db.get_users()
    return [UserResponse(**user) for user in users]