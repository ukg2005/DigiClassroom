from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from classrooms.models import Classroom
from lectures.models import Lecture, LectureComment
from notices.models import Notice, NoticeComment
from assignments.models import Assignment, Question, Choice, Submission, StudentAnswer
from users.models import Profile


class Command(BaseCommand):
    help = 'Creates dummy data for testing the DigiClassroom application'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Creating dummy data...'))
        
        # Create users
        self.stdout.write('Creating users...')
        
        # Create teacher
        teacher, created = User.objects.get_or_create(
            username='teacher1',
            defaults={
                'email': 'teacher@example.com',
                'first_name': 'John',
                'last_name': 'Smith'
            }
        )
        if created:
            teacher.set_password('password123')
            teacher.save()
            profile, _ = Profile.objects.get_or_create(user=teacher)
            profile.is_teacher = True
            profile.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Created teacher: {teacher.username}'))
        else:
            self.stdout.write(f'  Teacher {teacher.username} already exists')
        
        # Create students
        students = []
        student_data = [
            ('student1', 'Alice', 'Johnson', 'alice@example.com'),
            ('student2', 'Bob', 'Williams', 'bob@example.com'),
            ('student3', 'Charlie', 'Brown', 'charlie@example.com'),
        ]
        
        for username, first, last, email in student_data:
            student, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first,
                    'last_name': last
                }
            )
            if created:
                student.set_password('password123')
                student.save()
                profile, _ = Profile.objects.get_or_create(user=student)
                profile.is_teacher = False
                profile.save()
                self.stdout.write(self.style.SUCCESS(f'✓ Created student: {student.username}'))
            else:
                self.stdout.write(f'  Student {student.username} already exists')
            students.append(student)
        
        # Create classrooms
        self.stdout.write('\nCreating classrooms...')
        
        classroom_data = [
            ('CS101 - Introduction to Computer Science', 'Learn the fundamentals of programming and computer science'),
        ]
        
        classrooms = []
        for name, desc in classroom_data:
            classroom, created = Classroom.objects.get_or_create(
                name=name,
                defaults={
                    'teacher': teacher,
                    'description': desc
                }
            )
            if created:
                # Add students to classroom
                classroom.students.add(*students)
                self.stdout.write(self.style.SUCCESS(f'✓ Created classroom: {classroom.name}'))
            else:
                self.stdout.write(f'  Classroom {classroom.name} already exists')
            classrooms.append(classroom)
        
        # Create lectures
        self.stdout.write('\nCreating lectures...')
        
        lecture_data = [
            ('Introduction to Python', 'https://www.youtube.com/watch?v=kqtD5dpn9C8'),
            ('Variables and Data Types', 'https://www.youtube.com/watch?v=Z1Yd7upQsXY'),
            ('Control Flow', 'https://www.youtube.com/watch?v=PqFKRqpHrjw'),
            ('Functions in Python', 'https://www.youtube.com/watch?v=NSbOtYzIQI0'),
            ('Object-Oriented Programming', 'https://www.youtube.com/watch?v=JeznW_7DlB0'),
        ]
        
        for classroom in classrooms:
            for title, url in lecture_data:
                lecture, created = Lecture.objects.get_or_create(
                    classroom=classroom,
                    title=title,
                    defaults={
                        'youtube_link': url
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Created lecture: {title}'))
                    
                    # Add some comments to lectures
                    if students:
                        LectureComment.objects.get_or_create(
                            lecture=lecture,
                            author=students[0],
                            defaults={'content': 'Great lecture! Very informative.'}
                        )
        
        # Create notices
        self.stdout.write('\nCreating notices...')
        
        notice_data = [
            ('Welcome to the Classroom!', 'Welcome everyone! Looking forward to a great semester. Please check the lectures and complete the assignments on time.'),
            ('Assignment Due Dates', 'All assignments are due by the end of each week. Please submit on time to receive full credit.'),
            ('Office Hours Available', 'I am available for questions during office hours. Feel free to reach out if you need help!'),
        ]
        
        for classroom in classrooms:
            for title, content in notice_data:
                notice, created = Notice.objects.get_or_create(
                    classroom=classroom,
                    title=title,
                    defaults={
                        'content': content,
                        'author': teacher
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Created notice: {title}'))
        
        # Create assignments
        self.stdout.write('\nCreating assignments...')
        
        assignment_data = [
            {
                'title': 'Python Basics Quiz',
                'questions': [
                    {
                        'text': 'What is the correct way to print "Hello World" in Python?',
                        'choices': [
                            ('print("Hello World")', True),
                            ('echo "Hello World"', False),
                            ('console.log("Hello World")', False),
                            ('printf("Hello World")', False),
                        ]
                    },
                    {
                        'text': 'Which data type is used for decimal numbers in Python?',
                        'choices': [
                            ('int', False),
                            ('float', True),
                            ('string', False),
                            ('decimal', False),
                        ]
                    },
                    {
                        'text': 'What keyword is used to create a function in Python?',
                        'choices': [
                            ('function', False),
                            ('def', True),
                            ('func', False),
                            ('define', False),
                        ]
                    },
                ]
            },
            {
                'title': 'Control Flow Quiz',
                'questions': [
                    {
                        'text': 'Which keyword is used for conditional statements in Python?',
                        'choices': [
                            ('if', True),
                            ('when', False),
                            ('case', False),
                            ('switch', False),
                        ]
                    },
                    {
                        'text': 'What does a for loop do?',
                        'choices': [
                            ('Performs an action once', False),
                            ('Iterates over a sequence', True),
                            ('Creates a function', False),
                            ('Defines a variable', False),
                        ]
                    },
                    {
                        'text': 'How do you create a list in Python?',
                        'choices': [
                            ('list = ()', False),
                            ('list = []', True),
                            ('list = {}', False),
                            ('list = ""', False),
                        ]
                    },
                ]
            },
            {
                'title': 'Python Data Structures',
                'questions': [
                    {
                        'text': 'Which data structure uses key-value pairs?',
                        'choices': [
                            ('List', False),
                            ('Tuple', False),
                            ('Dictionary', True),
                            ('Set', False),
                        ]
                    },
                    {
                        'text': 'What is the difference between a list and a tuple?',
                        'choices': [
                            ('Lists are immutable', False),
                            ('Tuples are mutable', False),
                            ('Tuples are immutable', True),
                            ('No difference', False),
                        ]
                    },
                ]
            },
        ]
        
        for classroom in classrooms:
            for assign_info in assignment_data:
                assignment, created = Assignment.objects.get_or_create(
                    classroom=classroom,
                    title=assign_info['title'],
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Created assignment: {assign_info["title"]}'))
                    
                    # Create questions and choices
                    for q_data in assign_info['questions']:
                        question = Question.objects.create(
                            assignment=assignment,
                            text=q_data['text']
                        )
                        
                        for choice_text, is_correct in q_data['choices']:
                            Choice.objects.create(
                                question=question,
                                text=choice_text,
                                is_correct=is_correct
                            )
                    
                    # Create a sample submission from first student
                    if students:
                        submission = Submission.objects.create(
                            assignment=assignment,
                            student=students[0],
                            score=0
                        )
                        
                        score = 0
                        for question in assignment.questions.all():
                            # Randomly pick an answer (first choice for demo)
                            choice = question.choices.first()
                            if choice:
                                StudentAnswer.objects.create(
                                    submission=submission,
                                    question=question,
                                    choice=choice
                                )
                                if choice.is_correct:
                                    score += 1
                        
                        submission.score = score
                        submission.teacher_feedback = "Good effort! Keep practicing."
                        submission.save()
                        
                        self.stdout.write(f'    ✓ Created sample submission for {students[0].username}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Dummy data creation complete!'))
        self.stdout.write(self.style.SUCCESS('\nLogin credentials:'))
        self.stdout.write('  Teacher: username=teacher1, password=password123')
        self.stdout.write('  Student: username=student1, password=password123')
        self.stdout.write('  Student: username=student2, password=password123')
        self.stdout.write('  Student: username=student3, password=password123')
