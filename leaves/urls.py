from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add/', views.add_leave, name='add_leave'),
    path('edit/<int:pk>/', views.edit_leave, name='edit_leave'),
    path('log-login/', views.log_login, name='log_login'),
    path('login-history/', views.login_history, name='login_history'),
    path('login-history/<int:year>/<int:month>/', views.login_history, name='login_history_filtered'),
]
