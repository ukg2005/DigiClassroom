from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from django.db.models import Q, Sum
import math
import csv
from classrooms.models import Classroom
from .models import Assignment, Question, Choice, Submission, StudentAnswer, SubmissionDraft, DeadlineEvent
from .forms import AssignmentForm, QuestionForm, DeadlineEventForm


def _is_admin_user(user):
    return bool(user and user.is_authenticated and (user.is_superuser or (hasattr(user, 'profile') and user.profile.is_admin)))


def _assignment_max_points(assignment):
    total = assignment.questions.aggregate(total=Sum('marks')).get('total') or 0
    return int(total)

@login_required(login_url='login')
def assignment_list(request, classroom_pk):
    classroom = get_object_or_404(Classroom, pk=classroom_pk)
    is_admin = _is_admin_user(request.user)
    is_teacher = classroom.is_teacher(request.user)
    is_student = classroom.students.filter(pk=request.user.pk).exists()
    if not (is_teacher or is_student or is_admin):
        return redirect('home')

    assignments = classroom.assignments.all().order_by('-created_at')
    return render(request, 'assignments/assignment_list.html', {
        'classroom': classroom,
        'assignments': assignments,
        'is_teacher': is_teacher,
        'is_admin': is_admin,
    })

@login_required(login_url='login')
def assignment_create(request, classroom_pk):
    classroom = get_object_or_404(Classroom, pk=classroom_pk)
    if not classroom.is_teacher(request.user):
        return redirect('assignment_list', classroom_pk=classroom.pk)
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.classroom = classroom
            assignment.save()
            return redirect('assignment_detail', pk=assignment.pk)
    else:
        form = AssignmentForm()
    return render(request, 'assignments/assignment_form.html', {'form': form, 'classroom': classroom})

@login_required(login_url='login')
def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    is_teacher = assignment.classroom.is_teacher(request.user)
    is_admin = _is_admin_user(request.user)
    is_student = assignment.classroom.students.filter(pk=request.user.pk).exists()
    if not (is_teacher or is_student or is_admin):
        return redirect('home')

    questions = assignment.questions.prefetch_related('choices').all()
    
    submission = None
    submissions = None
    attempts_used = 0
    attempts_left = 0
    can_attempt = False
    is_late_now = bool(assignment.due_date and timezone.now() > assignment.due_date)

    if is_student:
        submissions = Submission.objects.filter(assignment=assignment, student=request.user).order_by('-attempt_number', '-submitted_at')
        submission = submissions.first()
        attempts_used = submissions.count()
        attempts_left = max(assignment.max_attempts - attempts_used, 0)
        can_attempt = attempts_left > 0

        if is_late_now and assignment.late_submission_policy == Assignment.LATE_POLICY_DENY:
            can_attempt = False

    has_content = bool(assignment.prompt.strip()) or questions.exists()
        
    return render(request, 'assignments/assignment_detail.html', {
        'assignment': assignment,
        'is_teacher': is_teacher,
        'questions': questions,
        'submission': submission,
        'submissions': submissions,
        'attempts_used': attempts_used,
        'attempts_left': attempts_left,
        'can_attempt': can_attempt,
        'is_late_now': is_late_now,
        'is_admin': is_admin,
        'is_student': is_student,
        'has_content': has_content,
        'max_points': _assignment_max_points(assignment),
    })

