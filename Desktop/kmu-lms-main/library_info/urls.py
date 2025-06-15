from django.urls import path
from . import views

urlpatterns = [
    path('', views.library_info_list, name='library_info_list'),
    path('<str:day>/edit/', views.library_info_edit, name='library_info_edit'),
]
