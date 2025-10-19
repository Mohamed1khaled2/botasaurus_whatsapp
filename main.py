import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from gui.main_window import App

# initialization

if __name__ == "__main__":
    app = App() 
    app.mainloop()  
    
    
"""
    https://chatgpt.com/c/68f40e18-23ac-832d-bb31-adab3f6ed6b8
    
    # * run  python -m nuitka main.py --standalone --enable-plugin=tk-inter --include-package=customtkinter  --include-data-file=rocket.ico=rocket.ico --include-data-file=locations.json=locations.json --windows-icon-from-ico="rocket.ico" --output-filename="Rocket Sender.exe" --windows-console-mode=force --mingw64 
"""






