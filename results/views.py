from django.shortcuts import render
from django.db.models import Avg, Count, Max, Min, Sum
from exams.models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages



# Create your views here.



def results(request):
    exams = Exam.objects.all().order_by('-exam_date')
    selected_exam_id = request.GET.get("exam")
    selected_exam = None
    students_results = []

    if selected_exam_id:
        selected_exam = exams.filter(id=selected_exam_id).first()
        if selected_exam:
            sessions = StudentExamSession.objects.filter(exam=selected_exam)
            for s in sessions:
                total_marks = StudentAnswer.objects.filter(session=s).aggregate(
                    total=Sum('marks_obtained')
                )['total'] or 0
                students_results.append({
                    "student": s.student,
                    "total_marks": total_marks
                })

            # Sort descending
            students_results = sorted(students_results, key=lambda x: x['total_marks'], reverse=True)

    return render(request, 'result.html', {
        "exams": exams,
        "students_results": students_results,
        "selected_exam": selected_exam
    })

