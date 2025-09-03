from django.urls import path
from exams.views import *

urlpatterns = [
    path('student/dashboard/', student_dashboard , name='student_dashboard'),
    path('admin/dashboard/', admin_dashboard , name='admin_dashboard'),
    path('data/', admin_dashboard_data , name='admin_dashboard_data'),

    path('start/<int:exam_id>/', start_exam, name='start_exam'),
    path('exam/<int:session_id>/<int:q_no>/', exam_question, name='exam_question'),
    path('finish/<int:session_id>/', exam_finish, name='exam_finish'),

]