from django.shortcuts import render, redirect, get_object_or_404
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Classroom
from .models import ClassroomLeaveRequest, ClassroomTeacherJoinRequest
from .forms import ClassroomForm, JoinClassroomForm, ClassJoinSettingsForm, AdminClassroomForm
from assignments.models import Submission, Assignment, DeadlineEvent
from django.contrib.auth.models import User
from users.models import Notification, SupportTicket


def is_admin_user(user):
    return bool(user and user.is_authenticated and (user.is_superuser or (hasattr(user, 'profile') and user.profile.is_admin)))


def is_teacher_user(user):
    return bool(user and user.is_authenticated and hasattr(user, 'profile') and user.profile.is_teacher)


def _admin_users_queryset():
    return User.objects.filter(Q(is_superuser=True) | Q(profile__is_admin=True)).distinct()


def _create_deadline_reminder_if_missing(user, title, message, link):
    if Notification.objects.filter(recipient=user, title=title, link=link).exists():
        return
    Notification.objects.create(
        recipient=user,
        title=title,
        message=message,
        link=link,
    )

@login_required(login_url='login')
def home(request):
    try:
        if request.user.is_superuser or request.user.profile.is_admin:
            return redirect('admin_dashboard')
        if request.user.profile.is_teacher:
            return redirect('teacher_dashboard')
        else:
            return redirect('student_dashboard')
    except:
        return redirect('student_dashboard')


@login_required(login_url='login')
def admin_dashboard(request):
    if not is_admin_user(request.user):
        return redirect('home')

    if request.method == 'POST':
        form = AdminClassroomForm(request.POST)
        if form.is_valid():
            classroom = form.save(commit=False)
            classroom.created_by = request.user
            classroom.save()
            messages.success(request, f'Created class "{classroom.name}".')
            return redirect('admin_dashboard')
    else:
        form = AdminClassroomForm()

    classroom_cards = []
    for classroom in Classroom.objects.all().order_by('-created_at'):
        submissions = Submission.objects.filter(assignment__classroom=classroom)
        graded_submissions = submissions.filter(Q(assignment__assignment_type=Assignment.ASSIGNMENT_TYPE_QUIZ) | Q(graded_at__isnull=False))
        percentages = []
        for submission in graded_submissions.select_related('assignment'):
            max_points = submission.assignment.questions.aggregate(total=Sum('marks')).get('total') or 0
            if max_points > 0:
                percentages.append((submission.score / max_points) * 100)
        total_assignments = classroom.assignments.count()
        total_students = classroom.students.count()
        completion_rate = 0
        if total_assignments and total_students:
            completion_rate = round((graded_submissions.values('student_id', 'assignment_id').distinct().count() / (total_assignments * total_students)) * 100, 1)
        classroom_cards.append({
            'classroom': classroom,
            'total_students': total_students,
            'total_teachers': classroom.teachers.count(),
            'total_assignments': total_assignments,
            'total_submissions': graded_submissions.count(),
            'avg_score': round(sum(percentages) / len(percentages), 1) if percentages else 0,
            'completion_rate': completion_rate,
            'teacher_leave_requests': classroom.leave_requests.filter(role=ClassroomLeaveRequest.ROLE_TEACHER, status=ClassroomLeaveRequest.STATUS_PENDING).count(),
        })

    pending_leave_requests = ClassroomLeaveRequest.objects.filter(role=ClassroomLeaveRequest.ROLE_TEACHER, status=ClassroomLeaveRequest.STATUS_PENDING).select_related('classroom', 'requester')
    pending_join_requests = ClassroomTeacherJoinRequest.objects.filter(status=ClassroomTeacherJoinRequest.STATUS_PENDING).select_related('classroom', 'requester')
    support_tickets_open = SupportTicket.objects.filter(status=SupportTicket.STATUS_OPEN).count()

    return render(request, 'classrooms/admin_dashboard.html', {
        'form': form,
        'classroom_cards': classroom_cards,
        'pending_leave_requests': pending_leave_requests,
        'pending_join_requests': pending_join_requests,
        'support_tickets_open': support_tickets_open,
    })

