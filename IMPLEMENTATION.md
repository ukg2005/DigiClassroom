# Implementation Guide

## Overview

This document summarizes how core features are implemented in the current DigiClassroom codebase.

## App Structure

- users: auth, profiles, notifications, support tickets, support-thread messages.
- classrooms: role dashboards, membership workflows, join keys, join/leave request approvals.
- lectures: lecture content and classroom discussion threads.
- notices: announcement content and classroom discussion threads.
- assignments: assignment lifecycle, question authoring, quiz and Q&A submissions, grading.

## Role and Permission Model

- Admin: class creation, teacher request moderation, support inbox.
- Teacher: classroom teaching operations and grading.
- Student: enrollment, assignment submission, results consumption.
- Access checks are performed in view functions before rendering or processing forms.

## Classroom and Membership Workflows

- Student joins are key-based and time-limited.
- Teacher join requests are reviewed by admins.
- Student leave requests are reviewed in classroom context.
- Teacher leave requests are reviewed from admin dashboards.

## Assignment System Design

### Assignment Types

- Quiz: MCQ-based, auto-graded.
- Q&A: written responses, manually graded.

### Question Model

- Each question includes:
  - question type,
  - prompt text,
  - marks.

### Submission Model

- Stores attempt number, score, late flags, assignment feedback, and grading timestamp.
- For Q&A, each StudentAnswer stores:
  - written response,
  - awarded marks,
  - per-question feedback.

### Grading Flow

- Quiz:
  - score computed on submission from correct choices and question marks,
  - late penalty applied if configured,
  - marked graded at submit time.
- Q&A:
  - teacher reviews each answer,
  - assigns marks per question,
  - writes per-question feedback,
  - writes assignment-level feedback,
  - submission score and graded timestamp updated on save.

### Scoring and Analytics

- Assignment max points are derived from sum of question marks.
- Percentage analytics are based on score divided by assignment max points.
- Q&A submissions only contribute to graded analytics once graded.

## Deadlines and Notifications

- Assignment due dates and teacher-created deadline events feed classroom calendars.
- Student dashboard aggregates upcoming deadlines.
- Reminder notifications are generated for near-term due items.

## Support Ticket Implementation

- Support tickets include category, status, requester, and timestamps.
- Messages are threaded via parent-child relationships.
- Admin and requester can continue a structured discussion in one thread.

## UI Implementation Notes

- Reusable card/list patterns are used across dashboards.
- Dense sections use collapsible panels to reduce visual overload.
- Navigation is consolidated under a role-aware account dropdown.

## Operational Notes

After pulling updates:

```bash
python manage.py migrate
python manage.py check
```
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Generate join keys for existing classrooms
python manage.py generate_join_keys

# Run tests (if you have them)
python manage.py test
```

---

## Frontend Template Considerations

### Comment Display with Edit/Delete
```html
{% if comment.is_edited %}
    <small class="text-muted">(edited)</small>
{% endif %}

{% if user == comment.author or user == classroom.teacher %}
    <a href="{% url 'edit_lecture_comment' comment.id %}">Edit</a>
    <form method="POST" action="{% url 'delete_lecture_comment' comment.id %}">
        {% csrf_token %}
        <button type="submit">Delete</button>
    </form>
{% endif %}
```

### Assignment Due Date Display
```html
{% if assignment.due_date %}
    <p>Due: {{ assignment.due_date }}</p>
    {% if now > assignment.due_date %}
        <span class="badge badge-danger">Overdue</span>
    {% else %}
        <span class="badge badge-info">{{ days_until|default:"Today" }}</span>
    {% endif %}
{% endif %}
```

---

## Common Issues and Solutions

### Issue: Join key not generated for existing classrooms
**Solution**: Run `python manage.py generate_join_keys`

### Issue: "is_edited" field not showing
**Solution**: 
```html
{% if comment.is_edited %}
    <span class="text-muted">(edited at {{ comment.updated_at }})</span>
{% endif %}
```

### Issue: Permissions not checking correctly
**Solution**: Always validate:
```python
is_author = user == object.author
is_teacher = user == classroom.teacher
if not (is_author or is_teacher):
    return redirect('home')
```

---

## Performance Considerations

1. **Search**: Add database indexes on frequently searched fields
   ```python
   class Meta:
       indexes = [
           models.Index(fields=['name']),
           models.Index(fields=['teacher']),
       ]
   ```

2. **Submissions**: Use `select_related()` and `prefetch_related()` in queries

3. **Comments**: Consider pagination for large comment threads

---

## Next Phase Features

After these core features are implemented, consider:
- Advanced analytics dashboard
- Email notifications
- Discussion forums per classroom
- Resource file uploads
- Real-time collaboration features
