from django.views import View
from django.views.generic import ListView, TemplateView
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, user_passes_test
from library.models import Book, Loan, User
from .form import BookForm
from .services.admin_services import AdminService

admin_service = AdminService()

# 공통 데코레이터
admin_required = [login_required, user_passes_test(lambda u: u.is_staff)]

# 관리자 대시보드
@method_decorator(admin_required, name='dispatch')
class AdminDashboardView(TemplateView):
    template_name = 'myadmin/admin_dashboard.html'

# 책 관리
@method_decorator(admin_required, name='dispatch')
class BookListView(ListView):
    model = Book
    template_name = 'myadmin/book_list.html'
    context_object_name = 'books'

@method_decorator(admin_required, name='dispatch')
class BookCreateView(View): # GRASP - Controller, Don’t Talk to Strangers, Low Coupling
    def get(self, request):
        form = BookForm()
        return render(request, 'myadmin/new_book.html', {'form': form})

    def post(self, request):
        form = BookForm(request.POST)
        if form.is_valid():
            admin_service.new_book(
                title=form.cleaned_data['title'],
                author=form.cleaned_data['author']
            )
            return redirect('myadmin:admin_dashboard')
        return render(request, 'myadmin/new_book.html', {'form': form})

@method_decorator(admin_required, name='dispatch')
class BookUpdateView(View): # GRASP - Controller, Don’t Talk to Strangers, Low Coupling
    def get(self, request, book_id):
        book = get_object_or_404(Book, pk=book_id)
        form = BookForm(instance=book)
        return render(request, 'myadmin/edit_book.html', {'form': form, 'book': book})

    def post(self, request, book_id):
        book = get_object_or_404(Book, pk=book_id)
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            admin_service.edit_book(
                bookID=book_id,
                title=form.cleaned_data['title'],
                author=form.cleaned_data['author']
            )
            return redirect('myadmin:admin_dashboard')
        return render(request, 'myadmin/edit_book.html', {'form': form, 'book': book})

@method_decorator(admin_required, name='dispatch')
class BookDeleteView(View): # GRASP - Controller, Don’t Talk to Strangers, Low Coupling
    def post(self, request, book_id):
        try:
            admin_service.delete_book(book_id)
        except Exception as e:
            books = Book.objects.all()
            return render(request, 'myadmin/book_list.html', {'error': str(e), 'books': books})
        return redirect('myadmin:admin_dashboard')

# 대출 관리
@method_decorator(admin_required, name='dispatch')
class LoanListView(ListView):
    model = Loan
    template_name = 'myadmin/loan_list.html'
    context_object_name = 'loans'

@method_decorator(admin_required, name='dispatch')
class ExtendLoanView(View): # GRASP - Controller, Don’t Talk to Strangers, Low Coupling
    def post(self, request, loan_id):
        admin_service.manage_loan(loan_id)
        return redirect('myadmin:admin_dashboard')

# 연체 사용자 관리
@method_decorator(admin_required, name='dispatch')
class ManageOverdueView(View):
    def get(self, request):
        overdue_users = User.objects.filter(loans__is_overdue=True).distinct()
        return render(request, 'myadmin/manage_overdue.html', {'users': overdue_users})

@method_decorator(admin_required, name='dispatch')
class ImposePenaltyView(View):
    def post(self, request, user_id):
        try:
            admin_service.impose_penalty(user_id)
        except Exception as e:
            overdue_users = User.objects.filter(loans__is_overdue=True).distinct()
            return render(request, 'myadmin/manage_overdue.html', {'error': str(e), 'users': overdue_users})
        return redirect('myadmin:admin_dashboard')

@method_decorator(admin_required, name='dispatch')
class ReleasePenaltyView(View):
    def post(self, request, user_id):
        try:
            admin_service.release_penalty(user_id)
        except Exception as e:
            overdue_users = User.objects.filter(loans__is_overdue=True).distinct()
            return render(request, 'myadmin/manage_overdue.html', {'error': str(e), 'users': overdue_users})
        return redirect('myadmin:admin_dashboard')