@login_required(login_url='login')
def teacher_dashboard(request):
    if not is_teacher_user(request.user):
        return redirect('student_dashboard')

    classrooms = request.user.teaching_classrooms.order_by('-created_at')
    available_classrooms = Classroom.objects.exclude(teachers=request.user).order_by('-created_at')
    pending_join_requests = ClassroomTeacherJoinRequest.objects.filter(
        requester=request.user,
        status=ClassroomTeacherJoinRequest.STATUS_PENDING,
    ).select_related('classroom')
    pending_classroom_ids = set(pending_join_requests.values_list('classroom_id', flat=True))
    return render(request, 'classrooms/teacher_home.html', {
        'classrooms': classrooms,
        'available_classrooms': available_classrooms,
        'pending_classroom_ids': pending_classroom_ids,
        'pending_join_requests': pending_join_requests,
    })

@login_required(login_url='login')
def student_dashboard(request):
    enrolled_classrooms = request.user.enrolled_classrooms.all()
    available_classrooms = Classroom.objects.exclude(students=request.user).filter(joins_enabled=True)

    now = timezone.now()
    week_end = now + timedelta(days=7)
    one_day_end = now + timedelta(days=1)

    upcoming_assignments = Assignment.objects.filter(
        classroom__in=enrolled_classrooms,
        due_date__isnull=False,
        due_date__gte=now,
        due_date__lte=week_end,
    ).select_related('classroom').order_by('due_date')

    upcoming_events = DeadlineEvent.objects.filter(
        classroom__in=enrolled_classrooms,
        due_date__gte=now,
        due_date__lte=week_end,
    ).select_related('classroom').order_by('due_date')

    upcoming_deadlines = []

    for assignment in upcoming_assignments:
        reminder_key = f'assignment-{assignment.pk}-{assignment.due_date.date().isoformat()}'
        detail_link = f'/assignments/{assignment.pk}/?reminder={reminder_key}'
        upcoming_deadlines.append({
            'title': assignment.title,
            'classroom': assignment.classroom,
            'due_date': assignment.due_date,
            'event_type': 'assignment',
            'type_label': assignment.get_assignment_type_display(),
            'link': detail_link,
        })

        if assignment.due_date <= one_day_end:
            _create_deadline_reminder_if_missing(
                request.user,
                'Deadline reminder',
                f'"{assignment.title}" in {assignment.classroom.name} is due within 24 hours.',
                detail_link,
            )

    for event in upcoming_events:
        reminder_key = f'event-{event.pk}-{event.due_date.date().isoformat()}'
        calendar_link = f'/assignments/classroom/{event.classroom.pk}/calendar/?reminder={reminder_key}'
        upcoming_deadlines.append({
            'title': event.title,
            'classroom': event.classroom,
            'due_date': event.due_date,
            'event_type': 'event',
            'type_label': 'Calendar Event',
            'link': calendar_link,
        })

        if event.due_date <= one_day_end:
            _create_deadline_reminder_if_missing(
                request.user,
                'Deadline reminder',
                f'"{event.title}" in {event.classroom.name} is due within 24 hours.',
                calendar_link,
            )

    upcoming_deadlines.sort(key=lambda item: item['due_date'])
    urgent_deadlines = [item for item in upcoming_deadlines if item['due_date'] <= one_day_end]

    return render(request, 'classrooms/student_home.html', {
        'enrolled_classrooms': enrolled_classrooms,
        'available_classrooms': available_classrooms,
        'upcoming_deadlines': upcoming_deadlines,
        'urgent_deadlines': urgent_deadlines,
    })

@login_required(login_url='login')
def setup_classroom(request):
    if not is_admin_user(request.user):
        return redirect('home')

    if request.method == 'POST':
        form = AdminClassroomForm(request.POST)
        if form.is_valid():
            classroom = form.save(commit=False)
            classroom.created_by = request.user
            classroom.save()
            return redirect('admin_dashboard')
    else:
        form = AdminClassroomForm()
    return render(request, 'classrooms/setup_classroom.html', {'form': form})

