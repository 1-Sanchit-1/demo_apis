from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PDFFileViewSet
from . import views


router = DefaultRouter()
router.register(r'pdfs', PDFFileViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('get_question_answers',views.get_question_answers,name='get_question_answers'),
    
]
