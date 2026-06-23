import tkinter as tk
from tkinter import ttk, messagebox
from models.password_entry import PasswordEntry
from datetime import datetime

class AddEditDialog:
    def __init__(self, parent, database, crypto, entry=None):
        self.parent = parent
        self.db = database
        self.crypto = crypto
        self.entry = entry
        self.result = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Password" if entry else "Add New Password")
        self.dialog.geometry("520x550")
        self.dialog.resizable(False, False)
        self.dialog.configure(bg='#0f0f1a')
        
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        if entry:
            self.load_entry()
        
        self.dialog.bind('<Return>', lambda e: self.save())
    
    def setup_ui(self):
        main_frame = tk.Frame(self.dialog, bg='#0f0f1a')
        main_frame.pack(fill='both', expand=True, padx=30, pady=25)
        
        tk.Label(main_frame, text="Password Details", 
                font=('Segoe UI', 16, 'bold'), bg='#0f0f1a', fg='#ffffff').pack(pady=(0, 20))
        
        form_frame = tk.Frame(main_frame, bg='#0f0f1a')
        form_frame.pack(fill='both', expand=True)
        
        tk.Label(form_frame, text="Platform *", bg='#0f0f1a', fg='#a8d8ea',
                font=('Segoe UI', 10)).pack(anchor='w', pady=(0, 3))
        self.platform_entry = tk.Entry(form_frame, bg='#1a1a2e', fg='white',
                                      insertbackground='#e94560', font=('Segoe UI', 11),
                                      relief='flat', highlightthickness=1,
                                      highlightcolor='#e94560', highlightbackground='#1a1a2e')
        self.platform_entry.pack(fill='x', pady=(0, 12), ipady=5)
        
        tk.Label(form_frame, text="Username *", bg='#0f0f1a', fg='#a8d8ea',
                font=('Segoe UI', 10)).pack(anchor='w', pady=(0, 3))
        self.username_entry = tk.Entry(form_frame, bg='#1a1a2e', fg='white',
                                      insertbackground='#e94560', font=('Segoe UI', 11),
                                      relief='flat', highlightthickness=1,
                                      highlightcolor='#e94560', highlightbackground='#1a1a2e')
        self.username_entry.pack(fill='x', pady=(0, 12), ipady=5)
        
        tk.Label(form_frame, text="Password *", bg='#0f0f1a', fg='#a8d8ea',
                font=('Segoe UI', 10)).pack(anchor='w', pady=(0, 3))
        
        password_frame = tk.Frame(form_frame, bg='#0f0f1a')
        password_frame.pack(fill='x', pady=(0, 12))
        
        self.password_entry = tk.Entry(password_frame, bg='#1a1a2e', fg='white',
                                      insertbackground='#e94560', font=('Segoe UI', 11),
                                      show='*', relief='flat', highlightthickness=1,
                                      highlightcolor='#e94560', highlightbackground='#1a1a2e')
        self.password_entry.pack(side='left', fill='x', expand=True, ipady=5)
        
        btn_generate = tk.Button(password_frame, text="Generate", 
                                command=self.generate_password,
                                bg='#3b82f6', fg='white', font=('Segoe UI', 9, 'bold'),
                                relief='flat', cursor='hand2', padx=12, pady=3)
        btn_generate.pack(side='right', padx=(5, 0))
        
        tk.Label(form_frame, text="Category", bg='#0f0f1a', fg='#a8d8ea',
                font=('Segoe UI', 10)).pack(anchor='w', pady=(0, 3))
        
        categories = self.db.get_categories()
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(form_frame, textvariable=self.category_var,
                                          values=['General'] + categories,
                                          font=('Segoe UI', 10), state='readonly')
        self.category_combo.pack(fill='x', pady=(0, 12), ipady=3)
        self.category_var.set('General')
        
        tk.Label(form_frame, text="Notes", bg='#0f0f1a', fg='#a8d8ea',
                font=('Segoe UI', 10)).pack(anchor='w', pady=(0, 3))
        self.notes_text = tk.Text(form_frame, height=4, bg='#1a1a2e', fg='white',
                                 font=('Segoe UI', 10), wrap='word',
                                 relief='flat', highlightthickness=1,
                                 highlightcolor='#e94560', highlightbackground='#1a1a2e')
        self.notes_text.pack(fill='x', pady=(0, 15))
        
        btn_frame = tk.Frame(main_frame, bg='#0f0f1a')
        btn_frame.pack(fill='x', pady=(0, 5))
        
        btn_save = tk.Button(btn_frame, text="Save", command=self.save,
                            bg='#10b981', fg='white', font=('Segoe UI', 11, 'bold'),
                            relief='flat', cursor='hand2', padx=25, pady=8)
        btn_save.pack(side='right', padx=(5, 0))
        
        btn_cancel = tk.Button(btn_frame, text="Cancel", command=self.dialog.destroy,
                              bg='#ef4444', fg='white', font=('Segoe UI', 11),
                              relief='flat', cursor='hand2', padx=25, pady=8)
        btn_cancel.pack(side='right')
    
    def load_entry(self):
        self.platform_entry.insert(0, self.entry.platform)
        self.username_entry.insert(0, self.entry.username)
        self.password_entry.insert(0, self.crypto.decrypt(self.entry.encrypted_password))
        self.category_var.set(self.entry.category)
        self.notes_text.insert('1.0', self.entry.notes)
    
    def generate_password(self):
        password = self.crypto.generate_strong_password(16)
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, password)
    
    def save(self):
        platform = self.platform_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        category = self.category_var.get()
        notes = self.notes_text.get('1.0', tk.END).strip()
        
        if not platform or not username or not password:
            messagebox.showwarning("Warning", "Platform, username and password are required!")
            return
        
        if self.entry:
            self.entry.platform = platform
            self.entry.username = username
            self.entry.encrypted_password = self.crypto.encrypt(password)
            self.entry.category = category
            self.entry.notes = notes
            self.entry.updated_at = datetime.now().isoformat()
            self.db.update(self.entry)
        else:
            encrypted = self.crypto.encrypt(password)
            new_entry = PasswordEntry(platform, username, encrypted, category)
            new_entry.notes = notes
            self.db.add(new_entry)
        
        self.result = True
        self.dialog.destroy()