@login_required(login_url='login')
def enroll_classroom(request):
    # Backward-compatible endpoint: redirect to the key-based join flow.
    return redirect('join_classroom')


@login_required(login_url='login')
def join_classroom(request, pk=None):
    """Join a classroom using its time-limited join key."""
    if is_admin_user(request.user):
        messages.info(request, 'Admins do not join classes as students.')
        return redirect('admin_dashboard')

    if is_teacher_user(request.user):
        messages.info(request, 'Teachers do not join with class keys. Use Request To Teach on the teacher dashboard.')
        return redirect('teacher_dashboard')

    classroom = None
    if pk is not None:
        classroom = get_object_or_404(Classroom, pk=pk)

    if request.method == 'POST':
        form = JoinClassroomForm(request.POST)
        if form.is_valid():
            join_key = form.cleaned_data['join_key']

            target_classroom = classroom
            if target_classroom is None:
                target_classroom = Classroom.objects.filter(join_key__iexact=join_key).first()

            if not target_classroom:
                messages.error(request, 'Invalid join key.')
                return redirect('join_classroom')

            if not target_classroom.joins_enabled:
                messages.error(request, 'Joining is currently disabled for this classroom.')
                return redirect('join_classroom')

            if not target_classroom.is_join_key_valid(join_key):
                if target_classroom.join_key_expires_at and timezone.now() > target_classroom.join_key_expires_at:
                    messages.error(request, 'That join key has expired. Ask your teacher for a new key.')
                else:
                    messages.error(request, 'Invalid join key for this classroom.')
                return redirect('join_classroom_for_classroom', pk=target_classroom.pk)

            target_classroom.students.add(request.user)
            messages.success(request, f'Joined "{target_classroom.name}" successfully!')
            return redirect('classroom_detail', pk=target_classroom.pk)
    else:
        form = JoinClassroomForm()

    return render(request, 'classrooms/join_classroom.html', {
        'form': form,
        'classroom': classroom,
    })


@login_required(login_url='login')
def regenerate_join_key(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk)
    if not classroom.is_teacher(request.user):
        messages.error(request, 'Only the classroom teacher can regenerate the join key.')
        return redirect('home')

    if request.method != 'POST':
        return redirect('classroom_detail', pk=classroom.pk)

    classroom.regenerate_join_key()
    expires_local = timezone.localtime(classroom.join_key_expires_at)
    messages.success(
        request,
        f'New join key generated: {classroom.join_key} (expires at {expires_local.isoformat(timespec="minutes")})'
    )
    return redirect('classroom_detail', pk=classroom.pk)


@login_required(login_url='login')
def request_teacher_join_classroom(request, pk):
    if request.method != 'POST' or not is_teacher_user(request.user):
        return redirect('home')

    classroom = get_object_or_404(Classroom, pk=pk)
    if classroom.is_teacher(request.user):
        messages.info(request, 'You are already a teacher in this class.')
        return redirect('teacher_dashboard')

    req, created = ClassroomTeacherJoinRequest.objects.get_or_create(
        classroom=classroom,
        requester=request.user,
        status=ClassroomTeacherJoinRequest.STATUS_PENDING,
        defaults={'reason': request.POST.get('reason', '')},
    )
    if created:
        admin_users = _admin_users_queryset()
        notif_batch = [
            Notification(
                recipient=admin_user,
                title='New teacher join request',
                message=f'{request.user.username} requested to teach {classroom.name}.',
                link='/admin-dashboard/',
            )
            for admin_user in admin_users
            if admin_user.pk != request.user.pk
        ]
        if notif_batch:
            Notification.objects.bulk_create(notif_batch)
        messages.success(request, f'Join request submitted for "{classroom.name}".')
    else:
        messages.info(request, 'You already have a pending join request for this class.')
    return redirect('teacher_dashboard')


