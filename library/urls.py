from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.search_books, name='search_books'),
    path('reserve/<int:book_id>/', views.reserve_book, name='reserve_book'),
    path('borrow/<int:book_id>/', views.borrow_book, name='borrow_book'),
    path('return/<int:loan_id>/', views.return_book, name='return_book'),
    path('history/', views.loan_history, name='loan_history'),
]
