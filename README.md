# 🎓 AI-Powered Attendance System (SnapClass)

An AI-powered attendance management system designed to help teachers
manage classroom attendance using face recognition, with student
registration, subject/section management, attendance analytics, and
report export.

> **Project status:** Development project. Features and deployment
> behavior may depend on the configured database, installed
> dependencies, and current code version. Face recognition is
> probabilistic, so attendance records should be reviewed when
> confidence is low.

## 🌐 Live Demo

Try the deployed application here:

**[AI-Powered Attendance System — Live App](https://smart-attendance-system-7562.streamlit.app/)**

## ✨ Features

### 👤 Student Portal

-   Student account/profile registration.
-   Upload a profile photo or capture one using a camera where
    supported.
-   Save student face data for attendance recognition.
-   Enroll in subjects and view enrolled-subject information.
-   Add additional face samples to help recognition across different
    angles and lighting conditions.

### 🧑‍🏫 Teacher Portal

-   Create and manage subjects.
-   Associate subjects with sections and subject codes.
-   Filter subjects by section.
-   Delete subjects through the teacher interface.
-   Take attendance using an uploaded classroom image and face
    recognition.
-   View attendance records and attendance summaries.

### 🤖 AI Face Recognition

-   Extract and compare face embeddings to identify registered students.
-   Support multiple face samples per student, where enabled.
-   Validate embedding dimensions to avoid invalid-vector comparison
    errors.
-   Handle cases where a model cannot safely make a prediction.

### 📊 Attendance Analytics & Reports

-   View attendance summaries and subject-level trends.
-   Highlight students whose attendance falls below the configured 75%
    threshold.
-   Export attendance records as a CSV report.

### 🗄️ Database

-   Supabase/PostgreSQL support in the configured deployment.
-   Local SQLite fallback is described in the project development notes
    for environments where the remote database is unreachable.
-   Database behavior depends on the active configuration and schema.

### 🌐 Web Interface

-   Streamlit attendance application.
-   Flask-based landing page/frontend.
-   Frontend calls to action can link users to the main attendance
    application.

## 🧰 Technology Stack

The repository and project notes indicate the following technologies:

-   **Language:** Python
-   **Application UI:** Streamlit
-   **Web frontend/landing page:** Flask and HTML/CSS
-   **Database:** Supabase/PostgreSQL and SQLite fallback
-   **AI/Computer Vision:** Face-recognition pipeline and face
    embeddings
-   **Data/ML utilities:** NumPy and scikit-learn (depending on the
    installed project requirements)

Check `requirements.txt` and the source code for the exact package
versions used by your current checkout.

## 📁 Repository Structure

``` text
AI_POWERED_ATTENDANCE_SYSTEM/
├── snapclass-frontend/     # Frontend/landing-page assets
├── src/
│   ├── components/         # Reusable UI components
│   ├── database/           # Database configuration and data access
│   ├── pipelines/          # Face-recognition and AI pipelines
│   └── screens/            # Teacher and student screens
├── app.py                  # Main Streamlit application entry point
├── requirements.txt        # Python dependencies
├── .gitignore
└── README.md
```

*The exact folders and files may change as the project evolves.*

## ⚙️ Getting Started

### 1. Clone the repository

``` bash
git clone https://github.com/ankitkr756208-hash/AI_POWERED_ATTENDANCE_SYSTEM.git
cd AI_POWERED_ATTENDANCE_SYSTEM
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**

``` powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**

``` bat
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**

``` bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

``` bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Some audio/face-recognition dependencies can require additional system
packages or compatible Python versions. If installation fails, check the
package's installation instructions and your Python version.

### 4. Configure environment variables

If your setup uses Supabase, add the required credentials to your local
environment or the deployment platform's secrets/settings. Use the
variable names expected by the code in `src/database/config.py`.

**Security:** Never commit database passwords, API keys, service-role
keys, or other secrets to GitHub. Keep `.env` files out of version
control.

If the project is configured for local SQLite fallback, make sure the
application has permission to create/write its database file.

### 5. Run the main application

``` bash
streamlit run app.py
```

Streamlit normally prints a local URL such as:

``` text
http://localhost:8501
```

If the Flask landing page is part of your setup, inspect its entry point
and run command in the repository before starting it. The development
notes previously used port `5002` for the Flask page; that port is not
guaranteed in every version.

## 🧑‍💻 Typical Workflow

1.  Register a student account and provide a clear, front-facing profile
    photo.
2.  Sign in to the teacher portal.
3.  Create subjects with a subject name, code, and section.
4.  Enroll students in the relevant subjects.
5.  Open the attendance workflow and provide a classroom image.
6.  Review the detected identities and attendance results before relying
    on the records.
7.  Open attendance records to review summaries, identify students below
    the attendance threshold, and export a CSV report.

The exact labels and sequence may differ depending on the version
deployed.

## ☁️ Deployment Notes

-   Set required secrets in the hosting provider's environment/secrets
    configuration.
-   Confirm the database schema contains all columns expected by the
    deployed code.
-   Install all dependencies from `requirements.txt` using a compatible
    Python runtime.
-   Test registration, login, subject management, attendance marking,
    and CSV export after deployment.
-   If Streamlit reports duplicate element IDs, ensure repeated widgets
    use unique `key` values.
-   If a database API reports a missing column, apply the required
    schema migration rather than relying only on a code-side fallback.
-   Do not use `localhost` as a public deployment URL; it points to the
    current machine only.

## 🔐 Privacy, Security & Responsible Use

Face embeddings and attendance records are sensitive personal data.
Before using this system in a real institution:

-   Obtain appropriate consent and follow applicable privacy and
    institutional policies.
-   Restrict access by role and protect database credentials.
-   Use HTTPS for deployed applications.
-   Define retention and deletion policies for photos, embeddings, and
    attendance records.
-   Provide a manual attendance correction/review process for
    recognition errors.
-   Do not treat face recognition as perfectly accurate or as the sole
    basis for disciplinary decisions.
-   Add and test liveness/anti-spoofing checks before claiming
    protection against photo or video spoofing.

## 🛣️ Future Improvements

-   Stronger deep-learning face recognition models such as
    ArcFace/FaceNet.
-   Liveness detection and anti-spoofing.
-   Role-based access control for administrators, teachers, and
    students.
-   Institution, department, course, and section hierarchy.
-   QR-based subject enrollment with expiring, authenticated codes.
-   More detailed weekly/monthly analytics and downloadable Excel
    reports.
-   Progressive Web App (PWA) support for mobile devices.
-   Auditing, automated tests, backups, and database migrations.

## 🐛 Troubleshooting

-   **Dependency installation fails:** Check Python compatibility and
    the package's platform-specific installation instructions.
-   **Database connection fails:** Verify the Supabase URL, credentials,
    network access, and database status; confirm the configured SQLite
    fallback if available.
-   **Face matching fails:** Use clear, well-lit photos with one visible
    face and ensure the student has valid face samples stored.
-   **Embedding shape error:** Check that stored embeddings have the
    expected dimensions and remove or repair invalid test records.
-   **Streamlit duplicate widget error:** Add a stable, unique `key` to
    each repeated widget.
-   **Cloud deployment differs from local:** Confirm that the latest
    code, requirements, secrets, and database schema have all been
    deployed.

## 🤝 Contributing

Contributions, bug reports, and feature suggestions are welcome. For
changes:

1.  Create a feature branch.
2.  Keep credentials and private data out of commits.
3.  Test the affected student, teacher, and database workflows.
4.  Open a pull request with a clear description of the change.

## 👨‍💻 Author

**Ankit Kumar**\
B.Tech, Computer Science & Engineering\
ABES Engineering College, Ghaziabad

## 📄 License

No license is specified here. Add a `LICENSE` file before permitting
others to reuse, modify, or distribute this project.
