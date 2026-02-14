from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from classrooms.models import Classroom
from .models import Lecture, LectureComment
from .forms import LectureForm, LectureCommentForm

@login_required(login_url='login')
def lecture_list(request, classroom_pk):
    classroom = get_object_or_404(Classroom, pk=classroom_pk)
    lectures = classroom.lectures.all().order_by('-created_at')
    is_teacher = request.user == classroom.teacher
    return render(request, 'lectures/lecture_list.html', {
        'classroom': classroom, 'lectures': lectures, 'is_teacher': is_teacher
    })

@login_required(login_url='login')
def lecture_create(request, classroom_pk):
    classroom = get_object_or_404(Classroom, pk=classroom_pk)
    if request.user != classroom.teacher:
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
    
    if request.method == 'POST':
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
        'lecture': lecture, 'comments': comments, 'form': form
    })
