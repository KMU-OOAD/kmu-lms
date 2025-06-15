from django.shortcuts import render, redirect, get_object_or_404
from .models import Book, Loan, Reservation
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from datetime import timedelta, date
from .forms import BookSearchForm
from django.db.models import Q

# 도서 검색
def search_books(request):
    form = BookSearchForm(request.GET or None)
    books = Book.objects.all()

    if form.is_valid():
        query = form.cleaned_data.get('query')
        if query:
            books = books.filter(
                Q(title__icontains=query) | Q(author__icontains=query)
            ).distinct()

    return render(request, 'library/book_search.html', {
        'form': form,
        'books': books
    })

# 도서 예약
@login_required
def reserve_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    # 이미 사용자가 해당 책을 예약했는지 확인
    existing_reservation = Reservation.objects.filter(bookID=book, userID=request.user, status='Pending').exists()
    if existing_reservation:
        # 메시지 전달 기능이 있다면 추가 (예: messages.warning(request, "이미 예약한 도서입니다."))
        pass # 일단 아무것도 안 함, 또는 에러 메시지 표시
    elif not book.available:
        # 책이 대출 불가능한 상태일 때만 예약 가능하도록 (선택적 로직)
        Reservation.objects.create(userID=request.user, bookID=book, status='Pending')
        # 메시지 전달 기능이 있다면 추가 (예: messages.success(request, "도서가 예약되었습니다."))
    else:
        # 책이 대출 가능한 경우 예약 불가 (선택적 로직)
        # 메시지 전달 기능이 있다면 추가 (예: messages.info(request, "대출 가능한 도서는 바로 대출해주세요."))
        pass
    return redirect('library:search_books') # 네임스페이스 사용

# 도서 대출
@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    user = request.user

    # 사용자가 대출 가능한 상태인지 확인 (예: accounts.User.status)
    if user.status != 'allowed':
        # messages.error(request, "현재 대출이 불가능한 상태입니다.")
        return redirect('library:search_books')

    # 이미 대출 중인 책인지 확인 (선택적: 한 사용자가 같은 책을 여러 권 대출하는 것을 막을 경우)
    # existing_loan = Loan.objects.filter(bookID=book, userID=user, return_date__isnull=True).exists()
    # if existing_loan:
    #     messages.warning(request, "이미 대출 중인 도서입니다.")
    #     return redirect('library:search_books')

    if book.available:
        Loan.objects.create(userID=user, bookID=book, due_date=date.today() + timedelta(days=14))
        book.available = False
        book.loan_count += 1
        book.save()
        # messages.success(request, f"'{book.title}' 도서가 대출되었습니다.")
        # 예약이 있었다면 해당 예약 상태 변경 (예: 'Fulfilled')
        reservation = Reservation.objects.filter(bookID=book, userID=user, status='Pending').first()
        if reservation:
            reservation.status = 'Fulfilled' # 또는 'Completed' 등
            reservation.save()
    else:
        # messages.warning(request, "이미 대출 중인 도서입니다.")
        pass # 이미 대출 중이므로 아무것도 안하거나 메시지 표시
    return redirect('library:loan_history')

# 도서 반납
@login_required
def return_book(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id, userID=request.user) # 본인의 대출만 반납 가능하도록
    book = loan.bookID

    if loan.return_date is None: # 아직 반납되지 않은 경우에만 처리
        loan.return_date = date.today()
        # 연체 여부 업데이트 (반납 시점 기준)
        # 이 로직은 is_overdue 필드의 의미에 따라 달라짐
        # 만약 is_overdue가 "현재 연체 중인가" 라면 False가 맞음.
        # 만약 "대출 기간 동안 연체된 적이 있는가" 라면 다른 로직 필요.
        # 여기서는 "현재 연체 중인가"의 의미로 False로 설정 가정.
        loan.is_overdue = False 
        loan.save()

        if book:
            book.available = True
            book.save()
            # messages.success(request, f"'{book.title}' 도서가 반납되었습니다.")

            # 해당 도서에 대한 다음 예약자 확인 및 처리
            next_reservation = Reservation.objects.filter(bookID=book, status='Pending').order_by('reservation_date').first()
            if next_reservation:
                # 다음 예약자에게 알림 (실제 알림 로직은 별도 구현 필요)
                # messages.info(next_reservation.userID, f"{book.title} 도서가 반납되어 대출 가능합니다.")
                # 예약 상태를 변경하거나, 특정 기간 동안 대출 우선권을 줄 수 있음 (예: status = 'Available')
                next_reservation.status = 'Notified' # 예시 상태
                next_reservation.save()
    else:
        # messages.warning(request, "이미 반납 처리된 대출입니다.")
        pass

    return redirect('library:loan_history')

# 대출 이력 조회
@login_required
def loan_history(request):
    loans = Loan.objects.filter(userID=request.user).order_by('-start_date')
    return render(request, 'library/loan_history.html', {
        'loans': loans,
        'date_today': date.today() # 템플릿에서 오늘 날짜 비교를 위해 추가
    })

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'library/register.html', {'form': form})

@login_required
def my_reservations(request):
    reservations = Reservation.objects.filter(userID=request.user).order_by('-reservation_date')
    return render(request, 'library/my_reservations.html', {
        'reservations': reservations
    })

def popular_books(request):
    books = Book.objects.order_by('-loan_count')[:10]  # 인기 Top 10
    return render(request, 'library/popular_books.html', {'books': books})