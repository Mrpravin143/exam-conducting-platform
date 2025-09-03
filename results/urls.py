from django.urls import path
from results.views import *

urlpatterns = [

    path('student/results/',results,name='results'),

]