import sys
import os
from ui.login_dialog import LoginDialog
from ui.main_window import MainWindow
from database import Database

def main():
    login = LoginDialog()
    master_password = login.run()
    
    if not master_password:
        sys.exit()
    
    db = Database(master_password)
    app = MainWindow(master_password, db)
    app.run()

if __name__ == "__main__":
    main()