@login_required(login_url='login')
def add_question(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    if not assignment.classroom.is_teacher(request.user):
        return redirect('assignment_detail', pk=pk)
        
    if request.method == 'POST':
        form = QuestionForm(request.POST, assignment=assignment)
        if form.is_valid():
            if assignment.is_quiz:
                question = Question.objects.create(
                    assignment=assignment,
                    question_type=Question.QUESTION_TYPE_MCQ,
                    text=form.cleaned_data['question_text'],
                    marks=form.cleaned_data['question_marks'],
                )
                opts = [
                    (form.cleaned_data['option1'], '1'),
                    (form.cleaned_data['option2'], '2'),
                    (form.cleaned_data['option3'], '3'),
                    (form.cleaned_data['option4'], '4'),
                ]
                correct = form.cleaned_data['correct_option']
                for text, idx in opts:
                    Choice.objects.create(question=question, text=text, is_correct=(idx == correct))
            else:
                Question.objects.create(
                    assignment=assignment,
                    question_type=Question.QUESTION_TYPE_QNA,
                    text=form.cleaned_data['question_text'],
                    marks=form.cleaned_data['question_marks'],
                )
            return redirect('assignment_detail', pk=pk)
    else:
        form = QuestionForm(assignment=assignment)
    return render(request, 'assignments/add_question.html', {'form': form, 'assignment': assignment})

@login_required(login_url='login')
def take_assignment(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    if _is_admin_user(request.user):
        messages.error(request, 'Admins cannot attempt assignments.')
        return redirect('assignment_detail', pk=pk)

    if assignment.classroom.is_teacher(request.user):
        return redirect('assignment_detail', pk=pk)

    if not assignment.classroom.students.filter(pk=request.user.pk).exists():
        return redirect('home')

    existing_attempts = Submission.objects.filter(assignment=assignment, student=request.user).count()
    if existing_attempts >= assignment.max_attempts:
        messages.error(request, 'No attempts remaining for this assignment.')
        return redirect('assignment_detail', pk=pk)

    is_late = bool(assignment.due_date and timezone.now() > assignment.due_date)
    if is_late and assignment.late_submission_policy == Assignment.LATE_POLICY_DENY:
        messages.error(request, 'This assignment is closed because the due date has passed.')
        return redirect('assignment_detail', pk=pk)

    if assignment.is_quiz:
        draft, _ = SubmissionDraft.objects.get_or_create(assignment=assignment, student=request.user)
    else:
        draft = None
        
    if request.method == 'POST':
        if assignment.is_quiz:
            action = request.POST.get('action', 'submit')
            selected_answers = {}

            quiz_questions = assignment.questions.filter(question_type=Question.QUESTION_TYPE_MCQ)
            for question in quiz_questions:
                choice_id = request.POST.get(f'question_{question.id}')
                if choice_id:
                    selected_answers[str(question.id)] = int(choice_id)

            if action == 'save_draft':
                draft.answers = selected_answers
                draft.save(update_fields=['answers', 'updated_at'])
                messages.success(request, 'Draft saved.')
                return redirect('take_assignment', pk=pk)

            score = 0
            submission = Submission.objects.create(
                assignment=assignment,
                student=request.user,
                attempt_number=existing_attempts + 1,
                is_late=is_late,
            )

            for question in quiz_questions:
                choice_id = request.POST.get(f'question_{question.id}')
                if choice_id:
                    choice = Choice.objects.filter(question=question, pk=choice_id).first()
                    if not choice:
                        continue
                    StudentAnswer.objects.create(submission=submission, question=question, choice=choice)
                    if choice.is_correct:
                        score += question.marks

            penalty_percent = 0
            if is_late and assignment.late_submission_policy == Assignment.LATE_POLICY_PENALTY:
                penalty_percent = assignment.late_penalty_percent
                score = max(0, score - math.ceil(score * (penalty_percent / 100)))

            submission.score = score
            submission.late_penalty_percent = penalty_percent
            submission.graded_at = timezone.now()
            submission.save(update_fields=['score', 'late_penalty_percent', 'graded_at'])
            draft.delete()
        else:
            submission = Submission.objects.create(
                assignment=assignment,
                student=request.user,
                attempt_number=existing_attempts + 1,
                is_late=is_late,
                score=0,
                text_response=request.POST.get('general_response', '').strip(),
            )
            qna_questions = assignment.questions.filter(question_type=Question.QUESTION_TYPE_QNA)
            for question in qna_questions:
                text_response = request.POST.get(f'question_{question.id}_text', '').strip()
                if text_response:
                    StudentAnswer.objects.create(
                        submission=submission,
                        question=question,
                        text_response=text_response,
                    )

        messages.success(request, 'Assignment submitted successfully.')
        return redirect('assignment_detail', pk=pk)

    draft_answers = {}
    if draft and isinstance(draft.answers, dict):
        draft_answers = draft.answers

    return render(request, 'assignments/take_assignment.html', {
        'assignment': assignment,
        'draft_answers': draft_answers,
    })

@login_required(login_url='login')
def view_submissions(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    if not assignment.classroom.is_teacher(request.user):
        return redirect('home')
    submissions = assignment.submissions.all().order_by('-submitted_at')
    return render(request, 'assignments/view_submissions.html', {'assignment': assignment, 'submissions': submissions})

@login_required(login_url='login')
def submission_detail(request, pk):
    submission = get_object_or_404(Submission, pk=pk)
    is_teacher = submission.assignment.classroom.is_teacher(request.user)
    is_student = request.user == submission.student
    
    if not (is_teacher or is_student):
        return redirect('home')
        
    answers = submission.answers.select_related('question', 'choice').all() # type: ignore
    max_points = _assignment_max_points(submission.assignment)

    if request.method == 'POST' and is_teacher:
        assignment_feedback = request.POST.get('assignment_feedback', '').strip()
        submission.teacher_feedback = assignment_feedback

        if submission.assignment.is_quiz:
            if not submission.graded_at:
                submission.graded_at = timezone.now()
            submission.save(update_fields=['teacher_feedback', 'graded_at'])
            messages.success(request, 'Assignment feedback updated.')
            return redirect('submission_detail', pk=pk)

        total_score = 0
        for answer in answers:
            max_marks = answer.question.marks
            raw_marks = request.POST.get(f'question_{answer.pk}_marks', '').strip()
            try:
                awarded_marks = int(raw_marks) if raw_marks != '' else 0
            except ValueError:
                awarded_marks = 0
            awarded_marks = max(0, min(awarded_marks, max_marks))
            answer.awarded_marks = awarded_marks
            answer.teacher_feedback = request.POST.get(f'question_{answer.pk}_feedback', '').strip()
            answer.save(update_fields=['awarded_marks', 'teacher_feedback'])
            total_score += awarded_marks

        submission.score = total_score
        submission.graded_at = timezone.now()
        submission.save(update_fields=['score', 'teacher_feedback', 'graded_at'])
        messages.success(request, 'Submission graded successfully.')
        return redirect('submission_detail', pk=pk)

    return render(request, 'assignments/submission_detail.html', {
        'submission': submission,
        'answers': answers,
        'is_teacher': is_teacher,
        'max_points': max_points,
    })

@login_required(login_url='login')
def edit_assignment(request, pk):
    """Edit an assignment"""
    assignment = get_object_or_404(Assignment, pk=pk)
    
    # Check permission: only teacher can edit
    if not assignment.classroom.is_teacher(request.user):
        return redirect('assignment_detail', pk=pk)
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.updated_at = timezone.now()
            assignment.save()
            return redirect('assignment_detail', pk=pk)
    else:
        form = AssignmentForm(instance=assignment)
    
    return render(request, 'assignments/assignment_form.html', {
        'form': form,
        'assignment': assignment,
        'classroom': assignment.classroom,
        'edit': True
    })

@login_required(login_url='login')
def delete_assignment(request, pk):
    """Delete an assignment"""
    assignment = get_object_or_404(Assignment, pk=pk)
    classroom = assignment.classroom
    
    # Check permission: only teacher can delete
    if not classroom.is_teacher(request.user):
        return redirect('assignment_detail', pk=pk)
    
    if request.method == 'POST':
        assignment.delete()
        return redirect('assignment_list', classroom_pk=classroom.pk)
    
    return render(request, 'assignments/delete_assignment.html', {'assignment': assignment})

@login_required(login_url='login')
def teacher_dashboard(request, classroom_pk):
    """Teacher dashboard with class analytics and statistics"""
    classroom = get_object_or_404(Classroom, pk=classroom_pk)
    
    # Check permission: only teacher can view dashboard
    if not classroom.is_teacher(request.user):
        return redirect('home')
    
    assignments = classroom.assignments.all().order_by('-created_at')
    quiz_assignments = assignments.filter(assignment_type=Assignment.ASSIGNMENT_TYPE_QUIZ)
    
    # Calculate analytics
    total_students = classroom.students.count() if hasattr(classroom, 'students') else 0
    total_assignments = assignments.count()
    total_submissions = Submission.objects.filter(assignment__classroom=classroom).count()
    
    # Calculate average score
    submissions = Submission.objects.filter(assignment__classroom=classroom).filter(Q(assignment__assignment_type=Assignment.ASSIGNMENT_TYPE_QUIZ) | Q(graded_at__isnull=False))
    classroom_avg_score = 0
    if submissions.exists():
        # Calculate percentage for each submission, then average
        percentages = []
        for sub in submissions:
            max_points = _assignment_max_points(sub.assignment)
            if max_points > 0:
                pct = (sub.score / max_points) * 100
                percentages.append(pct)
        
        if percentages:
            classroom_avg_score = sum(percentages) / len(percentages)
    
    # Assignment details with submission stats
    assignment_stats = []
    for assignment in assignments:
        subs = assignment.submissions.all()
        late_subs = subs.filter(is_late=True).count()
        max_score = _assignment_max_points(assignment)
        assignment_avg_score = 0
        has_graded_submissions = assignment.is_quiz or subs.filter(graded_at__isnull=False).exists()
        if subs.exists() and max_score > 0 and has_graded_submissions:
            # Calculate percentage for each submission in this assignment, then average
            percentages = []
            for sub in subs:
                pct = (sub.score / max_score) * 100
                percentages.append(pct)
            if percentages:
                assignment_avg_score = sum(percentages) / len(percentages)
        assignment_stats.append({
            'assignment': assignment,
            'total_submitted': subs.count(),
            'late_submissions': late_subs,
            'avg_score': round(assignment_avg_score, 1) if has_graded_submissions else None,
        })
    
    return render(request, 'assignments/teacher_dashboard.html', {
        'classroom': classroom,
        'total_students': total_students,
        'total_assignments': total_assignments,
        'total_submissions': total_submissions,
        'avg_score': round(classroom_avg_score, 2),
        'assignment_stats': assignment_stats,
    })

@login_required(login_url='login')
def student_results(request):
    """Student performance page showing all quiz results and trends"""
    student = request.user
    enrolled_classrooms = student.enrolled_classrooms.all()
    
    # Get all submissions for the student
    submissions = Submission.objects.filter(
        student=student,
    ).filter(
        Q(assignment__assignment_type=Assignment.ASSIGNMENT_TYPE_QUIZ) | Q(graded_at__isnull=False)
    ).select_related('assignment', 'assignment__classroom').order_by('-submitted_at')
    
    # Group by classroom
    classroom_stats = {}
    for classroom in enrolled_classrooms:
        classroom_stats[classroom.id] = {
            'classroom': classroom,
            'submissions': [],
            'completed_quiz_ids': set(),
            'avg_score': 0,
            'total_submissions': 0,
            'completed_quizzes': 0,
            'available_quizzes': classroom.assignments.count(),
            'completion_rate': 0,
        }

    for submission in submissions:
        classroom = submission.assignment.classroom
        if classroom.id not in classroom_stats:
            classroom_stats[classroom.id] = {
                'classroom': classroom,
                'submissions': [],
                'completed_quiz_ids': set(),
                'avg_score': 0,
                'total_submissions': 0,
                'completed_quizzes': 0,
                'available_quizzes': classroom.assignments.count(),
                'completion_rate': 0,
            }
        classroom_stats[classroom.id]['submissions'].append(submission)
        classroom_stats[classroom.id]['completed_quiz_ids'].add(submission.assignment.pk)
        classroom_stats[classroom.id]['total_submissions'] += 1
    
    # Calculate averages per classroom
    for stats in classroom_stats.values():
        stats['completed_quizzes'] = len(stats['completed_quiz_ids'])
        stats['available_quizzes'] = stats['classroom'].assignments.count()
        stats['completion_rate'] = round((stats['completed_quizzes'] / stats['available_quizzes']) * 100, 1) if stats['available_quizzes'] else 0

        if stats['submissions']:
            percentages = []
            for sub in stats['submissions']:
                max_points = _assignment_max_points(sub.assignment)
                if max_points > 0:
                    percentages.append((sub.score / max_points) * 100)

            stats['avg_score'] = round(sum(percentages) / len(percentages), 1) if percentages else 0
        stats['completed_quiz_ids'] = None
    
    # Recent submissions (last 5)
    recent_submissions = submissions[:5]
    
    return render(request, 'assignments/student_results.html', {
        'submissions': submissions,
        'recent_submissions': recent_submissions,
        'classroom_stats': list(classroom_stats.values()),
    })

@login_required(login_url='login')
def export_submissions_csv(request, pk):
    """Export all submissions for an assignment as CSV"""
    assignment = get_object_or_404(Assignment, pk=pk)
    
    # Check permission: only teacher can export
    if not assignment.classroom.is_teacher(request.user):
        return redirect('home')
    
    submissions = assignment.submissions.all().order_by('-submitted_at')
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="submissions_{assignment.id}.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow(['Student', 'Assignment Type', 'Score', 'Max Score', 'Attempt #', 'Submitted At', 'Is Late', 'Late Penalty %', 'Text Response'])
    
    # Write data
    for submission in submissions:
        max_score = _assignment_max_points(submission.assignment)
        writer.writerow([
            submission.student.username,
            submission.assignment.get_assignment_type_display(),
            submission.score,
            max_score,
            submission.attempt_number,
            submission.submitted_at.strftime('%Y-%m-%d %H:%M:%S'),
            'Yes' if submission.is_late else 'No',
            submission.late_penalty_percent,
            submission.text_response,
        ])
    
    return response


@login_required(login_url='login')
def classroom_calendar(request, classroom_pk):
    classroom = get_object_or_404(Classroom, pk=classroom_pk)
    is_admin = _is_admin_user(request.user)
    is_teacher = classroom.is_teacher(request.user)
    is_student = classroom.students.filter(pk=request.user.pk).exists()
    if not (is_teacher or is_student or is_admin):
        return redirect('home')

    due_assignments = classroom.assignments.exclude(due_date__isnull=True).order_by('due_date')
    deadline_events = classroom.deadline_events.all().order_by('due_date')

    items = []
    for assignment in due_assignments:
        items.append({
            'title': assignment.title,
            'description': assignment.prompt,
            'due_date': assignment.due_date,
            'event_type': 'assignment',
            'type_label': assignment.get_assignment_type_display(),
            'link': f'/assignments/{assignment.pk}/',
        })

    for event in deadline_events:
        items.append({
            'title': event.title,
            'description': event.description,
            'due_date': event.due_date,
            'event_type': 'event',
            'type_label': 'Calendar Event',
            'link': None,
        })

    items.sort(key=lambda item: item['due_date'])

    return render(request, 'assignments/classroom_calendar.html', {
        'classroom': classroom,
        'items': items,
        'is_teacher': is_teacher,
    })


@login_required(login_url='login')
def add_deadline_event(request, classroom_pk):
    classroom = get_object_or_404(Classroom, pk=classroom_pk)
    if not classroom.is_teacher(request.user):
        return redirect('classroom_calendar', classroom_pk=classroom.pk)

    if request.method == 'POST':
        form = DeadlineEventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.classroom = classroom
            event.created_by = request.user
            event.save()
            messages.success(request, 'Deadline event added to calendar.')
            return redirect('classroom_calendar', classroom_pk=classroom.pk)
    else:
        form = DeadlineEventForm()

    return render(request, 'assignments/deadline_event_form.html', {
        'classroom': classroom,
        'form': form,
    })
