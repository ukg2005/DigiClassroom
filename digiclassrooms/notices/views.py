from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from classrooms.models import Classroom
from .models import Notice, NoticeComment
from .forms import NoticeForm, NoticeCommentForm

@login_required(login_url='login')
def notice_list(request, classroom_pk):
    classroom = get_object_or_404(Classroom, pk=classroom_pk)
    notices = classroom.notices.all().order_by('-created_at')
    is_teacher = request.user == classroom.teacher
    return render(request, 'notices/notice_list.html', {
        'classroom': classroom, 'notices': notices, 'is_teacher': is_teacher
    })

@login_required(login_url='login')
def notice_create(request, classroom_pk):
    classroom = get_object_or_404(Classroom, pk=classroom_pk)
    if request.user != classroom.teacher:
        return redirect('notices_list', classroom_pk=classroom.pk)
    
    if request.method == 'POST':
        form = NoticeForm(request.POST)
        if form.is_valid():
            notice = form.save(commit=False)
            notice.classroom = classroom
            notice.author = request.user
            notice.save()
            return redirect('notices_list', classroom_pk=classroom.pk)
    else:
        form = NoticeForm()
    return render(request, 'notices/notice_form.html', {'form': form, 'classroom': classroom})

@login_required(login_url='login')
def notice_detail(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    comments = notice.comments.filter(parent__isnull=True).order_by('created_at')
    
    if request.method == 'POST':
        form = NoticeCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.notice = notice
            comment.author = request.user
            parent_id = request.POST.get('parent_id')
            if parent_id:
                comment.parent_id = parent_id
            comment.save()
            return redirect('notice_detail', pk=pk)
    else:
        form = NoticeCommentForm()
        
    return render(request, 'notices/notice_detail.html', {
        'notice': notice, 'comments': comments, 'form': form
    })
