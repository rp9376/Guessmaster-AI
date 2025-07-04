from django.urls import path
from . import views
from . import test_views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/ask/', views.ask_ai, name='ask_ai'),
    path('api/test-ollama/', test_views.test_ollama, name='test_ollama'),
]