@login_required(login_url='login')
def cancel_teacher_join_request(request, pk):
    join_request = get_object_or_404(
        ClassroomTeacherJoinRequest,
        pk=pk,
        requester=request.user,
        status=ClassroomTeacherJoinRequest.STATUS_PENDING,
    )
    if request.method != 'POST':
        return redirect('teacher_dashboard')

    join_request.delete()
    messages.success(request, 'Join request cancelled.')
    return redirect('teacher_dashboard')


@login_required(login_url='login')
def review_teacher_join_request(request, pk):
    join_request = get_object_or_404(ClassroomTeacherJoinRequest, pk=pk)
    if not is_admin_user(request.user) or request.method != 'POST':
        return redirect('admin_dashboard')

    action = request.POST.get('action')
    if action == 'approve':
        join_request.classroom.teachers.add(join_request.requester)
        join_request.status = ClassroomTeacherJoinRequest.STATUS_APPROVED
        messages.success(request, 'Teacher join request approved.')
        Notification.objects.create(
            recipient=join_request.requester,
            title='Teacher request approved',
            message=f'Your request to teach {join_request.classroom.name} was approved.',
            link=f'/classroom/{join_request.classroom.pk}/',
        )
    else:
        join_request.status = ClassroomTeacherJoinRequest.STATUS_REJECTED
        messages.success(request, 'Teacher join request rejected.')
        Notification.objects.create(
            recipient=join_request.requester,
            title='Teacher request rejected',
            message=f'Your request to teach {join_request.classroom.name} was rejected.',
            link='/teacher/',
        )

    join_request.reviewed_by = request.user
    join_request.reviewed_at = timezone.now()
    join_request.save(update_fields=['status', 'reviewed_by', 'reviewed_at'])
    return redirect('admin_dashboard')


@login_required(login_url='login')
def dashboard_live_counts(request):
    if is_admin_user(request.user):
        return JsonResponse({
            'role': 'admin',
            'pending_join_requests': ClassroomTeacherJoinRequest.objects.filter(status=ClassroomTeacherJoinRequest.STATUS_PENDING).count(),
            'total_classrooms': Classroom.objects.count(),
        })

    if is_teacher_user(request.user):
        return JsonResponse({
            'role': 'teacher',
            'pending_join_requests': ClassroomTeacherJoinRequest.objects.filter(
                requester=request.user,
                status=ClassroomTeacherJoinRequest.STATUS_PENDING,
            ).count(),
            'available_classrooms': Classroom.objects.exclude(teachers=request.user).count(),
        })

    return JsonResponse({'role': 'student'})


@login_required(login_url='login')
def update_join_settings(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk)
    if not classroom.is_teacher(request.user):
        messages.error(request, 'Only the classroom teacher can update join settings.')
        return redirect('home')

    if request.method != 'POST':
        return redirect('classroom_detail', pk=classroom.pk)

    form = ClassJoinSettingsForm(request.POST, instance=classroom)
    if form.is_valid():
        classroom = form.save(commit=False)
        if classroom.join_key:
            classroom.join_key_expires_at = timezone.now() + timedelta(minutes=classroom.get_join_key_ttl_minutes())
        classroom.save()
        messages.success(request, 'Join settings updated.')
    else:
        messages.error(request, 'Unable to update join settings. Please check the form values.')

    return redirect('classroom_detail', pk=classroom.pk)


@login_required(login_url='login')
def remove_student(request, pk, student_id):
    classroom = get_object_or_404(Classroom, pk=pk)
    if not classroom.is_teacher(request.user):
        messages.error(request, 'Only the classroom teacher can remove students.')
        return redirect('classroom_detail', pk=pk)

    if request.method != 'POST':
        return redirect('classroom_detail', pk=pk)

    classroom.students.remove(student_id)
    messages.success(request, 'Student removed from classroom.')
    return redirect('classroom_detail', pk=pk)

