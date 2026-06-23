import json
import os
from datetime import datetime
from models.password_entry import PasswordEntry

class Database:
    def __init__(self, master_password):
        self.master_password = master_password
        self.data_dir = os.path.join(os.environ['APPDATA'], 'PasswordManager')
        self.data_file = os.path.join(self.data_dir, 'passwords.json')
        self.entries = []
        self._ensure_directory()
        self._load_data()
    
    def _ensure_directory(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def _load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.entries = [PasswordEntry.from_dict(item) for item in data]
            except:
                self.entries = []
        else:
            self.entries = []
            self._save_data()
    
    def _save_data(self):
        data = [entry.to_dict() for entry in self.entries]
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def reset_all_data(self):
        if os.path.exists(self.data_file):
            os.remove(self.data_file)
        self.entries = []
        self._save_data()
        return True
    
    def get_all(self):
        return sorted(self.entries, key=lambda x: x.platform)
    
    def search(self, term):
        if not term:
            return self.get_all()
        term = term.lower()
        return [e for e in self.entries if term in e.platform.lower() or term in e.username.lower()]
    
    def get_categories(self):
        categories = list(set(e.category for e in self.entries))
        return sorted(categories)
    
    def add(self, entry):
        self.entries.append(entry)
        self._save_data()
    
    def update(self, entry):
        for i, e in enumerate(self.entries):
            if e.id == entry.id:
                self.entries[i] = entry
                self._save_data()
                return True
        return False
    
    def delete(self, entry_id):
        self.entries = [e for e in self.entries if e.id != entry_id]
        self._save_data()