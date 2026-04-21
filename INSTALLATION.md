# Installation Guide

## Prerequisites

- Python 3.10+
- pip

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/DigiClassroom.git
cd DigiClassroom
```

### 2. Set Up Virtual Environment

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize Database

```bash
cd digiclassrooms
python manage.py migrate
```

### 5. Create Admin User (Optional)

To access the Django admin interface:
```bash
python manage.py createsuperuser
```

### 6. Generate Demo Data (Recommended)

Populate your database with test users, classrooms, lectures, and assignments:
```bash
python manage.py create_dummy_data
```

This will create:
- **Teachers**: teacher1, teacher2
- **Students**: student1, student2, student3
- **Classrooms**: Multiple (CS101, Mathematics, Physics, Data Structures, Web Development)
- **Content**: Sample Lectures, Notices, Assignments, and Submissions for each classroom

Demo Credentials:
- Teacher: `teacher1` (password: `password123`)
- Student: `student1` (password: `password123`)

The demo data includes unique join keys for each classroom that students can use to enroll.

### 7. Generate Join Keys for Existing Classrooms (If Needed)

If you have existing classrooms without join keys, generate them:

```bash
python manage.py generate_join_keys
```

To regenerate all classroom keys:
```bash
python manage.py generate_join_keys --all
```

### 8. Run Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

### 9. Verify New Feature Migrations (Recommended)

Recent updates include Q&A grading fields, per-question marks, and support/thread workflow changes.

Run:

```bash
python manage.py migrate
python manage.py check
```

Then sanity-check these flows:
- Teacher creates a Q&A question with marks greater than 1
- Student submits Q&A answers
- Teacher assigns per-question marks and feedback in submission review
- Admin can view pending teacher join/leave requests on admin dashboard

## Email Configuration

For password reset functionality:

- **Development**: Emails print to the console (default).
- **Production**: Configure SMTP in `settings.py`.

See [EMAIL_SETUP.md](../EMAIL_SETUP.md) for detailed configuration instructions.

## Troubleshooting

### Database Issues
If you encounter migration issues, try:
```bash
python manage.py migrate --run-syncdb
```

### Port Already in Use
If port 8000 is already in use, specify a different port:
```bash
python manage.py runserver 8001
```

### Module Import Errors
Ensure your virtual environment is activated and dependencies are installed:
```bash
pip install -r requirements.txt
```
