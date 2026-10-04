import streamlit as st

from src.ui.base_layout import style_background_dashboard, style_base_layout

from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from PIL import Image
import numpy as np
from src.pipelines.face_pipeline import predict_attendance, get_face_embeddings, train_classifier
from src.pipelines.voice_pipeline import get_voice_embedding
from src.database.db import get_all_students, create_student, get_student_subjects, get_student_attendance, unenroll_student_to_subject, add_student_face_embedding
import time

from src.components.dialog_enroll import enroll_dialog
from src.components.subject_card import subject_card

def student_dashboard():
    student_data = st.session_state.student_data
    student_id = student_data['student_id']
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"""Welcome, {student_data['name']} """)
        if st.button("Logout", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['is_logged_in'] = False
            del st.session_state.student_data 
            st.rerun()


    st.space()

    c1, c2 =st.columns(2)
    with c1:
        st.header('Your Enrolled Subjects')
    with c2:
        if st.button('Enroll in Subject', type='primary', width='stretch'):
            enroll_dialog()


    st.divider()


    with st.spinner('Loading your enrolled subjects..'):
        subjects = get_student_subjects(student_id)
        logs = get_student_attendance(student_id)

    stats_map = {}

    for log in logs:
        sid = log['subject_id']

        if sid not in stats_map:
            stats_map[sid] = {"total":0, "attended": 0}

        stats_map[sid]['total'] +=1

        if log.get('is_present'):
            stats_map[sid]['attended'] += 1


    cols = st.columns(2)
    for i, sub_node in enumerate(subjects):
        sub = sub_node['subjects']
        sid = sub['subject_id']
        stats = stats_map.get(sid, {"total": 0, "attended": 0})

        def make_unenroll_button(s_id, s_name):
            def unenroll_button():
                if st.button("Unenroll from this course", key=f"unenroll_{s_id}", type='tertiary', width='stretch', icon=':material/delete_forever:'):
                    unenroll_student_to_subject(student_id, s_id)
                    st.toast(f"Unenrolled from {s_name} successfully!")
                    st.rerun()
            return unenroll_button

        with cols[i % 2]:
            subject_card(
                name = sub['name'],
                code = sub['subject_code'],
                section = sub['section'],
                stats = [
                    ('📅', 'Total', stats['total']),
                    ('✅', 'Attended', stats['attended']),
                ],
                footer_callback=make_unenroll_button(sid, sub['name'])
            )

    st.divider()
    with st.expander("📸 Enhance AI Recognition (Add Multi-Angle Face Samples)"):
        st.write("Upload extra photos with different lighting, glasses, or angles to make your AI face recognition 100% accurate!")
        extra_photo = st.file_uploader("Upload additional face photo", type=['jpg', 'jpeg', 'png'], key="extra_student_angle")
        if extra_photo and st.button("Save New Face Angle Sample", type="primary"):
            with st.spinner("Processing new facial features..."):
                img = np.array(Image.open(extra_photo).convert('RGB'))
                encs = get_face_embeddings(img)
                if encs:
                    add_student_face_embedding(student_id, encs[0].tolist())
                    train_classifier()
                    st.toast("✅ New face angle sample saved! AI recognition accuracy improved.")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("No clear face detected in the photo. Please use a clearer image.")

    footer_dashboard()


def student_screen():


    style_background_dashboard()
    style_base_layout()


    if "student_data" in st.session_state:
        student_dashboard()
        return
    
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()

    st.header('Login / Register using FaceID', text_alignment='center')
    st.space()

    if 'student_photo_input_mode' not in st.session_state:
        st.session_state.student_photo_input_mode = 'camera'

    t1, t2 = st.columns(2)
    with t1:
        type_cam = "primary" if st.session_state.student_photo_input_mode == 'camera' else "tertiary"
        if st.button("Use Camera", type=type_cam, width='stretch', icon=":material/photo_camera:"):
            st.session_state.student_photo_input_mode = 'camera'
            st.rerun()
    with t2:
        type_up = "primary" if st.session_state.student_photo_input_mode == 'upload' else "tertiary"
        if st.button("Upload Photo", type=type_up, width='stretch', icon=":material/upload_file:"):
            st.session_state.student_photo_input_mode = 'upload'
            st.rerun()

    st.space()

    show_registration = False
    photo_source = None

    if st.session_state.student_photo_input_mode == 'camera':
        photo_source = st.camera_input("Position your face in the center")
    else:
        photo_source = st.file_uploader("Upload your face photo (JPG/PNG)", type=['jpg', 'jpeg', 'png'], key="student_portal_upload")

    if photo_source:
        img = np.array(Image.open(photo_source).convert('RGB'))

        with st.spinner('AI is scanning face..'):
            detected, all_ids, num_faces = predict_attendance(img)

            if num_faces == 0:
                st.warning('Face not detected in image! Please use a clear facial photo.')
            elif num_faces > 1:
                st.warning('Multiple faces detected! Please use an image with a single person.')
            else:
                if detected:
                    student_id = list(detected.keys())[0]
                    all_students = get_all_students()
                    student = next((s for s in all_students if s['student_id'] == student_id), None)

                    if student:
                        st.session_state.is_logged_in = True
                        st.session_state.user_role = 'student'
                        st.session_state.student_data = student
                        st.toast(f"Welcome Back {student['name']}")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.info('Face not recognized! Create your new student profile below:')
                    show_registration = True

    if show_registration:
        with st.container(border=True):
            st.header('Register new Profile')
            new_name = st.text_input("Enter your name", placeholder='E.g. Hamza Rizvi')

            st.subheader('Optional : Voice Enrollment')
            st.info("Enroll your voice for audio attendance")

            audio_data = None
            try:
                audio_data = st.audio_input('Record a short phrase like "I am present, My name is Akash."')
            except Exception:
                st.error('Audio recording not supported on this device.')

            if st.button('Create Account & Save Profile', type='primary', width='stretch'):
                if new_name:
                    with st.spinner('Creating student profile in database..'):
                        img = np.array(Image.open(photo_source).convert('RGB'))
                        encodings = get_face_embeddings(img)
                        if encodings:
                            face_emb = encodings[0].tolist()
                            voice_emb = None
                            if audio_data:
                                voice_emb = get_voice_embedding(audio_data.read())

                            response_data = create_student(new_name, face_embedding=face_emb, voice_embedding=voice_emb)

                            if response_data:
                                train_classifier()
                                st.session_state.is_logged_in = True
                                st.session_state.user_role = 'student'
                                st.session_state.student_data = response_data[0]
                                st.toast(f'Profile Created! Welcome {new_name}!')
                                time.sleep(1)
                                st.rerun()
                        else:
                            st.error('Could not extract facial features from the image. Please try another photo.')
                else:
                    st.warning('Please enter your full name!')


        
    footer_dashboard()