import multiprocessing
from gui.main_window import App

if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = App()
    app.mainloop()