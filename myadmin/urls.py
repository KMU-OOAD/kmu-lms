from django.urls import path
from .views import (
    AdminDashboardView, BookListView, BookCreateView, BookUpdateView, BookDeleteView,
    LoanListView, ExtendLoanView, ManageOverdueView, ImposePenaltyView, ReleasePenaltyView
)

app_name = 'myadmin'

urlpatterns = [
    path('', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('books/', BookListView.as_view(), name='book_list'),
    path('books/new/', BookCreateView.as_view(), name='new_book'),
    path('books/edit/<int:book_id>/', BookUpdateView.as_view(), name='edit_book'),
    path('books/delete/<int:book_id>/', BookDeleteView.as_view(), name='delete_book'),
    path('loans/', LoanListView.as_view(), name='loan_list'),
    path('loans/extend/<int:loan_id>/', ExtendLoanView.as_view(), name='extend_loan'),
    path('overdue/', ManageOverdueView.as_view(), name='manage_overdue'),
    path('overdue/impose/<int:user_id>/', ImposePenaltyView.as_view(), name='impose_penalty'),
    path('overdue/release/<int:user_id>/', ReleasePenaltyView.as_view(), name='release_penalty'),
]
