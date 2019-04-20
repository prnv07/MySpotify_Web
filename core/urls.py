from django.urls import path
from . import views

urlpatterns = [
    path('',views.UserNameView, name='enter_user'  ),
    path('username_enter/', views.ExecuteScript, name='script_exec'),
    path('show_stats/', views.ShowStats, name='show_stats')
]