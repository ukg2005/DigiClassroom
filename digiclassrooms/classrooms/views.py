from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Classroom
from .forms import ClassroomForm

@login_required(login_url='login')
def home(request):
    try:
        if request.user.profile.is_teacher:
            return redirect('teacher_dashboard')
        else:
            return redirect('student_dashboard')
    except:
        return redirect('student_dashboard')

@login_required(login_url='login')
def teacher_dashboard(request):
    if not hasattr(request.user, 'profile') or not request.user.profile.is_teacher:
        return redirect('student_dashboard')
        
    try:
        classroom = request.user.teaching_classroom
        notices = classroom.notices.all().order_by('-created_at')[:5]
        lectures = classroom.lectures.all().order_by('-created_at')[:5]
        assignments = classroom.assignments.all().order_by('-created_at')[:5]
    except Classroom.DoesNotExist:
        return redirect('setup_classroom')
        
    return render(request, 'classrooms/teacher_home.html', {
        'classroom': classroom,
        'notices': notices,
        'lectures': lectures,
        'assignments': assignments,
    })

@login_required(login_url='login')
def student_dashboard(request):
    enrolled_classrooms = request.user.enrolled_classrooms.all()
    available_classrooms = Classroom.objects.exclude(students=request.user)
    return render(request, 'classrooms/student_home.html', {
        'enrolled_classrooms': enrolled_classrooms,
        'available_classrooms': available_classrooms
    })

@login_required(login_url='login')
def setup_classroom(request):
    if not request.user.profile.is_teacher:
        return redirect('home')
    
    if hasattr(request.user, 'teaching_classroom'):
        return redirect('teacher_dashboard')

    if request.method == 'POST':
        form = ClassroomForm(request.POST)
        if form.is_valid():
            classroom = form.save(commit=False)
            classroom.teacher = request.user
            classroom.save()
            return redirect('teacher_dashboard')
    else:
        form = ClassroomForm()
    return render(request, 'classrooms/setup_classroom.html', {'form': form})

@login_required(login_url='login')
def enroll_classroom(request):
    if request.method == 'POST':
        classroom_id = request.POST.get('classroom_id')
        if classroom_id:
            classroom = get_object_or_404(Classroom, pk=int(classroom_id))
            classroom.students.add(request.user)
    return redirect('student_dashboard')

@login_required(login_url='login')
def classroom_detail(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk)
    is_teacher = request.user == classroom.teacher
    is_student = request.user in classroom.students.all()
    
    if not (is_teacher or is_student):
        return redirect('student_dashboard')

    context = {
        'classroom': classroom,
        'is_teacher': is_teacher,
    }
    return render(request, 'classrooms/classroom_detail.html', context)

@login_required(login_url='login')
def classroom_notices(request, pk):
    return redirect('notices_list', classroom_pk=pk)

@login_required(login_url='login')
def classroom_lectures(request, pk):
    return redirect('lectures_list', classroom_pk=pk)

@login_required(login_url='login')
def classroom_assignments(request, pk):
    return redirect('assignments_list', classroom_pk=pk)
