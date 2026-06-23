import tkinter as tk
from tkinter import messagebox
import hashlib
import os
import json

class LoginDialog:
    def __init__(self):
        self.dialog = tk.Tk()
        self.dialog.title("Secure Password Manager - Login")
        self.dialog.geometry("420x520")
        self.dialog.resizable(False, False)
        self.dialog.configure(bg='#0f0f1a')
        self.dialog.eval('tk::PlaceWindow . center')
        
        self.password = None
        self.login_attempts = 0
        self.max_attempts = 3
        
        self.master_hash_file = os.path.join(os.environ['APPDATA'], 'PasswordManager', 'master.hash')
        self.is_first_run = not os.path.exists(self.master_hash_file)
        
        self.setup_ui()
        self.dialog.protocol("WM_DELETE_WINDOW", self.dialog.quit)
    
    def setup_ui(self):
        main_frame = tk.Frame(self.dialog, bg='#0f0f1a')
        main_frame.pack(fill='both', expand=True, padx=40, pady=30)
        
        title_frame = tk.Frame(main_frame, bg='#0f0f1a')
        title_frame.pack(pady=(0, 30))
        
        tk.Label(title_frame, text="Password Manager", 
                font=('Segoe UI', 24, 'bold'), bg='#0f0f1a', fg='#ffffff').pack()
        tk.Label(title_frame, text="Secure & Modern", 
                font=('Segoe UI', 11), bg='#0f0f1a', fg='#6b7280').pack()
        
        if self.is_first_run:
            info_text = "First run! Please set your master password."
            self.info_label = tk.Label(main_frame, text=info_text, 
                                      font=('Segoe UI', 9), bg='#0f0f1a', fg='#10b981')
            self.info_label.pack(pady=(0, 15))
        
        input_frame = tk.Frame(main_frame, bg='#1a1a2e', highlightthickness=2, 
                               highlightcolor='#e94560', highlightbackground='#1a1a2e')
        input_frame.pack(fill='x', pady=(0, 10))
        
        self.password_entry = tk.Entry(input_frame, width=30, show='*',
                                      bg='#1a1a2e', fg='#ffffff', 
                                      insertbackground='#e94560',
                                      font=('Segoe UI', 14), relief='flat',
                                      highlightthickness=0)
        self.password_entry.pack(padx=15, pady=12)
        self.password_entry.bind('<Return>', lambda e: self.login())
        self.password_entry.focus()
        
        show_frame = tk.Frame(main_frame, bg='#0f0f1a')
        show_frame.pack(fill='x', pady=(0, 20))
        
        self.show_var = tk.IntVar()
        show_check = tk.Checkbutton(show_frame, text="Show Password", 
                                   variable=self.show_var, command=self.toggle_password,
                                   bg='#0f0f1a', fg='#9ca3af', selectcolor='#0f0f1a',
                                   font=('Segoe UI', 9), relief='flat', padx=0)
        show_check.pack()
        
        self.btn_login = tk.Button(main_frame, text="Login", 
                                  command=self.login,
                                  bg='#e94560', fg='#ffffff', 
                                  font=('Segoe UI', 12, 'bold'),
                                  relief='flat', cursor='hand2',
                                  height=2, width=25)
        self.btn_login.pack(pady=(0, 10))
        
        self.error_label = tk.Label(main_frame, text="", 
                                   font=('Segoe UI', 9), bg='#0f0f1a', fg='#ef4444')
        self.error_label.pack(pady=(0, 5))
        
        footer_frame = tk.Frame(main_frame, bg='#0f0f1a')
        footer_frame.pack(side='bottom', fill='x', pady=(20, 0))
        
        if self.is_first_run:
            tk.Label(footer_frame, text="Don't forget this password! No recovery available.",
                    font=('Segoe UI', 8), bg='#0f0f1a', fg='#6b7280').pack()
        else:
            tk.Label(footer_frame, text="All your data is encrypted.",
                    font=('Segoe UI', 8), bg='#0f0f1a', fg='#6b7280').pack()
    
    def toggle_password(self):
        if self.show_var.get():
            self.password_entry.config(show='')
        else:
            self.password_entry.config(show='*')
    
    def login(self):
        password = self.password_entry.get()
        
        if not password:
            self.show_error("Please enter your password!")
            return
        
        if self.is_first_run:
            if len(password) < 4:
                self.show_error("Password must be at least 4 characters!")
                return
            
            os.makedirs(os.path.dirname(self.master_hash_file), exist_ok=True)
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            with open(self.master_hash_file, 'w') as f:
                json.dump({'hash': password_hash}, f)
            
            self.password = password
            self.dialog.quit()
            self.dialog.destroy()
            return
        
        try:
            with open(self.master_hash_file, 'r') as f:
                data = json.load(f)
                stored_hash = data.get('hash')
        except:
            self.show_error("System error! File cannot be read.")
            return
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if password_hash == stored_hash:
            self.password = password
            self.dialog.quit()
            self.dialog.destroy()
        else:
            self.login_attempts += 1
            remaining = self.max_attempts - self.login_attempts
            
            if remaining <= 0:
                messagebox.showerror("Error", "Too many failed attempts! Program will close.")
                self.dialog.quit()
                self.dialog.destroy()
                return
            
            self.show_error(f"Wrong password! {remaining} attempts remaining.")
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus()
    
    def show_error(self, message):
        self.error_label.config(text=message)
        self.dialog.after(3000, lambda: self.error_label.config(text=""))
    
    def run(self):
        self.dialog.mainloop()
        return self.password