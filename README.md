# DigiClassroom

DigiClassroom is a robust, Django-based Learning Management System (LMS) designed to facilitate seamless interaction between teachers and students. It provides a virtual environment for managing classrooms, sharing resources, and conducting assessments.

## Features

### 👥 User Roles
- **Teacher**: Can create classrooms, post notices, upload video lectures, and create assignments.
- **Student**: Can join classrooms, view notices, watch lectures, and submit assignments.

### 🏫 Classroom Management
- **Create Classroom**: Teachers can set up their own virtual classrooms.
- **Join Classroom**: Students can browse available classrooms and enroll with a single click.
- **Dashboard**: personalized dashboards for both teachers and students to track their activities.

### 📢 Notices & Announcements
- **Post Notices**: Teachers can share important updates and announcements.
- **Comments**: Students can ask questions or discuss notices through a commenting system.

### 🎥 Video Lectures
- **YouTube Integration**: Teachers can embed educational videos directly from YouTube.
- **Interactive Learning**: Students can watch lectures and participate in discussions via comments.

### 📝 Assignments & Assessment
- **Create Assignments**: Teachers can design assignments with multiple-choice questions.
- **Auto-Grading**: Submissions are automatically graded, providing instant feedback to students.
- **Submission Tracking**: Teachers can review student submissions and scores.

## Tech Stack

- **Backend**: Django 6.0.2 (Python)
- **Database**: SQLite (Default, easily swappable)
- **Frontend**: HTML5, CSS3, Django Template Language
- **Authentication**: Django Auth System

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/yourusername/DigiClassroom.git
    cd DigiClassroom
    ```

2.  **Create a Virtual Environment**
    ```bash
    # Windows
    python -m venv venv
    venv/Scripts/activate

    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Apply Database Migrations**
    ```bash
    cd digiclassrooms
    python manage.py migrate
    ```

5.  **Create a Superuser (Optional)**
    To access the Django admin interface:
    ```bash
    python manage.py createsuperuser
    ```

6.  **Run the Development Server**
    ```bash
    python manage.py runserver
    ```

7.  **Generate Test Data (Optional)**
    There is a custom management command to pre-populate the database with dummy users, classrooms, lectures, notices, and assignments. This is helpful for trying out the application quickly.

    ```bash
    python manage.py create_dummy_data
    ```
    
    This will create:
    - **Teacher**: `teacher1` (password: `password123`)
    - **Students**: `student1`, `student2`, `student3` (all passwords: `password123`)
    - **Classrooms**: Mathematics, Physics
    - **Content**: Sample Lectures, Notices, Assignments, and Submissions

8.  **Access the Application**
    Open your browser and navigate to `http://127.0.0.1:8000/`.

## 📧 Email Configuration

DigiClassroom supports multiple email backends for password resets and notifications. 
- **Development**: Defaults to console output.
- **Production**: Supports SMTP (Gmail, SendGrid, etc.).

For detailed configuration instructions, please refer to [EMAIL_SETUP.md](EMAIL_SETUP.md).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
