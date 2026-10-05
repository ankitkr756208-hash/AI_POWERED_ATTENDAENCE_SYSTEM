from src.database.config import supabase
import bcrypt
from httpx import RequestError


class DatabaseConnectionError(RuntimeError):
    pass



def hash_pass(pwd):
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()

def check_pass(pwd, hashed):
    return bcrypt.checkpw(pwd.encode(), hashed.encode())


def check_teacher_exists(username):
    # Check for unique username, returns false when username is already taken
    try:
        response = supabase.table("teachers").select("username").eq("username", username).execute()
    except RequestError as exc:
        raise DatabaseConnectionError("Unable to reach Supabase right now.") from exc
    return len(response.data) > 0 



def create_teacher(username, password, name):

    data = { "username" : username, "password": hash_pass(password), "name": name}
    try:
        response = supabase.table("teachers").insert(data).execute()
    except RequestError as exc:
        raise DatabaseConnectionError("Unable to reach Supabase right now.") from exc
    return response.data


def teacher_login(username, password):
    try:
        response = supabase.table("teachers").select("*").eq("username", username).execute()
    except RequestError as exc:
        raise DatabaseConnectionError("Unable to reach Supabase right now.") from exc
    if response.data:
        teacher = response.data[0]
        if check_pass(password, teacher['password']):
            return teacher
    return None


def get_all_students():
    try:
        response = supabase.table('students').select("*").execute()
    except RequestError as exc:
        raise DatabaseConnectionError("Unable to reach Supabase right now.") from exc
    return response.data

def create_student(new_name, face_embedding=None, voice_embedding=None):
    data_full = {'name': new_name, 'face_embedding': face_embedding, 'face_embeddings_list': [face_embedding] if face_embedding else [], "voice_embedding": voice_embedding}
    try:
        response = supabase.table('students').insert(data_full).execute()
        return response.data
    except Exception:
        # Fallback for Supabase remote schemas where 'face_embeddings_list' column is missing
        data_compat = {'name': new_name, 'face_embedding': face_embedding, "voice_embedding": voice_embedding}
        try:
            response = supabase.table('students').insert(data_compat).execute()
            return response.data
        except Exception as exc:
            raise DatabaseConnectionError("Unable to reach database right now.") from exc

def add_student_face_embedding(student_id, new_face_embedding):
    try:
        res = supabase.table('students').select('*').eq('student_id', student_id).execute()
        if not res.data:
            return None
        student = res.data[0]
        emb_list = student.get('face_embeddings_list') or []
        if not isinstance(emb_list, list):
            emb_list = []
        if student.get('face_embedding') and len(student['face_embedding']) == 128:
            if student['face_embedding'] not in emb_list:
                emb_list.append(student['face_embedding'])
        
        if len(emb_list) >= 5:
            emb_list.pop(0)
        emb_list.append(new_face_embedding)
        
        response = supabase.table('students').update({'face_embeddings_list': emb_list}).eq('student_id', student_id).execute()
        return response.data
    except Exception as exc:
        print("Skipping multi-embedding update for remote schema:", exc)
        return None


def create_subject(subject_code, name, section, teacher_id):
    data = {"subject_code": subject_code, "name": name, "section": section, "teacher_id": teacher_id}
    try:
        response = supabase.table("subjects").insert(data).execute()
    except RequestError as exc:
        raise DatabaseConnectionError("Unable to reach Supabase right now.") from exc
    return response.data

def delete_subject(subject_id):
    try:
        supabase.table('attendance_logs').delete().eq('subject_id', subject_id).execute()
        supabase.table('subject_students').delete().eq('subject_id', subject_id).execute()
        response = supabase.table('subjects').delete().eq('subject_id', subject_id).execute()
        return response.data
    except Exception as exc:
        print("Error deleting subject:", exc)
        raise DatabaseConnectionError("Unable to delete subject right now.") from exc

def get_teacher_subjects(teacher_id):
    try:
        response = supabase.table('subjects').select("*, subject_students(count), attendance_logs(timestamp)").eq("teacher_id", teacher_id).execute()
    except RequestError as exc:
        raise DatabaseConnectionError("Unable to reach Supabase right now.") from exc
    subjects = response.data


    for sub in subjects:
        sub['total_students'] = sub.get("subject_students", [{}])[0].get('count', 0) if sub.get('subject_students') else 0
        attendance = sub.get('attendance_logs', [])
        unique_sessions = len(set(log['timestamp'] for log in attendance))
        sub['total_classes'] = unique_sessions


        sub.pop('subject_students', None)
        sub.pop('attendance_logs', None)

    return subjects


def  enroll_student_to_subject(student_id, subject_id):
    data = {'student_id': student_id, "subject_id": subject_id}
    try:
        response= supabase.table('subject_students').insert(data).execute()
    except RequestError as exc:
        raise DatabaseConnectionError("Unable to reach Supabase right now.") from exc
    return response.data


def  unenroll_student_to_subject(student_id, subject_id):
    try:
        response= supabase.table('subject_students').delete().eq('student_id', student_id).eq('subject_id', subject_id).execute()
    except RequestError as exc:
        raise DatabaseConnectionError("Unable to reach Supabase right now.") from exc
    return response.data



def get_student_subjects(student_id):
    try:
        response = supabase.table('subject_students').select('*, subjects(*)').eq('student_id', student_id).execute()
    except RequestError as exc:
        raise DatabaseConnectionError("Unable to reach Supabase right now.") from exc
    return response.data


def get_student_attendance(student_id):
    try:
        response = supabase.table('attendance_logs').select('*, subjects(*)').eq('student_id', student_id).execute()
    except RequestError as exc:
        raise DatabaseConnectionError("Unable to reach Supabase right now.") from exc
    return response.data


def create_attendance(logs):
    try:
        response = supabase.table('attendance_logs').insert(logs).execute()
    except RequestError as exc:
        raise DatabaseConnectionError("Unable to reach Supabase right now.") from exc
    return response.data

def get_attendance_for_teacher(teacher_id):
    try:
        response = supabase.table('attendance_logs').select("*, subjects!inner(*)").eq('subjects.teacher_id', teacher_id).execute()
    except RequestError as exc:
        raise DatabaseConnectionError("Unable to reach Supabase right now.") from exc
    return response.data