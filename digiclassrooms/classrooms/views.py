from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required(login_url='login')
def home(request):
    try:
        is_teacher = request.user.profile.is_teacher
    except:
        is_teacher = False
    if is_teacher:
        return render(request, 'classrooms/teacher_home.html')
    else:
        return render(request, 'classrooms/student_home.html')