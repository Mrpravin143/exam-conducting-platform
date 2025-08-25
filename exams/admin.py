from django.contrib import admin
from exams.models import *

# Register your models here.
@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    # Single datetime picker
    formfield_overrides = {
        models.DateTimeField: {'widget': admin.widgets.AdminSplitDateTime}, 
    }

admin.site.register(Question)
admin.site.register(StudentExamSession)
admin.site.register(StudentAnswer)





