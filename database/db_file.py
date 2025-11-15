import json
import os
from typing import Dict, List, Any
from datetime import datetime

class FileDatabase:
    def __init__(self, file_path: str = "database.json"):
        self.file_path = file_path
        self.data = self._load_data()
    
    def _load_data(self) -> Dict[str, List[Any]]:
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                return json.load(f)
        return {
            "users": [],
            "notes": []
        }
    
    def _save_data(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.data, f, indent=2, default=str)
    
    def get_users(self) -> List[Dict]:
        return self.data["users"]
    
    def add_user(self, user: Dict) -> Dict:
        self.data["users"].append(user)
        self._save_data()
        return user
    
    def get_user_by_email(self, email: str) -> Dict:
        for user in self.data["users"]:
            if user["email"] == email:
                return user
        return None
    
    def get_user_by_id(self, user_id: str) -> Dict:
        for user in self.data["users"]:
            if user["id"] == user_id:
                return user
        return None
    
    def get_notes(self) -> List[Dict]:
        return self.data["notes"]
    
    def add_note(self, note: Dict) -> Dict:
        self.data["notes"].append(note)
        self._save_data()
        return note
    
    def update_note(self, note_id: str, updated_note: Dict) -> Dict:
        for i, note in enumerate(self.data["notes"]):
            if note["id"] == note_id:
                self.data["notes"][i] = {**note, **updated_note}
                self._save_data()
                return self.data["notes"][i]
        return None
    
    def delete_note(self, note_id: str) -> bool:
        for i, note in enumerate(self.data["notes"]):
            if note["id"] == note_id:
                del self.data["notes"][i]
                self._save_data()
                return True
        return False
    
    def get_note_by_id(self, note_id: str) -> Dict:
        for note in self.data["notes"]:
            if note["id"] == note_id:
                return note
        return None

# Global database instance
db = FileDatabase("database.json")