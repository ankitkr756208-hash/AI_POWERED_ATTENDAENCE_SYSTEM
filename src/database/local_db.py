import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "snapclass.db")

class Response:
    def __init__(self, data):
        self.data = data

class TableQuery:
    def __init__(self, table_name, db_path=DB_PATH):
        self.table_name = table_name
        self.db_path = db_path
        self.select_cols = "*"
        self.eq_conditions = []
        self.limit_val = None
        self.is_delete = False
        self.insert_data = None
        self.update_data = None

    def select(self, cols="*"):
        self.select_cols = cols
        return self

    def eq(self, col, val):
        self.eq_conditions.append((col, val))
        return self

    def limit(self, val):
        self.limit_val = val
        return self

    def delete(self):
        self.is_delete = True
        return self

    def insert(self, data):
        self.insert_data = data
        return self

    def update(self, data):
        self.update_data = data
        return self

    def execute(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            if self.update_data is not None:
                set_clauses = []
                vals = []
                for k, v in self.update_data.items():
                    set_clauses.append(f"{k} = ?")
                    if isinstance(v, (list, dict)):
                        v = json.dumps(v)
                    vals.append(v)
                where_clause = ""
                if self.eq_conditions:
                    where_clause = " WHERE " + " AND ".join([f"{col} = ?" for col, _ in self.eq_conditions])
                    vals.extend([val for _, val in self.eq_conditions])
                cursor.execute(f"UPDATE {self.table_name} SET {', '.join(set_clauses)}{where_clause}", vals)
                conn.commit()
                return Response([])
            if self.insert_data is not None:
                rows_to_insert = self.insert_data if isinstance(self.insert_data, list) else [self.insert_data]
                inserted_records = []
                for row in rows_to_insert:
                    keys = list(row.keys())
                    vals = []
                    for k in keys:
                        v = row[k]
                        if isinstance(v, (list, dict)):
                            v = json.dumps(v)
                        vals.append(v)
                    placeholders = ", ".join(["?"] * len(keys))
                    col_names = ", ".join(keys)
                    query = f"INSERT INTO {self.table_name} ({col_names}) VALUES ({placeholders})"
                    cursor.execute(query, vals)
                    row_id = cursor.lastrowid

                    pk_name = "teacher_id" if self.table_name == "teachers" else \
                              "student_id" if self.table_name == "students" else \
                              "subject_id" if self.table_name == "subjects" else "id"
                    cursor.execute(f"SELECT * FROM {self.table_name} WHERE {pk_name} = ?", (row_id,))
                    fetched = cursor.fetchone()
                    if fetched:
                        item = dict(fetched)
                        if self.table_name == "students":
                            if item.get("face_embedding") and isinstance(item["face_embedding"], str):
                                try: item["face_embedding"] = json.loads(item["face_embedding"])
                                except: pass
                            if item.get("voice_embedding") and isinstance(item["voice_embedding"], str):
                                try: item["voice_embedding"] = json.loads(item["voice_embedding"])
                                except: pass
                        inserted_records.append(item)
                conn.commit()
                return Response(inserted_records)

            if self.is_delete:
                where_clause = ""
                params = []
                if self.eq_conditions:
                    where_clause = " WHERE " + " AND ".join([f"{col} = ?" for col, _ in self.eq_conditions])
                    params = [val for _, val in self.eq_conditions]
                cursor.execute(f"DELETE FROM {self.table_name}{where_clause}", params)
                conn.commit()
                return Response([])

            # Select queries
            if "subject_students(count)" in self.select_cols:
                where_clause = ""
                params = []
                if self.eq_conditions:
                    where_clause = " WHERE " + " AND ".join([f"{col} = ?" for col, _ in self.eq_conditions])
                    params = [val for _, val in self.eq_conditions]
                cursor.execute(f"SELECT * FROM subjects{where_clause}", params)
                subjects = [dict(r) for r in cursor.fetchall()]
                for sub in subjects:
                    sid = sub["subject_id"]
                    cursor.execute("SELECT COUNT(*) as count FROM subject_students WHERE subject_id = ?", (sid,))
                    cnt = cursor.fetchone()["count"]
                    sub["subject_students"] = [{"count": cnt}]
                    cursor.execute("SELECT timestamp FROM attendance_logs WHERE subject_id = ?", (sid,))
                    logs = [dict(r) for r in cursor.fetchall()]
                    sub["attendance_logs"] = logs
                return Response(subjects)

            if self.table_name == "subject_students" and "subjects" in self.select_cols:
                where_clause = ""
                params = []
                if self.eq_conditions:
                    where_clause = " WHERE " + " AND ".join([f"subject_students.{col} = ?" for col, _ in self.eq_conditions])
                    params = [val for _, val in self.eq_conditions]
                cursor.execute(f"SELECT subject_students.*, subjects.subject_code as sub_code, subjects.name as sub_name, subjects.section as sub_section, subjects.teacher_id as sub_tid FROM subject_students JOIN subjects ON subject_students.subject_id = subjects.subject_id{where_clause}", params)
                rows = cursor.fetchall()
                res = []
                for r in rows:
                    item = dict(r)
                    sub_dict = {
                        "subject_id": item["subject_id"],
                        "subject_code": item.pop("sub_code"),
                        "name": item.pop("sub_name"),
                        "section": item.pop("sub_section"),
                        "teacher_id": item.pop("sub_tid")
                    }
                    item["subjects"] = sub_dict
                    res.append(item)
                return Response(res)

            if self.table_name == "subject_students" and "students" in self.select_cols:
                where_clause = ""
                params = []
                if self.eq_conditions:
                    where_clause = " WHERE " + " AND ".join([f"subject_students.{col} = ?" for col, _ in self.eq_conditions])
                    params = [val for _, val in self.eq_conditions]
                cursor.execute(f"SELECT subject_students.*, students.name as st_name, students.face_embedding as st_face, students.voice_embedding as st_voice FROM subject_students JOIN students ON subject_students.student_id = students.student_id{where_clause}", params)
                rows = cursor.fetchall()
                res = []
                for r in rows:
                    item = dict(r)
                    st_face = item.pop("st_face")
                    st_voice = item.pop("st_voice")
                    if st_face and isinstance(st_face, str):
                        try: st_face = json.loads(st_face)
                        except: pass
                    if st_voice and isinstance(st_voice, str):
                        try: st_voice = json.loads(st_voice)
                        except: pass
                    st_dict = {
                        "student_id": item["student_id"],
                        "name": item.pop("st_name"),
                        "face_embedding": st_face,
                        "voice_embedding": st_voice
                    }
                    item["students"] = st_dict
                    res.append(item)
                return Response(res)

            if self.table_name == "attendance_logs" and "subjects" in self.select_cols:
                where_clause = ""
                params = []
                if self.eq_conditions:
                    conds = []
                    for col, val in self.eq_conditions:
                        if col.startswith("subjects."):
                            conds.append(f"{col} = ?")
                        else:
                            conds.append(f"attendance_logs.{col} = ?")
                        params.append(val)
                    where_clause = " WHERE " + " AND ".join(conds)
                cursor.execute(f"SELECT attendance_logs.*, subjects.subject_code as sub_code, subjects.name as sub_name, subjects.section as sub_section, subjects.teacher_id as sub_tid FROM attendance_logs JOIN subjects ON attendance_logs.subject_id = subjects.subject_id{where_clause}", params)
                rows = cursor.fetchall()
                res = []
                for r in rows:
                    item = dict(r)
                    sub_dict = {
                        "subject_id": item["subject_id"],
                        "subject_code": item.pop("sub_code"),
                        "name": item.pop("sub_name"),
                        "section": item.pop("sub_section"),
                        "teacher_id": item.pop("sub_tid")
                    }
                    item["subjects"] = sub_dict
                    res.append(item)
                return Response(res)

            # Standard select query
            where_clause = ""
            params = []
            if self.eq_conditions:
                where_clause = " WHERE " + " AND ".join([f"{col} = ?" for col, _ in self.eq_conditions])
                params = [val for _, val in self.eq_conditions]

            limit_clause = f" LIMIT {self.limit_val}" if self.limit_val else ""
            cursor.execute(f"SELECT * FROM {self.table_name}{where_clause}{limit_clause}", params)
            rows = [dict(r) for r in cursor.fetchall()]
            if self.table_name == "students":
                for item in rows:
                    if item.get("face_embedding") and isinstance(item["face_embedding"], str):
                        try: item["face_embedding"] = json.loads(item["face_embedding"])
                        except: pass
                    if item.get("face_embeddings_list") and isinstance(item["face_embeddings_list"], str):
                        try: item["face_embeddings_list"] = json.loads(item["face_embeddings_list"])
                        except: pass
                    if item.get("voice_embedding") and isinstance(item["voice_embedding"], str):
                        try: item["voice_embedding"] = json.loads(item["voice_embedding"])
                        except: pass
            return Response(rows)
        finally:
            conn.close()

class LocalDBClient:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teachers (
                teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                face_embedding TEXT,
                face_embeddings_list TEXT,
                voice_embedding TEXT
            );
        """)
        try:
            cursor.execute("ALTER TABLE students ADD COLUMN face_embeddings_list TEXT;")
        except Exception:
            pass

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_code TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                section TEXT NOT NULL,
                teacher_id INTEGER NOT NULL
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subject_students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                is_present INTEGER NOT NULL
            );
        """)
        conn.commit()
        conn.close()

    def table(self, table_name):
        return TableQuery(table_name, self.db_path)
