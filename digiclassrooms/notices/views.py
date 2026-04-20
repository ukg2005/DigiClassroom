from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from classrooms.models import Classroom
from .models import Notice, NoticeComment, GlobalDiscussionPost, ClassDiscussionPost
from .forms import NoticeForm, NoticeCommentForm


def _is_admin_user(user):
    return bool(user and user.is_authenticated and (user.is_superuser or (hasattr(user, 'profile') and user.profile.is_admin)))


def _get_discussion_root(post):
    current = post
    while current.parent_id:
        parent = ClassDiscussionPost.objects.filter(pk=current.parent_id).first()
        if not parent:
            break
        current = parent
    return current


def _build_discussion_tree(posts):
    nodes = {}
    roots = []
    for post in posts:
        nodes[post.pk] = {'post': post, 'children': []}

    for post in posts:
        node = nodes[post.pk]
        if post.parent_id and post.parent_id in nodes:
            nodes[post.parent_id]['children'].append(node)
        else:
            roots.append(node)

    return roots, nodes

@login_required(login_url='login')
def notice_list(request, classroom_pk):
    classroom = get_object_or_404(Classroom, pk=classroom_pk)
    notices = classroom.notices.all().order_by('-is_pinned', '-created_at')
    is_teacher = classroom.is_teacher(request.user)
    return render(request, 'notices/notice_list.html', {
        'classroom': classroom, 'notices': notices, 'is_teacher': is_teacher
    })

@login_required(login_url='login')
def notice_create(request, classroom_pk):
    classroom = get_object_or_404(Classroom, pk=classroom_pk)
    if not classroom.is_teacher(request.user):
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
    is_teacher = notice.classroom.is_teacher(request.user)
    is_student = notice.classroom.students.filter(pk=request.user.pk).exists()
    is_admin = _is_admin_user(request.user)
    can_interact = is_teacher or is_student

    if not (is_teacher or is_student or is_admin):
        return redirect('home')
    
    if request.method == 'POST':
        if not can_interact:
            messages.error(request, 'Admins cannot participate in class discussions.')
            return redirect('notice_detail', pk=pk)
        if notice.is_thread_locked and not notice.classroom.is_teacher(request.user):
            messages.error(request, 'This thread is locked by the teacher.')
            return redirect('notice_detail', pk=pk)

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
        'notice': notice,
        'comments': comments,
        'form': form,
        'is_teacher': is_teacher,
        'can_interact': can_interact,
    })


