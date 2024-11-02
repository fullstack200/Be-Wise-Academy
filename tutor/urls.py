from django.urls import path
from .views import *


urlpatterns = [
    path('resources/mathematics', mathematicsView, name='mathematics'),
    path('resources/physics', physicsView, name='physics'),
    path('resources/chemistry', chemistryView, name='chemistry'),
    path('resources/biology',biologyView , name='biology'),
    path('resources/computerScience', computerScienceView, name='computerScience'),
    path('resources/english', englishView, name='english'),
    path('resources/hindi', hindiView, name='hindi'),
    path('evaluation/math',mathQuizView.as_view(),name='mathQ'),
    path('evaluation/science',scienceQuizView.as_view(),name='scienceQ'),
    path('evaluation/mathresult',mathResultView,name='mathresult'),
    path('evaluation/scienceresult',scienceResultView,name='scienceresult'),   
    path('evaluation/math/test-review', mathQuestionsReview, name='math-test-review'),
    path('evaluation/science/test-review',scienceQuestionsReview, name='science-test-review'),
    path('blogs',BlogListView.as_view(),name='blogList'),
    path('blog/<uuid:bid>',blogDetailView ,name='blogDetail'),
]
