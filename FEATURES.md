# DigiClassroom - Features Guide

This guide lists the implemented features currently available in DigiClassroom.

## Role-Based Experience

### Admin
- Create classrooms and assign teachers.
- Review pending teacher join requests.
- Review pending teacher leave requests.
- Access support inbox and manage complaint/ticket status.
- Monitor class-level summary cards and platform activity.

### Teacher
- Manage teaching classrooms from a dedicated dashboard.
- Request to teach additional classrooms.
- Create and manage lectures, notices, and assignments.
- Review submissions and provide detailed feedback.

### Student
- Join classrooms with valid join keys.
- View upcoming deadlines and reminders.
- Submit quiz and Q&A assignments.
- View results, grades, and teacher feedback.

## Classroom and Membership Features

- Join keys for student enrollment (time-limited and regeneratable).
- Teacher join requests for classrooms.
- Leave-request workflow:
    - student leave requests reviewed in classroom context,
    - teacher leave requests reviewed by admins.
- Classroom detail hub with notices, discussion, lectures, and assignments.

## Learning Content Features

- Lecture publishing with discussion threads.
- Notice publishing with threaded comments.
- Nested replies for discussion continuity.
- Permission-aware edit/delete controls for content and comments.

## Assignment and Grading Features

### Assignment Types
- Quiz assignments (MCQ).
- Q&A assignments (written responses).

### Authoring
- Teachers create assignments with due dates and late policies.
- Teachers add prompts/questions with per-question marks.
- Quiz questions include options and correct-answer selection.

### Submission and Attempts
- Attempt tracking per assignment.
- Draft save for quiz responses.
- Late submission handling with allow/deny/penalty behavior.

### Grading and Feedback
- Auto-grading for quizzes.
- Manual grading for Q&A:
    - marks awarded per question,
    - per-question feedback,
    - assignment-level feedback.
- Submission review pages for both teachers and students.

## Deadlines, Calendar, and Alerts

- Classroom calendar with assignment due dates and deadline events.
- Teacher-created deadline events.
- Student dashboard list of upcoming deadlines.
- Near-deadline reminder notifications.

## Support and Communication

- Contact-admin support form with categories.
- Admin support inbox for ticket triage.
- Threaded support conversation per ticket.
- Ticket status flow (open, in progress, resolved, closed).

## UI and UX Improvements

- Standardized button styles across pages.
- Simplified navigation with account dropdown.
- Collapsible panels for dense sections (requests, histories, threads).
- Cleaner classroom card layouts and reduced action clutter.

## Analytics and Reporting

- Teacher classroom analytics views.
- Student result summaries by classroom.
- Submission exports to CSV for teacher workflows.

## Migration Note

After pulling updates, run:

```bash
python manage.py migrate
```

Existing classrooms will have empty join_keys - run management command to generate:

```bash
python manage.py generate_join_keys
```

---

## Next Steps

1. Create management command for generating join keys
2. Update views to handle join key logic
3. Add forms for edit/delete functionality
4. Create search views and templates
5. Add submission history views
6. Update templates with new UI
7. Create management commands for utilities
