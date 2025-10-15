import os
import sys
import sqlite3


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
        self.cur = self.con.cursor()

    def create_table(self):
        self.cur.execute(
            f"""Create Table numbers(number_id INT, number INT, last_user DATE)""")
        self.con.commit()

    def rename_already_table(self, name_table, new_name_table):
        self.cur.execute(
            f"""RENAME TABLE {name_table} TO {new_name_table}""")
        self.con.commit()

    def add_filed_to_table(self, table_name,  name_filed, type_filed):
        self.cur.execute(
            f"""ALTER TABLE {table_name} ADD {name_filed} {type_filed}""")
        self.con.commit()

    def get_all_numbers(self):
        data = self.cur.execute(
            """SELECT * FROM numbers""").fetchall()
        self.con.commit()

        return data

    def del_column(self, name_table, name_column):
        query = f"""ALTER TABLE {name_table} 
        DROP COLUMN {name_column}    
        """
        self.cur.execute(query)
        self.con.commit()

    def add_number(self, number, last_date_used="#"):

        last_id_row = self.cur.execute(
            "SELECT MAX(number_id) FROM numbers").fetchone()
        last_id = last_id_row[0] if last_id_row and last_id_row[0] is not None else 0
        new_id = last_id + 1

        query = "INSERT INTO numbers (number_id, number, last_user) VALUES (?, ?, ?)"
        self.cur.execute(query, (new_id, str(number), str(last_date_used)))
        self.con.commit()

        return [new_id, str(number), str(last_date_used)]

    def search_numbers(self, keyword: str):
        """
        تبحث عن الأرقام اللي تحتوي على الكلمة المدخلة في عمود number.
        """
        keyword = f"%{keyword.strip()}%"
        query = "SELECT * FROM numbers WHERE CAST(number AS TEXT) LIKE ?"
        result = self.cur.execute(query, (keyword,)).fetchall()
        return result

    def clear_all_numbers(self):
        """تحذف كل البيانات من جدول numbers بدون حذف الجدول نفسه"""
        self.cur.execute("DELETE FROM numbers")
        self.con.commit()
        print("🗑️ تم مسح جميع البيانات من الجدول بنجاح.")

    def delete_number(self, number):
        """حذف رقم محدد من قاعدة البيانات"""
        self.cur.execute("DELETE FROM numbers WHERE number = ?", (number,))
        self.con.commit()


if __name__ == "__main__":
    database = ChanDataBase()
    print(database.clear_all_data())
