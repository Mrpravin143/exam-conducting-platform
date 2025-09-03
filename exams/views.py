from django.shortcuts import render, redirect , get_object_or_404
from exams.models import *
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
import uuid
import datetime
from django.db.models import Avg, Count, Max, Min, Sum




def is_admin(user):
    return getattr(user, "role", None) == "admin"


@login_required
def student_dashboard(request):
    # Upcoming exams (today onwards)
    now = timezone.now()
    exams = Exam.objects.filter(exam_date__gte=now).order_by('exam_date')
    return render(request, "student_dashboard.html", {"NewExam": exams})


def admin_dashboard(request):
    exams = Exam.objects.all().order_by('-exam_date')

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        exam_date = request.POST.get("exam_date")
        duration_minutes = request.POST.get("duration_minutes")

        if title and exam_date:
            Exam.objects.create(
                title=title,
                description=description,
                exam_date=exam_date,
                duration_minutes=duration_minutes
            )
            messages.success(request, f"Exam '{title}' created successfully!")
            return redirect('admin_exam_create')
        else:
            messages.error(request, "Title and Exam Date are required!")

    return render(request, 'admin_dashboard.html', {"exams": exams})
    

    exam = get_object_or_404(Exam, pk=pk)
    exam.delete()
    messages.success(request, f"Exam '{exam.title}' deleted successfully!")
    return redirect('admin_dashboard')


def start_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    # Create session if not exists
    session, created = StudentExamSession.objects.get_or_create(
        student=request.user,
        exam=exam,
    )

    # Total duration in seconds
    duration_seconds = exam.duration_minutes * 60
    return render(request, "start_exam.html", {
        "exam": exam,
        "session": session,
        "duration_seconds": duration_seconds,
    })


def exam_question(request, session_id, q_no):
    session = get_object_or_404(StudentExamSession, id=session_id)
    questions = session.exam.questions.all()
    total_qs = questions.count()

    # Start question number should be at least 1
    if q_no < 1:
        q_no = 1

    # All questions answered
    if q_no > total_qs:
        return redirect("exam_finish", session_id=session.id)

    question = questions[q_no - 1]

    # Set start_time if not already set
    if not session.start_time:
        session.start_time = timezone.now()
        session.save()

    # Calculate remaining exam time (seconds)
    exam_start_time = session.start_time
    duration_minutes = session.exam.duration_minutes
    end_time = exam_start_time + datetime.timedelta(minutes=duration_minutes)
    now = timezone.now()
    remaining_seconds = int((end_time - now).total_seconds())

    # If time over, redirect to finish
    if remaining_seconds <= 0:
        return redirect("exam_finish", session_id=session.id)

    if request.method == "POST":
        answer_text = request.POST.get("answer_text", "")
        selected_option = request.POST.get("selected_option", "")
        marks_obtained = 0

        # MCQ logic
        if question.question_type == "MCQ" and selected_option:
            if selected_option.strip() == question.correct_answer.strip():
                marks_obtained = question.marks

        # Save or update student answer
        StudentAnswer.objects.update_or_create(
            session=session,
            question=question,
            defaults={
                "answer_text": answer_text,
                "selected_option": selected_option,
                "marks_obtained": marks_obtained
            }
        )

        # Redirect to next question
        return redirect("exam_question", session_id=session.id, q_no=q_no + 1)

    return render(request, "exam_question.html", {
        "session": session,
        "question": question,
        "q_no": q_no,
        "total_qs": total_qs,
        "remaining_seconds": remaining_seconds
    })


def exam_finish(request, session_id):
    session = get_object_or_404(StudentExamSession, id=session_id)
    session.is_submitted = True
    session.save()
    return render(request, "exam_finish.html", {"session": session})



def admin_dashboard_data(request):
    total_exams = Exam.objects.count()
    total_students = StudentExamSession.objects.values("student").distinct().count()
    total_sessions = StudentExamSession.objects.count()
    submitted_sessions = StudentExamSession.objects.filter(is_submitted=True).count()

    # Exams Stats
    exams_stats = Exam.objects.annotate(
        total_students=Count("studentexamsession"),
        submitted=Count("studentexamsession", filter=models.Q(studentexamsession__is_submitted=True)),
        avg_marks=Avg("studentexamsession__studentanswer__marks_obtained"),
        max_marks=Max("studentexamsession__studentanswer__marks_obtained"),
        min_marks=Min("studentexamsession__studentanswer__marks_obtained"),
    )

    # Question stats
    total_questions = Question.objects.count()
    mcq_count = Question.objects.filter(question_type="MCQ").count()
    desc_count = Question.objects.filter(question_type="DESC").count()

    context = {
        "total_exams": total_exams,
        "total_students": total_students,
        "total_sessions": total_sessions,
        "submitted_sessions": submitted_sessions,
        "submission_rate": (submitted_sessions / total_sessions * 100) if total_sessions else 0,
        "exams_stats": exams_stats,
        "total_questions": total_questions,
        "mcq_count": mcq_count,
        "desc_count": desc_count,
    }
    return render(request, "admin_data.html", context)