@login_required(login_url='login')
def toggle_notice_pin(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    if not notice.classroom.is_teacher(request.user) or request.method != 'POST':
        return redirect('notice_detail', pk=pk)

    notice.is_pinned = not notice.is_pinned
    notice.save(update_fields=['is_pinned'])
    messages.success(request, 'Notice pin state updated.')
    return redirect('notice_detail', pk=pk)


@login_required(login_url='login')
def toggle_notice_thread_lock(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    if not notice.classroom.is_teacher(request.user) or request.method != 'POST':
        return redirect('notice_detail', pk=pk)

    notice.is_thread_locked = not notice.is_thread_locked
    notice.save(update_fields=['is_thread_locked'])
    messages.success(request, 'Notice thread lock updated.')
    return redirect('notice_detail', pk=pk)

@login_required(login_url='login')
def edit_notice_comment(request, comment_id):
    """Edit a notice comment"""
    comment = get_object_or_404(NoticeComment, pk=comment_id)
    notice = comment.notice
    
    # Check permission: only comment author or teacher can edit
    if request.user != comment.author and not notice.classroom.is_teacher(request.user):
        return redirect('notice_detail', pk=notice.pk)
    
    if request.method == 'POST':
        form = NoticeCommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.is_edited = True
            comment.save()
            return redirect('notice_detail', pk=notice.pk)
    else:
        form = NoticeCommentForm(instance=comment)
    
    return render(request, 'notices/edit_comment.html', {
        'form': form,
        'comment': comment,
        'notice': notice
    })

@login_required(login_url='login')
def delete_notice_comment(request, comment_id):
    """Delete a notice comment"""
    comment = get_object_or_404(NoticeComment, pk=comment_id)
    notice = comment.notice
    
    # Check permission: only comment author or teacher can delete
    if request.user != comment.author and not notice.classroom.is_teacher(request.user):
        return redirect('notice_detail', pk=notice.pk)
    
    if request.method == 'POST':
        comment.delete()
        return redirect('notice_detail', pk=notice.pk)
    
    return render(request, 'notices/delete_comment.html', {'comment': comment})

@login_required(login_url='login')
def edit_notice(request, pk):
    """Edit a notice"""
    notice = get_object_or_404(Notice, pk=pk)
    
    # Check permission: only teacher can edit
    if not notice.classroom.is_teacher(request.user):
        return redirect('notice_detail', pk=pk)
    
    if request.method == 'POST':
        form = NoticeForm(request.POST, instance=notice)
        if form.is_valid():
            notice = form.save(commit=False)
            notice.updated_at = __import__('django.utils.timezone', fromlist=['now']).now()
            notice.save()
            return redirect('notice_detail', pk=pk)
    else:
        form = NoticeForm(instance=notice)
    
    return render(request, 'notices/notice_form.html', {
        'form': form,
        'notice': notice,
        'classroom': notice.classroom,
        'edit': True
    })

@login_required(login_url='login')
def delete_notice(request, pk):
    """Delete a notice"""
    notice = get_object_or_404(Notice, pk=pk)
    classroom = notice.classroom
    
    # Check permission: only teacher can delete
    if not classroom.is_teacher(request.user):
        return redirect('notice_detail', pk=pk)
    
    if request.method == 'POST':
        notice.delete()
        return redirect('notices_list', classroom_pk=classroom.pk)
    
    return render(request, 'notices/delete_notice.html', {'notice': notice})


@login_required(login_url='login')
def global_discussion(request):
    if request.method == 'POST':
        content = (request.POST.get('content') or '').strip()
        if not content:
            messages.error(request, 'Post content cannot be empty.')
            return redirect('global_discussion')
        GlobalDiscussionPost.objects.create(author=request.user, content=content)
        messages.success(request, 'Posted to global discussion.')
        return redirect('global_discussion')

    posts = GlobalDiscussionPost.objects.select_related('author')[:50]
    return render(request, 'notices/global_discussion.html', {'posts': posts})


@login_required(login_url='login')
def delete_global_post(request, pk):
    post = get_object_or_404(GlobalDiscussionPost, pk=pk)
    if request.method != 'POST':
        return redirect('global_discussion')

    if request.user != post.author and (not hasattr(request.user, 'profile') or not request.user.profile.is_teacher):
        messages.error(request, 'You can only delete your own posts.')
        return redirect('global_discussion')

    post.delete()
    messages.success(request, 'Post deleted.')
    return redirect('global_discussion')


@login_required(login_url='login')
def class_discussion(request, classroom_pk):
    classroom = get_object_or_404(Classroom, pk=classroom_pk)
    is_member = classroom.is_teacher(request.user) or classroom.students.filter(pk=request.user.pk).exists()
    if not is_member:
        return redirect('home')

    if request.method == 'POST':
        content = (request.POST.get('content') or '').strip()
        if not content:
            messages.error(request, 'Post content cannot be empty.')
            return redirect('class_discussion', classroom_pk=classroom.pk)
        ClassDiscussionPost.objects.create(classroom=classroom, author=request.user, content=content)
        messages.success(request, 'Thread posted.')
        return redirect('class_discussion', classroom_pk=classroom.pk)

    posts = ClassDiscussionPost.objects.filter(classroom=classroom).select_related('author').order_by('created_at')
    threads, _ = _build_discussion_tree(posts)
    return render(request, 'notices/class_discussion.html', {'classroom': classroom, 'threads': threads, 'is_teacher': classroom.is_teacher(request.user)})


@login_required(login_url='login')
def class_discussion_thread(request, pk):
    thread = get_object_or_404(ClassDiscussionPost, pk=pk, parent__isnull=True)
    classroom = thread.classroom
    is_member = classroom.is_teacher(request.user) or classroom.students.filter(pk=request.user.pk).exists()
    if not is_member:
        return redirect('home')

    if request.method == 'POST':
        content = (request.POST.get('content') or '').strip()
        parent_id = request.POST.get('parent_id')
        if not content:
            messages.error(request, 'Reply content cannot be empty.')
            return redirect('class_discussion_thread', pk=thread.pk)
        parent = None
        if parent_id:
            parent = ClassDiscussionPost.objects.filter(pk=parent_id, classroom=classroom).first()
        ClassDiscussionPost.objects.create(
            classroom=classroom,
            author=request.user,
            content=content,
            parent=parent or thread,
        )
        messages.success(request, 'Reply posted.')
        return redirect('class_discussion_thread', pk=thread.pk)

    posts = ClassDiscussionPost.objects.filter(classroom=classroom).select_related('author').order_by('created_at')
    _, nodes = _build_discussion_tree(posts)
    thread_node = nodes.get(thread.pk)
    is_teacher = classroom.is_teacher(request.user)
    return render(
        request,
        'notices/class_discussion_thread.html',
        {'classroom': classroom, 'thread': thread, 'thread_node': thread_node, 'is_teacher': is_teacher},
    )


@login_required(login_url='login')
def edit_class_discussion_post(request, pk):
    post = get_object_or_404(ClassDiscussionPost, pk=pk)
    classroom = post.classroom
    root = _get_discussion_root(post)
    is_member = classroom.is_teacher(request.user) or classroom.students.filter(pk=request.user.pk).exists()
    if not is_member:
        return redirect('home')

    if request.user != post.author and not classroom.is_teacher(request.user):
        messages.error(request, 'You do not have permission to edit this post.')
        return redirect('class_discussion_thread', pk=root.pk)

    if request.method == 'POST':
        content = (request.POST.get('content') or '').strip()
        if not content:
            messages.error(request, 'Post content cannot be empty.')
            return redirect('edit_class_discussion_post', pk=post.pk)

        post.content = content
        post.is_edited = True
        post.save(update_fields=['content', 'is_edited', 'updated_at'])
        messages.success(request, 'Post updated.')
        return redirect('class_discussion_thread', pk=root.pk)

    return render(request, 'notices/edit_class_discussion_post.html', {'post': post, 'classroom': classroom, 'root_post': root})


@login_required(login_url='login')
def delete_class_discussion_post(request, pk):
    post = get_object_or_404(ClassDiscussionPost, pk=pk)
    classroom = post.classroom
    is_member = classroom.is_teacher(request.user) or classroom.students.filter(pk=request.user.pk).exists()
    if not is_member:
        return redirect('home')

    can_delete = request.user == post.author or classroom.is_teacher(request.user)
    if not can_delete:
        messages.error(request, 'You do not have permission to delete this post.')
        root = _get_discussion_root(post)
        return redirect('class_discussion_thread', pk=root.pk)

    if request.method != 'POST':
        root = _get_discussion_root(post)
        return redirect('class_discussion_thread', pk=root.pk)

    root = _get_discussion_root(post)
    post.delete()
    messages.success(request, 'Post deleted.')
    if root.pk == post.pk:
        return redirect('class_discussion', classroom_pk=classroom.pk)
    return redirect('class_discussion_thread', pk=root.pk)
