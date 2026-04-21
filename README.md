# DigiClassroom

DigiClassroom is a Django-based Learning Management System (LMS) for classroom management, content delivery, assessments, and communication across Admin, Teacher, and Student roles.

The platform focuses on practical teaching workflows: classroom onboarding, assignment authoring, submission review, Q&A grading, calendar deadlines, reminders, and admin support conversations.

---

## Documentation

- [Installation & setup](INSTALLATION.md) — environment setup, migrations, running the server
- [Email configuration](EMAIL_SETUP.md) — SMTP/console backend configuration for notifications
- [Features](FEATURES.md) — user-facing feature overview
- [Implementation notes](IMPLEMENTATION.md) — app structure, design notes, and development details

## Quickstart (local)

See [INSTALLATION.md](INSTALLATION.md) for full details. The shortest path is:

1. Create/activate a virtualenv
2. Install dependencies: `pip install -r requirements.txt`
3. Run migrations: `python digiclassrooms/manage.py migrate`
4. Start server: `python digiclassrooms/manage.py runserver`

## Key Features

### Roles and Dashboards
- Admin dashboard for class creation, teacher join/leave approvals, and support inbox access.
- Teacher dashboard for active classes, class join requests, and classroom operations.
- Student dashboard with enrolled classes, upcoming deadlines, and alert visibility.
- Profile page for user details and quick navigation.

### Classroom Management
- Admin-created classrooms with teacher assignment and membership controls.
- Join with expiring join keys for students.
- Teacher join-request flow for new classes.
- Teacher and student leave-request flows with role-based approvals.

### Lectures and Notices
- Lecture and notice modules with classroom-scoped content.
- Threaded discussion comments with nested replies.
- Edit and moderation support where permitted by role.

### Assignments and Grading
- Assignment types: Quiz and Q&A.
- Question-level marks for both quiz and Q&A prompts.
- Quiz auto-grading with attempts, late policy, and optional late penalty.
- Q&A manual grading by teachers with:
	- per-question marks awarded,
	- per-question feedback,
	- assignment-level feedback.
- Submission history and teacher review views.

### Deadlines and Alerts
- Classroom calendar view for assignment due dates and teacher-created deadline events.
- Student-facing upcoming deadlines with urgency windows.
- Notification reminders for near-term deadlines.

### Support and Communication
- Contact-admin ticketing with categories.
- Threaded support conversations between users and admins.
- Admin support inbox and ticket status handling.

---

## Technical Architecture

### Framework and Technology Stack
- **Backend**: Django with Python
- **Database**: SQLite (default, easily swappable to PostgreSQL or MySQL)
- **Frontend**: HTML5, CSS3, Django Template Language
- **Authentication**: Django's built-in authentication system with custom profile extensions

### Modular Application Structure
The project is organized into app modules:

- **users**: authentication, profiles, notifications, support tickets, support threads.
- **classrooms**: classroom creation, join/leave requests, enrollment, dashboards.
- **lectures**: lecture content and discussion threads.
- **notices**: notice publishing and discussion threads.
- **assignments**: assignment lifecycle, question authoring, submissions, quiz auto-grading, Q&A manual grading.
- **results**: reserved for expanded analytics/reporting workflows.

### Database Relationships
- One-to-one: User to Profile
- Many-to-many: users to classrooms through teacher/student membership links
- Foreign keys: lectures, notices, assignments, events, and requests bound to classrooms
- Hierarchical replies: threaded comments and threaded support messages

### Data Models Overview

#### User and Profile
- `User`: Django's built-in User model
- `Profile`: Custom extension storing teacher/student flag

#### Classroom Hierarchy
- `Classroom`: Container for all classroom content (name, description, teacher, students)
- `Lecture`: Video content (title, YouTube link, creation timestamp)
- `LectureComment`: Threaded discussion on lectures (with parent field for replies)
- `Notice`: Text announcements (title, content, author, timestamp)
- `NoticeComment`: Threaded discussion on notices (with parent field for replies)

#### Assessment System
- `Assignment`: quiz or Q&A container, attempts and late-policy controls
- `Question`: prompt text, type, and marks
- `Choice`: options and correctness for quiz questions
- `Submission`: attempt record, score, assignment feedback, grading timestamp
- `StudentAnswer`: per-question response, awarded marks, and per-question feedback

---

## Getting Started

To set up and run DigiClassroom locally, start with [INSTALLATION.md](INSTALLATION.md).

For email configuration, see [EMAIL_SETUP.md](EMAIL_SETUP.md).

To understand what the project includes and how it’s structured, see [FEATURES.md](FEATURES.md) and [IMPLEMENTATION.md](IMPLEMENTATION.md).

### Classroom join keys

- Teachers see a join key on the Teacher Dashboard and can regenerate it anytime.
- Students must use a valid (unexpired) key to join a classroom.
- Key lifetime is configured via `CLASSROOM_JOIN_KEY_TTL_MINUTES` in `digiclassrooms/digiclassrooms/settings.py`.

### Q&A grading

- Teachers assign marks when creating each prompt.
- Teachers grade Q&A submissions from the submission review page.
- Teachers can provide both per-question and assignment-level feedback.
