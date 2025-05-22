from django.shortcuts import render, redirect, get_object_or_404
from .models import Book, Loan, Reservation
from django.contrib.auth.decorators import login_required
from datetime import timedelta, date

# 도서 검색
def search_books(request):
    query = request.GET.get('q')
    books = Book.objects.filter(title__icontains=query) if query else []
    return render(request, 'library/search.html', {'books': books})

# 도서 예약
@login_required
def reserve_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    Reservation.objects.create(user=request.user, book=book)
    return redirect('search_books')

# 도서 대출
@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    if book.available:
        Loan.objects.create(user=request.user, book=book, due_date=date.today() + timedelta(days=14))
        book.available = False
        book.save()
    return redirect('loan_history')

# 도서 반납
@login_required
def return_book(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    loan.return_date = date.today()
    loan.book.available = True
    loan.book.save()
    loan.save()
    return redirect('loan_history')

# 대출 이력 조회
@login_required
def loan_history(request):
    loans = Loan.objects.filter(user=request.user).order_by('-start_date')
    return render(request, 'library/loan_history.html', {'loans': loans})
