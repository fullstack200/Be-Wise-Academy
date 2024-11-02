from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Resources)
admin.site.register(Syllabus)
admin.site.register(Fee)
admin.site.register(Quiz)
admin.site.register(mathQuizResult)
admin.site.register(scienceQuizResult)
admin.site.register(Blogs)