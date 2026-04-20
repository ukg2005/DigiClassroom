from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from classrooms.models import Classroom
from .models import Lecture, LectureComment
from .forms import LectureForm, LectureCommentForm


def _is_admin_user(user):
    return bool(user and user.is_authenticated and (user.is_superuser or (hasattr(user, 'profile') and user.profile.is_admin)))

@login_required(login_url='login')
def lecture_list(request, classroom_pk):
    classroom = get_object_or_404(Classroom, pk=classroom_pk)
    lectures = classroom.lectures.all().order_by('-created_at')
    is_teacher = classroom.is_teacher(request.user)
    return render(request, 'lectures/lecture_list.html', {
        'classroom': classroom, 'lectures': lectures, 'is_teacher': is_teacher
    })

@login_required(login_url='login')
def lecture_create(request, classroom_pk):
    classroom = get_object_or_404(Classroom, pk=classroom_pk)
    if not classroom.is_teacher(request.user):
        return redirect('lectures_list', classroom_pk=classroom.pk)
    
    if request.method == 'POST':
        form = LectureForm(request.POST)
        if form.is_valid():
            lecture = form.save(commit=False)
            lecture.classroom = classroom
            lecture.save()
            return redirect('lectures_list', classroom_pk=classroom.pk)
    else:
        form = LectureForm()
    return render(request, 'lectures/lecture_form.html', {'form': form, 'classroom': classroom})

@login_required(login_url='login')
def lecture_detail(request, pk):
    lecture = get_object_or_404(Lecture, pk=pk)
    comments = lecture.comments.filter(parent__isnull=True).order_by('created_at') # pyright: ignore[reportAttributeAccessIssue]
    is_teacher = lecture.classroom.is_teacher(request.user)
    is_student = lecture.classroom.students.filter(pk=request.user.pk).exists()
    is_admin = _is_admin_user(request.user)
    can_interact = is_teacher or is_student

    if not (is_teacher or is_student or is_admin):
        return redirect('home')
    
    if request.method == 'POST':
        if not can_interact:
            messages.error(request, 'Admins cannot participate in class discussions.')
            return redirect('lecture_detail', pk=pk)
        if lecture.is_thread_locked and not lecture.classroom.is_teacher(request.user):
            messages.error(request, 'This discussion is locked by the teacher.')
            return redirect('lecture_detail', pk=pk)

        form = LectureCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.lecture = lecture
            comment.author = request.user
            parent_id = request.POST.get('parent_id')
            if parent_id:
                comment.parent_id = parent_id
            comment.save()
            return redirect('lecture_detail', pk=pk)
    else:
        form = LectureCommentForm()
        
    return render(request, 'lectures/lecture_detail.html', {
        'lecture': lecture,
        'comments': comments,
        'form': form,
        'is_teacher': is_teacher,
        'can_interact': can_interact,
    })


@login_required(login_url='login')
def toggle_lecture_thread_lock(request, pk):
    lecture = get_object_or_404(Lecture, pk=pk)
    if not lecture.classroom.is_teacher(request.user) or request.method != 'POST':
        return redirect('lecture_detail', pk=pk)

    lecture.is_thread_locked = not lecture.is_thread_locked
    lecture.save(update_fields=['is_thread_locked'])
    messages.success(request, 'Lecture discussion lock updated.')
    return redirect('lecture_detail', pk=pk)

@login_required(login_url='login')
def edit_lecture_comment(request, comment_id):
    """Edit a lecture comment"""
    comment = get_object_or_404(LectureComment, pk=comment_id)
    lecture = comment.lecture
    
    # Check permission: only comment author or teacher can edit
    if request.user != comment.author and not lecture.classroom.is_teacher(request.user):
        return redirect('lecture_detail', pk=lecture.pk)
    
    if request.method == 'POST':
        form = LectureCommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.is_edited = True
            comment.save()
            return redirect('lecture_detail', pk=lecture.pk)
    else:
        form = LectureCommentForm(instance=comment)
    
    return render(request, 'lectures/edit_comment.html', {
        'form': form,
        'comment': comment,
        'lecture': lecture
    })

@login_required(login_url='login')
def delete_lecture_comment(request, comment_id):
    """Delete a lecture comment"""
    comment = get_object_or_404(LectureComment, pk=comment_id)
    lecture = comment.lecture
    
    # Check permission: only comment author or teacher can delete
    if request.user != comment.author and not lecture.classroom.is_teacher(request.user):
        return redirect('lecture_detail', pk=lecture.pk)
    
    if request.method == 'POST':
        comment.delete()
        return redirect('lecture_detail', pk=lecture.pk)
    
    return render(request, 'lectures/delete_comment.html', {'comment': comment})

@login_required(login_url='login')
def edit_lecture(request, pk):
    """Edit a lecture"""
    lecture = get_object_or_404(Lecture, pk=pk)
    
    # Check permission: only teacher can edit
    if not lecture.classroom.is_teacher(request.user):
        return redirect('lecture_detail', pk=pk)
    
    if request.method == 'POST':
        form = LectureForm(request.POST, instance=lecture)
        if form.is_valid():
            lecture = form.save(commit=False)
            lecture.updated_at = __import__('django.utils.timezone', fromlist=['now']).now()
            lecture.save()
            return redirect('lecture_detail', pk=pk)
    else:
        form = LectureForm(instance=lecture)
    
    return render(request, 'lectures/lecture_form.html', {
        'form': form,
        'lecture': lecture,
        'classroom': lecture.classroom,
        'edit': True
    })

@login_required(login_url='login')
def delete_lecture(request, pk):
    """Delete a lecture"""
    lecture = get_object_or_404(Lecture, pk=pk)
    classroom = lecture.classroom
    
    # Check permission: only teacher can delete
    if not classroom.is_teacher(request.user):
        return redirect('lecture_detail', pk=pk)
    
    if request.method == 'POST':
        lecture.delete()
        return redirect('lectures_list', classroom_pk=classroom.pk)
    
    return render(request, 'lectures/delete_lecture.html', {'lecture': lecture})
