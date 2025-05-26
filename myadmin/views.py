from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .services.admin_services import AdminService
from .form import BookForm
# from .models import Book, Loan, User
from accounts.models import User
from library.models import Book, Loan

# Create your views here.
admin_service = AdminService()

# 관리자만 접근 가능하게
def is_admin(user):
    return user.is_authenticated and user.is_admin

# 관리자 대쉬보드
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    return render(request, 'myadmin/admin_dashboard.html')

# 책 관리
@login_required
@user_passes_test(is_admin)
def book_list(request):
    books = Book.objects.all()
    return render(request, 'myadmin/book_list.html', {'books': books})

@login_required
@user_passes_test(is_admin)
def new_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            admin_service.new_book(
                title=form.cleaned_data['title'],
                author=form.cleaned_data['author']
            )
            return redirect('myadmin:admin_dashboard')
    else:
        form = BookForm()
    return render(request, 'myadmin/new_book.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def edit_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            admin_service.edit_book(
                bookID=book_id,
                title=form.cleaned_data['title'],
                author=form.cleaned_data['author']
            )
            return redirect('myadmin:admin_dashboard')
    else:
        form = BookForm(instance=book)
    return render(request, 'myadmin/edit_book.html', {'form': form, 'book': book})

@login_required
@user_passes_test(is_admin)
def delete_book(request, book_id):
    try:
        admin_service.delete_book(book_id)
    except Exception as e:
        return render(request, 'myadmin/book_list.html', {'error': str(e)})
    return redirect('myadmin:admin_dashboard')


# 대출 관리
@login_required
@user_passes_test(is_admin)
def loan_list(request):
    loans = Loan.objects.all()
    return render(request, 'myadmin/loan_list.html', {'loans': loans})

@login_required
@user_passes_test(is_admin)
def extend_loan(request, loan_id):
    admin_service.manage_loan(loan_id)
    return redirect('myadmin:admin_dashboard')


# 연체 사용자 관리
@login_required
@user_passes_test(is_admin)
def manage_overdue(request):
    overdue_users = User.objects.filter(loan__is_overdue=True).distinct()
    return render(request, 'myadmin/manage_overdue.html', {'users': overdue_users})

@login_required
@user_passes_test(is_admin)
def impose_penalty(request, user_id):
    try:
        admin_service.impose_penalty(user_id)
    except Exception as e:
        return render(request, 'myadmin/manage_overdue.html', {'error': str(e)})
    return redirect('myadmin:admin_dashboard')

@login_required
@user_passes_test(is_admin)
def release_penalty(request, user_id):
    try:
        admin_service.release_penalty(user_id)
    except Exception as e:
        return render(request, 'myadmin/manage_overdue.html', {'error': str(e)})
    return redirect('myadmin:admin_dashboard')
