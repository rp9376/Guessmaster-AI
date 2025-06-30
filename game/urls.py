from django.urls import path
from . import views

app_name = 'game'

urlpatterns = [
    path('', views.GameView.as_view(), name='home'),
    path('ask/', views.AskQuestionView.as_view(), name='ask'),
    path('reset/', views.ResetGameView.as_view(), name='reset'),
]
