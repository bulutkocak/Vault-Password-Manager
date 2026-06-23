import uuid
from datetime import datetime

class PasswordEntry:
    def __init__(self, platform="", username="", encrypted_password="", category="General"):
        self.id = str(uuid.uuid4())
        self.platform = platform
        self.username = username
        self.encrypted_password = encrypted_password
        self.category = category
        self.notes = ""
        self.created_at = datetime.now().isoformat()
        self.updated_at = None
    
    def to_dict(self):
        return {
            'id': self.id,
            'platform': self.platform,
            'username': self.username,
            'encrypted_password': self.encrypted_password,
            'category': self.category,
            'notes': self.notes,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data):
        entry = cls(
            data['platform'],
            data['username'],
            data['encrypted_password'],
            data.get('category', 'General')
        )
        entry.id = data['id']
        entry.notes = data.get('notes', '')
        entry.created_at = data['created_at']
        entry.updated_at = data.get('updated_at')
        return entry