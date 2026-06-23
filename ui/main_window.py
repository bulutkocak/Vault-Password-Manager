import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip
from crypto_helper import CryptoHelper
from ui.add_edit_dialog import AddEditDialog
from models.password_entry import PasswordEntry
from datetime import datetime

class MainWindow:
    def __init__(self, master_password, database):
        self.master_password = master_password
        self.db = database
        self.crypto = CryptoHelper(master_password)
        
        self.window = tk.Tk()
        self.window.title("Secure Password Manager")
        self.window.geometry("1100x700")
        self.window.minsize(900, 600)
        self.window.configure(bg='#0f0f1a')
        self.window.eval('tk::PlaceWindow . center')
        
        self.setup_styles()
        self.setup_ui()
        self.load_entries()
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("Custom.Treeview",
                       background='#1a1a2e',
                       foreground='#ffffff',
                       fieldbackground='#1a1a2e',
                       borderwidth=0,
                       font=('Segoe UI', 10))
        style.configure("Custom.Treeview.Heading",
                       background='#16213e',
                       foreground='#a8d8ea',
                       borderwidth=0,
                       font=('Segoe UI', 10, 'bold'))
        style.map("Custom.Treeview.Heading",
                 background=[('active', '#1a1a2e')])
        
        style.configure("Custom.TCombobox",
                       background='#1a1a2e',
                       foreground='#ffffff',
                       fieldbackground='#1a1a2e',
                       borderwidth=0)
    
    def setup_ui(self):
        main_container = tk.Frame(self.window, bg='#0f0f1a')
        main_container.pack(fill='both', expand=True, padx=15, pady=15)
        
        header = tk.Frame(main_container, bg='#0f0f1a', height=60)
        header.pack(fill='x', pady=(0, 15))
        header.pack_propagate(False)
        
        tk.Label(header, text="Password Manager", 
                font=('Segoe UI', 22, 'bold'), bg='#0f0f1a', fg='#ffffff').pack(side='left')
        
        info_frame = tk.Frame(header, bg='#0f0f1a')
        info_frame.pack(side='right')
        
        tk.Label(info_frame, text=f"Passwords: {len(self.db.get_all())}", 
                font=('Segoe UI', 10), bg='#0f0f1a', fg='#6b7280').pack(side='left', padx=10)
        
        btn_lock = tk.Button(info_frame, text="Logout", command=self.on_close,
                            bg='#e94560', fg='white', font=('Segoe UI', 10, 'bold'),
                            relief='flat', cursor='hand2', padx=15, pady=5)
        btn_lock.pack(side='left')
        
        toolbar = tk.Frame(main_container, bg='#1a1a2e', height=50)
        toolbar.pack(fill='x', pady=(0, 15))
        toolbar.pack_propagate(False)
        
        left_toolbar = tk.Frame(toolbar, bg='#1a1a2e')
        left_toolbar.pack(side='left', fill='y', padx=10)
        
        tk.Label(left_toolbar, text="Search:", bg='#1a1a2e', fg='#a8d8ea', 
                font=('Segoe UI', 10)).pack(side='left', padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.filter_entries())
        
        search_entry = tk.Entry(left_toolbar, textvariable=self.search_var, width=20,
                               bg='#0f3460', fg='white', insertbackground='white',
                               font=('Segoe UI', 10), relief='flat', highlightthickness=1,
                               highlightcolor='#e94560', highlightbackground='#0f3460')
        search_entry.pack(side='left', padx=5)
        
        tk.Label(left_toolbar, text="Category:", bg='#1a1a2e', fg='#a8d8ea',
                font=('Segoe UI', 10)).pack(side='left', padx=(10, 5))
        
        self.category_var = tk.StringVar(value="All")
        self.category_combo = ttk.Combobox(left_toolbar, textvariable=self.category_var,
                                          width=15, font=('Segoe UI', 10), 
                                          state='readonly', style="Custom.TCombobox")
        self.category_combo.pack(side='left', padx=5)
        self.category_combo.bind('<<ComboboxSelected>>', lambda e: self.filter_entries())
        
        right_toolbar = tk.Frame(toolbar, bg='#1a1a2e')
        right_toolbar.pack(side='right', padx=10)
        
        btn_add = tk.Button(right_toolbar, text="Add New", command=self.add_entry,
                           bg='#10b981', fg='white', font=('Segoe UI', 10, 'bold'),
                           relief='flat', cursor='hand2', padx=15, pady=5)
        btn_add.pack(side='left', padx=3)
        
        btn_edit = tk.Button(right_toolbar, text="Edit", command=self.edit_entry,
                            bg='#3b82f6', fg='white', font=('Segoe UI', 10, 'bold'),
                            relief='flat', cursor='hand2', padx=15, pady=5)
        btn_edit.pack(side='left', padx=3)
        
        btn_delete = tk.Button(right_toolbar, text="Delete", command=self.delete_entry,
                              bg='#ef4444', fg='white', font=('Segoe UI', 10, 'bold'),
                              relief='flat', cursor='hand2', padx=15, pady=5)
        btn_delete.pack(side='left', padx=3)
        
        btn_reset = tk.Button(right_toolbar, text="Reset All", command=self.reset_all_data,
                             bg='#f59e0b', fg='white', font=('Segoe UI', 10, 'bold'),
                             relief='flat', cursor='hand2', padx=15, pady=5)
        btn_reset.pack(side='left', padx=3)
        
        content_frame = tk.Frame(main_container, bg='#0f0f1a')
        content_frame.pack(fill='both', expand=True)
        
        list_panel = tk.Frame(content_frame, bg='#1a1a2e')
        list_panel.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        columns = ('Platform', 'Username', 'Category', 'Date')
        self.tree = ttk.Treeview(list_panel, columns=columns, show='headings',
                                style="Custom.Treeview", height=20)
        
        scrollbar = ttk.Scrollbar(list_panel, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.heading('Platform', text='Platform')
        self.tree.heading('Username', text='Username')
        self.tree.heading('Category', text='Category')
        self.tree.heading('Date', text='Created')
        
        self.tree.column('Platform', width=180)
        self.tree.column('Username', width=160)
        self.tree.column('Category', width=120)
        self.tree.column('Date', width=120)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        self.tree.bind('<Double-1>', lambda e: self.show_password())
        
        detail_panel = tk.Frame(content_frame, bg='#1a1a2e', width=320)
        detail_panel.pack(side='right', fill='y', padx=(5, 0))
        detail_panel.pack_propagate(False)
        
        tk.Label(detail_panel, text="Details", 
                font=('Segoe UI', 14, 'bold'), bg='#1a1a2e', fg='#a8d8ea').pack(pady=(15, 10))
        
        self.detail_frame = tk.Frame(detail_panel, bg='#0f3460')
        self.detail_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        self.detail_text = tk.Text(self.detail_frame, bg='#0f3460', fg='#ffffff',
                                  font=('Segoe UI', 10), wrap='word',
                                  relief='flat', padx=12, pady=12,
                                  highlightthickness=0)
        self.detail_text.pack(fill='both', expand=True)
        
        btn_frame = tk.Frame(detail_panel, bg='#1a1a2e')
        btn_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        btn_show = tk.Button(btn_frame, text="Show & Copy", 
                            command=self.show_password,
                            bg='#8b5cf6', fg='white', font=('Segoe UI', 10, 'bold'),
                            relief='flat', cursor='hand2', pady=8)
        btn_show.pack(fill='x', pady=3)
        
        btn_edit_detay = tk.Button(btn_frame, text="Edit",
                                  command=self.edit_entry,
                                  bg='#3b82f6', fg='white', font=('Segoe UI', 10, 'bold'),
                                  relief='flat', cursor='hand2', pady=8)
        btn_edit_detay.pack(fill='x', pady=3)
        
        status_frame = tk.Frame(main_container, bg='#0f0f1a', height=30)
        status_frame.pack(fill='x', pady=(10, 0))
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, text="Ready", 
                                    bg='#0f0f1a', fg='#6b7280',
                                    font=('Segoe UI', 9))
        self.status_label.pack(side='left')
        
        self.count_label = tk.Label(status_frame, text="", 
                                   bg='#0f0f1a', fg='#6b7280',
                                   font=('Segoe UI', 9))
        self.count_label.pack(side='right')
        
        self.update_categories()
        self.update_count()
    
    def update_count(self):
        count = len(self.db.get_all())
        self.count_label.config(text=f"Total: {count} passwords")
    
    def load_entries(self, entries=None):
        self.tree.delete(*self.tree.get_children())
        
        if entries is None:
            entries = self.db.get_all()
        
        for entry in entries:
            created = entry.created_at[:10] if entry.created_at else ""
            self.tree.insert('', 'end', values=(
                entry.platform,
                entry.username,
                entry.category,
                created
            ), tags=(entry.id,))
    
    def filter_entries(self):
        search = self.search_var.get().strip()
        category = self.category_var.get()
        
        entries = self.db.search(search)
        if category != "All":
            entries = [e for e in entries if e.category == category]
        
        self.load_entries(entries)
        self.update_count()
    
    def update_categories(self):
        categories = self.db.get_categories()
        self.category_combo['values'] = ['All'] + categories
        self.category_var.set('All')
    
    def on_select(self, event):
        selection = self.tree.selection()
        if not selection:
            self.detail_text.delete('1.0', tk.END)
            return
        
        item = self.tree.item(selection[0])
        entry_id = item['tags'][0]
        
        entries = [e for e in self.db.get_all() if e.id == entry_id]
        if entries:
            entry = entries[0]
            self.display_details(entry)
    
    def display_details(self, entry, show_password=False):
        self.detail_text.delete('1.0', tk.END)
        
        detail = f"""
PLATFORM
{entry.platform}

USERNAME
{entry.username}

{'PASSWORD' if show_password else 'PASSWORD'}
{self.crypto.decrypt(entry.encrypted_password) if show_password else '********'}

CATEGORY
{entry.category}

NOTES
{entry.notes or '-'}

CREATED
{entry.created_at[:16]}

UPDATED
{entry.updated_at[:16] if entry.updated_at else '-'}
"""
        self.detail_text.insert('1.0', detail.strip())
    
    def show_password(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a password!")
            return
        
        item = self.tree.item(selection[0])
        entry_id = item['tags'][0]
        
        entries = [e for e in self.db.get_all() if e.id == entry_id]
        if entries:
            entry = entries[0]
            password = self.crypto.decrypt(entry.encrypted_password)
            if password:
                pyperclip.copy(password)
                self.display_details(entry, show_password=True)
                self.status_label.config(text="Password copied to clipboard!")
                messagebox.showinfo("Success", "Password copied to clipboard!")
            else:
                messagebox.showerror("Error", "Failed to decrypt password!")
    
    def add_entry(self):
        dialog = AddEditDialog(self.window, self.db, self.crypto)
        self.window.wait_window(dialog.dialog)
        if dialog.result:
            self.load_entries()
            self.update_categories()
            self.update_count()
            self.status_label.config(text="New password added")
    
    def edit_entry(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a password to edit!")
            return
        
        item = self.tree.item(selection[0])
        entry_id = item['tags'][0]
        
        entries = [e for e in self.db.get_all() if e.id == entry_id]
        if entries:
            dialog = AddEditDialog(self.window, self.db, self.crypto, entries[0])
            self.window.wait_window(dialog.dialog)
            if dialog.result:
                self.load_entries()
                self.update_categories()
                self.update_count()
                self.status_label.config(text="Password updated")
                self.on_select(None)
    
    def delete_entry(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a password to delete!")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this password?"):
            item = self.tree.item(selection[0])
            entry_id = item['tags'][0]
            self.db.delete(entry_id)
            self.load_entries()
            self.detail_text.delete('1.0', tk.END)
            self.update_count()
            self.status_label.config(text="Password deleted")
    
    def reset_all_data(self):
        if messagebox.askyesno("Reset All Data", 
                               "WARNING: This will delete ALL your passwords!\n\n"
                               "Are you sure you want to continue?"):
            if messagebox.askyesno("Final Confirmation", 
                                   "This action cannot be undone!\n\n"
                                   "All your saved passwords will be permanently lost.\n"
                                   "Do you really want to reset all data?"):
                try:
                    self.db.reset_all_data()
                    self.load_entries()
                    self.update_categories()
                    self.update_count()
                    self.detail_text.delete('1.0', tk.END)
                    self.status_label.config(text="All data has been reset")
                    messagebox.showinfo("Success", "All data has been reset successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to reset data: {str(e)}")
    
    def on_close(self):
        if messagebox.askyesno("Exit", "Are you sure you want to exit the program?"):
            self.window.quit()
            self.window.destroy()
    
    def run(self):
        self.window.mainloop()