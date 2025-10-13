import os, sys, sqlite3

class ChanDataBase:
    def __init__(self):
        # تحديد مسار قاعدة البيانات سواء exe أو script
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))

        db_path = os.path.join(base_path, "database", "chan.db")

        # تأكد إن المجلد موجود
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # افتح الاتصال بقاعدة البيانات
        self.con = sqlite3.connect(db_path)
        print("📂 Database path:", db_path)
        cur = self.con.cursor()

if __name__ == "__main__":
    ChanDataBase()  