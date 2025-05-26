"""
URL configuration for lms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

app_name = 'myadmin'

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('books/', views.book_list, name='book_list'),
    path('books/new_book/', views.new_book, name='new_book'),
    path('books/<int:book_id>/edit/', views.edit_book, name='edit_book'),
    path('books/<int:book_id>/delete/', views.delete_book, name='delete_book'),
    path('loans/', views.loan_list, name='loan_list'),
    path('loans/<int:loan_id>/extend/', views.extend_loan, name='extend_loan'),
    path('overdue/', views.manage_overdue, name='manage_overdue'),
    path('overdue/<int:user_id>/penalty/', views.impose_penalty, name='impose_penalty'),
    path('overdue/<int:user_id>/release/', views.release_penalty, name='release_penalty'),
]
