from django.shortcuts import render, redirect , get_object_or_404
from exams.models import *
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
import uuid
import datetime
from django.db.models import Sum




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
    selected_exam_id = request.GET.get("exam")  # filter by exam
    selected_exam = None  # new

    # Handle exam creation
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        exam_date = request.POST.get("exam_date")
        duration_minutes = request.POST.get("duration_minutes")

        Exam.objects.create(
            title=title,
            description=description,
            exam_date=exam_date,
            duration_minutes=duration_minutes
        )
        return redirect('admin_dashboard')

    # Students-wise results
    students_results = []
    top_students = []
    if selected_exam_id:
        selected_exam = exams.filter(id=selected_exam_id).first()  # template-friendly
        if selected_exam:
            sessions = StudentExamSession.objects.filter(exam=selected_exam)
            for s in sessions:
                total_marks = StudentAnswer.objects.filter(session=s).aggregate(total=Sum('marks_obtained'))['total'] or 0
                students_results.append({
                    "student": s.student,
                    "total_marks": total_marks
                })

            # Sort descending
            students_results = sorted(students_results, key=lambda x: x['total_marks'], reverse=True)
            top_students = students_results[:10]  # top 10

    return render(request, 'admin_dashboard.html', {
        "exams": exams,
        "students_results": students_results,
        "top_students": top_students,
        "selected_exam": selected_exam  # pass to template
    })



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













