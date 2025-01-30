from django.urls import path
from .views import *


urlpatterns = [
    path('price/', feeView, name='price'),
    path('resources/mathematics', mathematicsView, name='mathematics'),
    path('resources/physics', physicsView, name='physics'),
    path('resources/chemistry', chemistryView, name='chemistry'),
    path('evaluation/math',mathQuizView.as_view(),name='mathQ'),
    path('evaluation/science',scienceQuizView.as_view(),name='scienceQ'),
    path('evaluation/mathresult',mathResultView,name='mathresult'),
    path('evaluation/scienceresult',scienceResultView,name='scienceresult'),   
    path('evaluation/math/test-review', mathQuestionsReview, name='math-test-review'),
    path('evaluation/science/test-review',scienceQuestionsReview, name='science-test-review'),
    path('blogs',BlogListView.as_view(),name='blogList'),
    path('blog/<uuid:bid>',blogDetailView ,name='blogDetail'),
]