@login_required(login_url='login')
def classroom_detail(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk)
    is_admin = is_admin_user(request.user)
    is_teacher = classroom.is_teacher(request.user)
    is_student = request.user in classroom.students.all()
    
    if not (is_teacher or is_student or is_admin):
        return redirect('student_dashboard')

    student_request = ClassroomLeaveRequest.objects.filter(classroom=classroom, requester=request.user, role=ClassroomLeaveRequest.ROLE_STUDENT, status=ClassroomLeaveRequest.STATUS_PENDING).first()
    teacher_request = ClassroomLeaveRequest.objects.filter(classroom=classroom, requester=request.user, role=ClassroomLeaveRequest.ROLE_TEACHER, status=ClassroomLeaveRequest.STATUS_PENDING).first()
    pending_student_requests = ClassroomLeaveRequest.objects.filter(classroom=classroom, role=ClassroomLeaveRequest.ROLE_STUDENT, status=ClassroomLeaveRequest.STATUS_PENDING)
    pending_teacher_requests = ClassroomLeaveRequest.objects.filter(classroom=classroom, role=ClassroomLeaveRequest.ROLE_TEACHER, status=ClassroomLeaveRequest.STATUS_PENDING)

    context = {
        'classroom': classroom,
        'is_teacher': is_teacher,
        'is_admin': is_admin,
        'students': classroom.students.order_by('username'),
        'teachers': classroom.teachers.order_by('username'),
        'join_settings_form': ClassJoinSettingsForm(instance=classroom),
        'default_join_ttl_minutes': Classroom.join_key_ttl_minutes(),
        'effective_join_ttl_minutes': classroom.get_join_key_ttl_minutes(),
        'student_leave_request': student_request,
        'teacher_leave_request': teacher_request,
        'pending_student_requests': pending_student_requests,
        'pending_teacher_requests': pending_teacher_requests,
        'can_discuss': is_teacher or is_student,
    }
    return render(request, 'classrooms/classroom_detail.html', context)


@login_required(login_url='login')
def student_analytics(request, pk, student_id):
    classroom = get_object_or_404(Classroom, pk=pk)
    if not classroom.is_teacher(request.user):
        return redirect('classroom_detail', pk=pk)

    student = get_object_or_404(classroom.students, pk=student_id)
    submissions = Submission.objects.filter(assignment__classroom=classroom, student=student).select_related('assignment').order_by('-submitted_at')
    available_quizzes = classroom.assignments.count()
    graded_submissions = submissions.filter(Q(assignment__assignment_type=Assignment.ASSIGNMENT_TYPE_QUIZ) | Q(graded_at__isnull=False))
    completed_quizzes = graded_submissions.values('assignment_id').distinct().count()
    completion_rate = round((completed_quizzes / available_quizzes) * 100, 1) if available_quizzes else 0

    submission_percentages = []
    for submission in graded_submissions:
        max_points = submission.assignment.questions.aggregate(total=Sum('marks')).get('total') or 0
        if max_points > 0:
            submission_percentages.append((submission.score / max_points) * 100)

    avg_score = round(sum(submission_percentages) / len(submission_percentages), 1) if submission_percentages else 0
    missing_assignments = classroom.assignments.exclude(id__in=graded_submissions.values_list('assignment_id', flat=True))

    return render(request, 'classrooms/student_analytics.html', {
        'classroom': classroom,
        'student': student,
        'submissions': submissions,
        'available_quizzes': available_quizzes,
        'completed_quizzes': completed_quizzes,
        'completion_rate': completion_rate,
        'avg_score': avg_score,
        'missing_assignments': missing_assignments,
    })


