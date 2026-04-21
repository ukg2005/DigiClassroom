from datetime import timedelta
import random
import time

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import OperationalError, close_old_connections, connection
from django.utils import timezone

from classrooms.models import Classroom
from lectures.models import Lecture, LectureComment
from notices.models import Notice, NoticeComment
from assignments.models import Assignment, Question, Choice, Submission, StudentAnswer
from users.models import Profile


class Command(BaseCommand):
    help = 'Creates realistic semester-based dummy data for demo presentation'

    DUMMY_PASSWORD = 'demo12345'

    SUBJECTS_BY_SEMESTER = {
        1: [
            ('CS1101', 'Engineering Mathematics I'),
            ('CS1102', 'Green Chemistry'),
            ('CS1103', 'English'),
            ('CS1104', 'Computer Programming Using C'),
            ('CS1105', 'IT Essentials'),
        ],
        2: [
            ('CS1201', 'Engineering Mathematics II'),
            ('CS1202', 'Engineering Physics'),
            ('CS1203', 'Elements of Electronics Engineering'),
            ('CS1204', 'Data Structures Using C'),
            ('CS1205', 'Digital Logic Design'),
        ],
        3: [
            ('CS2101', 'Discrete Mathematical Structures'),
            ('CS2102', 'Computer Organization and Architecture'),
            ('CS2103', 'Probability, Statistics and Queuing Theory'),
            ('CS2104', 'Operating Systems'),
            ('CS2105', 'Object Oriented Programming Through Java'),
            ('CS2109', 'Intellectual Property Rights'),
            ('CS2110', 'Environmental Science'),
        ],
        4: [
            ('CS2201', 'Microprocessors'),
            ('CS2202', 'Design and Analysis of Algorithms'),
            ('CS2203', 'Database Management Systems'),
            ('CS2204', 'Formal Languages & Automata Theory'),
            ('CS2205', 'Managerial Economics'),
            ('CS2208', 'Web Technologies'),
            ('CS2209', 'Professional Ethics & Universal Human Values'),
        ],
        5: [
            ('CS3101', 'Data Communication and Computer Networks'),
            ('CS3102', 'Compiler Design'),
            ('CS3103', 'Artificial Intelligence'),
            ('CS3104', 'Data Warehousing and Data Mining'),
            ('CS3105', 'Python Programming'),
        ],
        6: [
            ('CS3201', 'Object Oriented Software Engineering'),
            ('CS3202', 'Machine Learning'),
            ('CS3203', 'Cryptography & Network Security'),
            ('CS3204', 'Sensor Networks'),
            ('CS3205', 'Embedded Systems'),
        ],
    }

    REAL_TEACHER_USERNAMES = [
        ('rajeshkumar', 'Rajesh', 'Kumar'),
        ('priyavenkataraman', 'Priya', 'Venkataraman'),
        ('sureshnaidu', 'Suresh', 'Naidu'),
        ('anithareddy', 'Anitha', 'Reddy'),
    ]

    REAL_STUDENT_USERNAMES = [
        ('udaykiran', 'Uday', 'Kiran'),
        ('karthik', 'Karthik', ''),
        ('sarathchandra', 'Sarath', 'Chandra'),
        ('varunkalidindi', 'Varun', 'Kalidindi'),
        ('sudharshanpaul', 'Sudharshan', 'Paul'),
    ]

    EXTRA_TEACHER_NAMES = [
        ('teacher05', 'Aparna', 'Iyer'),
        ('teacher06', 'Vikram', 'Rao'),
        ('teacher07', 'Nikhil', 'Mehta'),
        ('teacher08', 'Keerthi', 'Menon'),
        ('teacher09', 'Harish', 'Patel'),
        ('teacher10', 'Meghana', 'Sharma'),
        ('teacher11', 'Ravi', 'Teja'),
        ('teacher12', 'Divya', 'Srinivas'),
        ('teacher13', 'Arjun', 'Bose'),
    ]

    NOTICE_TEMPLATES = [
        ('Class Schedule Update', 'Please note the revised class timing for this week. Check timetable and LMS calendar.'),
        ('Assignment Reminder', 'Complete the latest assignment before the due date. Late submissions may incur penalty.'),
        ('Lab Session Instructions', 'Carry your lab notebook and complete pre-lab preparation before session starts.'),
        ('Assessment Update', 'A short quiz will be conducted in the upcoming class based on recent topics.'),
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            '--dummy-students',
            type=int,
            default=100,
            help='Number of additional dummy students to create (default: 100)',
        )

    def handle(self, *args, **options):
        rng = random.Random(20260421)
        dummy_student_count = max(0, int(options['dummy_students']))

        self.stdout.write(self.style.WARNING('Creating realistic semester-based dummy data...'))
        self._configure_sqlite_busy_timeout()

        teachers = self._run_with_retry(self._create_teachers, 'Create teachers')
        students_by_sem = self._run_with_retry(lambda: self._create_students(dummy_student_count), 'Create students')
        classrooms_by_sem = self._run_with_retry(lambda: self._create_classrooms(teachers), 'Create classrooms')
        self._run_with_retry(lambda: self._enroll_students(students_by_sem, classrooms_by_sem), 'Enroll students')
        self._run_with_retry(lambda: self._populate_content(classrooms_by_sem, students_by_sem, rng), 'Populate classroom content')

        self.stdout.write(self.style.SUCCESS('\nData generation complete.'))
        self.stdout.write(self.style.SUCCESS(f'Dummy password for generated teacher/student accounts: {self.DUMMY_PASSWORD}'))
        self.stdout.write('Real teacher usernames: rajeshkumar, priyavenkataraman, sureshnaidu, anithareddy')
        self.stdout.write('Real student usernames: udaykiran, karthik, sarathchandra, varunkalidindi, sudharshanpaul')

    def _configure_sqlite_busy_timeout(self):
        if connection.vendor != 'sqlite':
            return
        with connection.cursor() as cursor:
            cursor.execute('PRAGMA busy_timeout = 30000')

    def _run_with_retry(self, func, label, retries=4, base_delay=0.7):
        for attempt in range(1, retries + 1):
            try:
                return func()
            except OperationalError as exc:
                is_locked = 'database is locked' in str(exc).lower()
                if not is_locked or attempt == retries:
                    raise

                wait_seconds = base_delay * attempt
                self.stdout.write(
                    self.style.WARNING(
                        f'{label}: SQLite database is locked. Retrying in {wait_seconds:.1f}s '
                        f'(attempt {attempt}/{retries})...'
                    )
                )
                close_old_connections()
                time.sleep(wait_seconds)

    def _ensure_profile(self, user, is_teacher):
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.is_teacher = is_teacher
        if user.is_superuser:
            profile.is_admin = True
        profile.save(update_fields=['is_teacher', 'is_admin', 'roll_no'])
        return profile

    def _create_teachers(self):
        teachers = []
        teacher_specs = self.REAL_TEACHER_USERNAMES + self.EXTRA_TEACHER_NAMES
        for username, first_name, last_name in teacher_specs:
            email = f'{username}@demo.college.edu'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                },
            )
            if created:
                user.set_password(self.DUMMY_PASSWORD)
            else:
                user.email = user.email or email
                user.first_name = user.first_name or first_name
                user.last_name = user.last_name or last_name
            user.save()
            self._ensure_profile(user, is_teacher=True)
            teachers.append(user)
        self.stdout.write(self.style.SUCCESS(f'Created/updated {len(teachers)} teachers.'))
        return teachers

    def _create_students(self, dummy_student_count):
        students_by_sem = {sem: [] for sem in self.SUBJECTS_BY_SEMESTER.keys()}

        # Place real students into final semesters for live demo value.
        real_sem_map = [5, 5, 6, 6, 6]
        for (username, first_name, last_name), semester in zip(self.REAL_STUDENT_USERNAMES, real_sem_map):
            email = f'{username}@demo.college.edu'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                },
            )
            if created:
                user.set_password(self.DUMMY_PASSWORD)
            else:
                user.email = user.email or email
                user.first_name = user.first_name or first_name
                user.last_name = user.last_name or last_name
            user.save()
            profile = self._ensure_profile(user, is_teacher=False)
            if not profile.roll_no:
                profile.roll_no = ''
                profile.save(update_fields=['roll_no'])
            students_by_sem[semester].append(user)

        sem_list = sorted(self.SUBJECTS_BY_SEMESTER.keys())
        for idx in range(dummy_student_count):
            semester = sem_list[idx % len(sem_list)]
            username = f'student{idx + 1:03d}'
            first_name = f'Student{idx + 1:03d}'
            last_name = 'Demo'
            email = f'{username}@demo.college.edu'
            roll_no = f'CS{semester}{(idx + 1):03d}'

            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                },
            )
            if created:
                user.set_password(self.DUMMY_PASSWORD)
            else:
                user.email = user.email or email
                user.first_name = user.first_name or first_name
                user.last_name = user.last_name or last_name
            user.save()
            profile = self._ensure_profile(user, is_teacher=False)
            if not profile.roll_no:
                profile.roll_no = roll_no
                profile.save(update_fields=['roll_no'])

            students_by_sem[semester].append(user)

        total = sum(len(v) for v in students_by_sem.values())
        self.stdout.write(self.style.SUCCESS(f'Created/updated {total} students across semesters.'))
        return students_by_sem

    def _create_classrooms(self, teachers):
        classrooms_by_sem = {sem: [] for sem in self.SUBJECTS_BY_SEMESTER.keys()}
        weighted_teacher_indices = [0, 0, 1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 0, 1, 2, 3]
        pick = 0

        for semester, subjects in self.SUBJECTS_BY_SEMESTER.items():
            for code, title in subjects:
                teacher = teachers[weighted_teacher_indices[pick % len(weighted_teacher_indices)]]
                pick += 1
                name = f'{code} - {title}'
                description = f'{title} for semester {semester}. Includes lectures, assessments, and class discussions.'

                classroom, created = Classroom.objects.get_or_create(
                    name=name,
                    defaults={
                        'teacher': teacher,
                        'created_by': teacher,
                        'description': description,
                    },
                )
                if not created:
                    classroom.teacher = teacher
                    classroom.created_by = classroom.created_by or teacher
                    classroom.description = description
                    classroom.save(update_fields=['teacher', 'created_by', 'description'])

                classroom.teachers.add(teacher)
                classrooms_by_sem[semester].append(classroom)

        self.stdout.write(self.style.SUCCESS('Created/updated classrooms for all semester subjects.'))
        return classrooms_by_sem

    def _enroll_students(self, students_by_sem, classrooms_by_sem):
        for semester, students in students_by_sem.items():
            semester_classrooms = classrooms_by_sem[semester]
            for classroom in semester_classrooms:
                classroom.students.add(*students)
        self.stdout.write(self.style.SUCCESS('Enrolled students only in their semester subjects.'))

    def _youtube_search_link(self, code, title):
        query = f'{code} {title} full course lecture'
        return 'https://www.youtube.com/results?search_query=' + query.replace(' ', '+')

    def _make_quiz_question_bank(self, code, title):
        return [
            {
                'text': f'Which topic is central to {title}?',
                'choices': [
                    ('Core foundational concepts', True),
                    ('Only historical timelines', False),
                    ('Only hardware repair', False),
                    ('Only UI styling', False),
                ],
            },
            {
                'text': f'In {code}, what is most important for scoring well?',
                'choices': [
                    ('Consistent practice and revision', True),
                    ('Skipping problem-solving', False),
                    ('Memorizing without understanding', False),
                    ('Ignoring class exercises', False),
                ],
            },
            {
                'text': f'Which is a good strategy while preparing {title}?',
                'choices': [
                    ('Solve previous and model questions', True),
                    ('Study only one unit', False),
                    ('Avoid notes and examples', False),
                    ('Skip feedback from instructor', False),
                ],
            },
            {
                'text': f'{code}: select the best classroom practice.',
                'choices': [
                    ('Attend lectures and submit on time', True),
                    ('Submit after deadlines always', False),
                    ('Ignore assignments', False),
                    ('Avoid practical work', False),
                ],
            },
        ]

    def _make_qna_prompts(self, code, title):
        return [
            f'Explain one important concept from {title} in your own words with an example.',
            f'Compare two subtopics you learned in {code} and discuss where each is useful.',
            f'Describe a real-world application of {title} and mention implementation challenges.',
        ]

    def _create_assignments_for_classroom(self, classroom, code, title, rng):
        now = timezone.now()
        assignments = []

        quiz_assignment, _ = Assignment.objects.get_or_create(
            classroom=classroom,
            title=f'{code} Unit Quiz 1',
            defaults={
                'assignment_type': Assignment.ASSIGNMENT_TYPE_QUIZ,
                'prompt': f'Quiz assessment for {title}.',
                'due_date': now + timedelta(days=7),
                'late_submission_policy': Assignment.LATE_POLICY_PENALTY,
                'late_penalty_percent': 10,
                'max_attempts': 2,
            },
        )
        if quiz_assignment.questions.count() == 0:
            for q in self._make_quiz_question_bank(code, title):
                question = Question.objects.create(
                    assignment=quiz_assignment,
                    question_type=Question.QUESTION_TYPE_MCQ,
                    text=q['text'],
                    marks=1,
                )
                for text, correct in q['choices']:
                    Choice.objects.create(question=question, text=text, is_correct=correct)
        assignments.append(quiz_assignment)

        qna_assignment, _ = Assignment.objects.get_or_create(
            classroom=classroom,
            title=f'{code} Conceptual Q&A 1',
            defaults={
                'assignment_type': Assignment.ASSIGNMENT_TYPE_QNA,
                'prompt': f'Written assessment for {title}.',
                'due_date': now + timedelta(days=10),
                'late_submission_policy': Assignment.LATE_POLICY_ALLOW,
                'max_attempts': 1,
            },
        )
        if qna_assignment.questions.count() == 0:
            for prompt in self._make_qna_prompts(code, title):
                Question.objects.create(
                    assignment=qna_assignment,
                    question_type=Question.QUESTION_TYPE_QNA,
                    text=prompt,
                    marks=rng.choice([5, 6, 8]),
                )
        assignments.append(qna_assignment)

        return assignments

    def _populate_content(self, classrooms_by_sem, students_by_sem, rng):
        for semester, classrooms in classrooms_by_sem.items():
            students = students_by_sem[semester]
            sample_students = students[: min(len(students), 20)]

            for classroom in classrooms:
                code, title = classroom.name.split(' - ', 1)

                lecture_topics = [
                    f'Introduction to {title}',
                    f'{title} - Core Concepts',
                    f'{title} - Problem Solving Session',
                    f'{title} - Exam Strategy and Revision',
                ]
                for topic in lecture_topics:
                    lecture, _ = Lecture.objects.get_or_create(
                        classroom=classroom,
                        title=topic,
                        defaults={'youtube_link': self._youtube_search_link(code, title)},
                    )
                    if sample_students:
                        LectureComment.objects.get_or_create(
                            lecture=lecture,
                            author=sample_students[0],
                            content='Thank you, this session helped me understand the topic better.',
                        )

                for notice_title, notice_body in self.NOTICE_TEMPLATES[:3]:
                    notice, _ = Notice.objects.get_or_create(
                        classroom=classroom,
                        title=f'{code}: {notice_title}',
                        defaults={
                            'content': notice_body,
                            'author': classroom.teacher,
                        },
                    )
                    if len(sample_students) > 1:
                        NoticeComment.objects.get_or_create(
                            notice=notice,
                            author=sample_students[1],
                            content='Acknowledged, thank you for the update.',
                        )

                assignments = self._create_assignments_for_classroom(classroom, code, title, rng)
                self._create_sample_submissions(assignments, sample_students, rng)

        self.stdout.write(self.style.SUCCESS('Created lectures, notices, assignments, and submissions.'))

    def _create_sample_submissions(self, assignments, students, rng):
        if not students:
            return

        for assignment in assignments:
            selected_students = students[: max(6, len(students) // 2)]
            for student in selected_students:
                if Submission.objects.filter(assignment=assignment, student=student).exists():
                    continue

                submission = Submission.objects.create(
                    assignment=assignment,
                    student=student,
                    attempt_number=1,
                    is_late=(rng.random() < 0.18),
                )

                if assignment.is_quiz:
                    score = 0
                    for question in assignment.questions.filter(question_type=Question.QUESTION_TYPE_MCQ).prefetch_related('choices'):
                        choices = list(question.choices.all())
                        if not choices:
                            continue
                        chosen = rng.choice(choices)
                        StudentAnswer.objects.create(submission=submission, question=question, choice=chosen)
                        if chosen.is_correct:
                            score += question.marks
                    submission.score = score
                    submission.teacher_feedback = 'Quiz evaluated automatically. Revise weak areas and retry practice questions.'
                    submission.graded_at = timezone.now()
                    submission.save(update_fields=['score', 'teacher_feedback', 'graded_at'])
                else:
                    total = 0
                    for question in assignment.questions.filter(question_type=Question.QUESTION_TYPE_QNA):
                        text = (
                            f'This answer explains key ideas from {assignment.title} and includes one practical application. '
                            'Further detail can be added with diagrams and examples.'
                        )
                        ans = StudentAnswer.objects.create(
                            submission=submission,
                            question=question,
                            text_response=text,
                        )

                        # Grade most Q&A submissions; leave some pending for realistic workflow.
                        if rng.random() < 0.7:
                            awarded = max(0, question.marks - rng.choice([0, 1, 2]))
                            ans.awarded_marks = awarded
                            ans.teacher_feedback = 'Good attempt. Improve structure and add one more concrete example.'
                            ans.save(update_fields=['awarded_marks', 'teacher_feedback'])
                            total += awarded

                    if total > 0:
                        submission.score = total
                        submission.teacher_feedback = 'Overall decent response quality. Focus on precision and examples.'
                        submission.graded_at = timezone.now()
                        submission.save(update_fields=['score', 'teacher_feedback', 'graded_at'])
