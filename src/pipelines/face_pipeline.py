

import dlib
import numpy as np
import face_recognition_models
from sklearn.svm import SVC
import streamlit as st

from src.database.db import get_all_students


@st.cache_resource
def load_dlib_models():
    detector = dlib.get_frontal_face_detector() 


    sp = dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()
    )

    facerec = dlib.face_recognition_model_v1(
        face_recognition_models.face_recognition_model_location()
    )

    return detector, sp, facerec

def get_face_embeddings(image_np):
    detector, sp, facerec = load_dlib_models()
    faces = detector(image_np, 1)

    encodings= []

    for face in faces:
        shape = sp(image_np, face)
        face_descriptor = facerec.compute_face_descriptor(image_np, shape, 1) #128 embedding

        encodings.append(np.array(face_descriptor))
    return encodings

@st.cache_resource
def get_trained_model():
    X = []
    y = []


    student_db = get_all_students()

    if not student_db:
        return None
    
    for student in student_db:
        student_id = student.get('student_id')
        single_emb = student.get('face_embedding')
        emb_list = student.get('face_embeddings_list') or []

        all_vecs = []
        if single_emb and len(single_emb) == 128:
            all_vecs.append(single_emb)
        if isinstance(emb_list, list):
            for emb in emb_list:
                if emb and len(emb) == 128:
                    all_vecs.append(emb)

        for vec in all_vecs:
            X.append(np.array(vec, dtype=np.float64))
            y.append(student_id)

    if len(X) == 0:
        return None
    
    clf = SVC(kernel='linear', probability=True, class_weight='balanced')

    try:
        clf.fit(X, y)
    except ValueError:
        pass

    return {'clf': clf, 'X':X, "y":y}


def train_classifier():
    st.cache_resource.clear()
    model_data = get_trained_model()
    return bool(model_data)

def predict_attendance(class_image_np):
    encodings = get_face_embeddings(class_image_np)

    detected_student = {}

    model_data = get_trained_model()

    if not model_data:
        return detected_student, [], len(encodings)
    
    clf = model_data['clf']
    X_train = model_data['X']
    y_train = model_data['y']

    all_students = sorted(list(set(y_train)))

    for encoding in encodings:
        predicted_id = None
        if len(all_students) >= 2 and hasattr(clf, 'classes_'):
            try:
                predicted_id = int(clf.predict([encoding])[0])
            except Exception:
                predicted_id = int(all_students[0])
        elif len(all_students) > 0:
            predicted_id = int(all_students[0])

        if predicted_id is not None and predicted_id in y_train:
            indices = [i for i, sid in enumerate(y_train) if sid == predicted_id]
            min_dist = float('inf')
            for idx in indices:
                st_emb = X_train[idx]
                if st_emb.shape == encoding.shape:
                    dist = np.linalg.norm(st_emb - encoding)
                    if dist < min_dist:
                        min_dist = dist

            resemblance_threshold = 0.6
            if min_dist <= resemblance_threshold:
                detected_student[predicted_id] = True
    return detected_student, all_students, len(encodings)