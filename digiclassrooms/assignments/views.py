from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from classrooms.models import Classroom
from .models import Assignment, Question, Choice, Submission, StudentAnswer
from .forms import AssignmentForm, QuestionForm

@login_required(login_url='login')
def assignment_list(request, classroom_pk):
    classroom = get_object_or_404(Classroom, pk=classroom_pk)
    assignments = classroom.assignments.all().order_by('-created_at')
    is_teacher = request.user == classroom.teacher
    return render(request, 'assignments/assignment_list.html', {
        'classroom': classroom, 'assignments': assignments, 'is_teacher': is_teacher
    })

@login_required(login_url='login')
def assignment_create(request, classroom_pk):
    classroom = get_object_or_404(Classroom, pk=classroom_pk)
    if request.user != classroom.teacher:
        return redirect('assignments_list', classroom_pk=classroom.pk)
    
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
    is_teacher = request.user == assignment.classroom.teacher
    questions = assignment.questions.all()
    
    submission = None
    if not is_teacher:
        submission = Submission.objects.filter(assignment=assignment, student=request.user).first()
        
    return render(request, 'assignments/assignment_detail.html', {
        'assignment': assignment,
        'is_teacher': is_teacher,
        'questions': questions,
        'submission': submission
    })

@login_required(login_url='login')
def add_question(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    if request.user != assignment.classroom.teacher:
        return redirect('assignment_detail', pk=pk)
        
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = Question.objects.create(assignment=assignment, text=form.cleaned_data['question_text'])
            opts = [
                (form.cleaned_data['option1'], '1'),
                (form.cleaned_data['option2'], '2'),
                (form.cleaned_data['option3'], '3'),
                (form.cleaned_data['option4'], '4'),
            ]
            correct = form.cleaned_data['correct_option']
            for text, idx in opts:
                Choice.objects.create(question=question, text=text, is_correct=(idx == correct))
            return redirect('assignment_detail', pk=pk)
    else:
        form = QuestionForm()
    return render(request, 'assignments/add_question.html', {'form': form, 'assignment': assignment})

@login_required(login_url='login')
def take_assignment(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    if Submission.objects.filter(assignment=assignment, student=request.user).exists():
        return redirect('assignment_detail', pk=pk)
        
    if request.method == 'POST':
        score = 0
        submission = Submission.objects.create(assignment=assignment, student=request.user)
        
        for question in assignment.questions.all():
            choice_id = request.POST.get(f'question_{question.id}')
            if choice_id:
                choice = Choice.objects.get(pk=choice_id)
                StudentAnswer.objects.create(submission=submission, question=question, choice=choice)
                if choice.is_correct:
                    score += 1
        
        submission.score = score
        submission.save()
        return redirect('assignment_detail', pk=pk)
        
    return render(request, 'assignments/take_assignment.html', {'assignment': assignment})

@login_required(login_url='login')
def view_submissions(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    if request.user != assignment.classroom.teacher:
        return redirect('home')
    submissions = assignment.submissions.all()
    return render(request, 'assignments/view_submissions.html', {'assignment': assignment, 'submissions': submissions})

@login_required(login_url='login')
def submission_detail(request, pk):
    submission = get_object_or_404(Submission, pk=pk)
    is_teacher = request.user == submission.assignment.classroom.teacher
    is_student = request.user == submission.student
    
    if not (is_teacher or is_student):
        return redirect('home')
        
    if request.method == 'POST' and is_teacher:
        feedback = request.POST.get('feedback')
        submission.teacher_feedback = feedback
        submission.save()
        return redirect('submission_detail', pk=pk)
        
    answers = submission.answers.all() # type: ignore
    return render(request, 'assignments/submission_detail.html', {
        'submission': submission,
        'answers': answers,
        'is_teacher': is_teacher
    })