@login_required(login_url='login')
def leave_classroom(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk)
    if request.method != 'POST':
        return redirect('classroom_detail', pk=pk)

    if classroom.students.filter(pk=request.user.pk).exists():
        req, created = ClassroomLeaveRequest.objects.get_or_create(
            classroom=classroom,
            requester=request.user,
            role=ClassroomLeaveRequest.ROLE_STUDENT,
            status=ClassroomLeaveRequest.STATUS_PENDING,
            defaults={'reason': request.POST.get('reason', '')},
        )
        if not created:
            messages.info(request, 'You already have a pending leave request for this classroom.')
        else:
            messages.success(request, f'Leave request submitted for "{classroom.name}". Waiting for teacher approval.')
        return redirect('classroom_detail', pk=pk)

    if classroom.is_teacher(request.user):
        req, created = ClassroomLeaveRequest.objects.get_or_create(
            classroom=classroom,
            requester=request.user,
            role=ClassroomLeaveRequest.ROLE_TEACHER,
            status=ClassroomLeaveRequest.STATUS_PENDING,
            defaults={'reason': request.POST.get('reason', '')},
        )
        if not created:
            messages.info(request, 'You already have a pending leave request for this classroom.')
        else:
            messages.success(request, f'Leave request submitted for "{classroom.name}". Waiting for admin approval.')
        return redirect('classroom_detail', pk=pk)

    messages.error(request, 'You are not a member of this classroom.')
    return redirect('home')


@login_required(login_url='login')
def review_leave_request(request, pk):
    leave_request = get_object_or_404(ClassroomLeaveRequest, pk=pk)
    classroom = leave_request.classroom
    is_admin = is_admin_user(request.user)
    is_teacher = classroom.is_teacher(request.user)
    if leave_request.role == ClassroomLeaveRequest.ROLE_STUDENT:
        allowed = is_teacher
    else:
        allowed = is_admin

    def _redirect_back():
        if is_admin and leave_request.role == ClassroomLeaveRequest.ROLE_TEACHER:
            return redirect('admin_dashboard')
        return redirect('classroom_detail', pk=classroom.pk)

    if not allowed or request.method != 'POST':
        return _redirect_back()

    action = request.POST.get('action')
    if action == 'reject':
        leave_request.status = ClassroomLeaveRequest.STATUS_REJECTED
        leave_request.reviewed_by = request.user
        leave_request.reviewed_at = timezone.now()
        leave_request.save(update_fields=['status', 'reviewed_by', 'reviewed_at'])
        messages.success(request, 'Leave request rejected.')
        return _redirect_back()

    if leave_request.role == ClassroomLeaveRequest.ROLE_STUDENT:
        classroom.students.remove(leave_request.requester)
    else:
        classroom.teachers.remove(leave_request.requester)
        if classroom.teacher_id == leave_request.requester_id:
            remaining_teacher = classroom.teachers.exclude(pk=leave_request.requester_id).first()
            if remaining_teacher:
                classroom.teacher = remaining_teacher
                classroom.save(update_fields=['teacher'])
            else:
                messages.error(request, 'Cannot approve teacher leave because no other teacher remains.')
                return _redirect_back()

    leave_request.status = ClassroomLeaveRequest.STATUS_APPROVED
    leave_request.reviewed_by = request.user
    leave_request.reviewed_at = timezone.now()
    leave_request.save(update_fields=['status', 'reviewed_by', 'reviewed_at'])
    messages.success(request, 'Leave request approved.')
    return _redirect_back()

@login_required(login_url='login')
def classroom_notices(request, pk):
    return redirect('notices_list', classroom_pk=pk)

@login_required(login_url='login')
def classroom_lectures(request, pk):
    return redirect('lectures_list', classroom_pk=pk)

@login_required(login_url='login')
def classroom_assignments(request, pk):
    return redirect('assignment_list', classroom_pk=pk)

@login_required(login_url='login')
def search_classrooms(request):
    """Search available classrooms by name, description, or teacher"""
    query = request.GET.get('q', '').strip()
    classrooms = Classroom.objects.exclude(students=request.user).filter(joins_enabled=True)
    
    if query:
        classrooms = classrooms.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(teacher__first_name__icontains=query) |
            Q(teacher__last_name__icontains=query) |
            Q(teachers__first_name__icontains=query) |
            Q(teachers__last_name__icontains=query)
        ).distinct()
    
    # Pagination
    paginator = Paginator(classrooms, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'classrooms/search.html', {
        'page_obj': page_obj,
        'query': query
    })
