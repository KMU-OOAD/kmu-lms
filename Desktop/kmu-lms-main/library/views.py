from django.shortcuts import render, redirect, get_object_or_404
from .models import Book, Loan, Reservation, Review, LoanNotification
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from datetime import timedelta, date
from .forms import BookSearchForm
from django.db.models import Q
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .services import (
    BookRecommendationService, ReviewService, NotificationService, 
    AdminService, LoanService
)
from .exceptions import *

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
        # 이미 예약한 경우
        pass
    else:
        # 예약 생성 (대출 가능/불가능 관계없이 예약 허용)
        Reservation.objects.create(userID=request.user, bookID=book, status='Pending')
    return redirect('library:search_books')

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
    
    # 통계 계산
    total_loans = loans.count()
    active_loans = loans.filter(return_date__isnull=True).count()
    returned_loans = loans.filter(return_date__isnull=False).count()
    overdue_loans = loans.filter(return_date__isnull=True, due_date__lt=date.today()).count()
    
    return render(request, 'library/loan_history.html', {
        'loans': loans,
        'date_today': date.today(),
        'total_loans': total_loans,
        'active_loans': active_loans,
        'returned_loans': returned_loans,
        'overdue_loans': overdue_loans,
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

# 신규 서비스 1: [과제5] 클래스메서드 기반 도서 추천 서비스
@login_required
def book_recommendations(request):
    """개인화된 도서 추천 페이지"""
    # 클래스메서드를 활용한 추천
    personal_recommendations = BookRecommendationService.get_recommendations_for_user(request.user, 5)
    popular_books = BookRecommendationService.get_trending_books(10)
    
    # 카테고리별 추천
    categories = Book.objects.values_list('category', flat=True).distinct()
    category_recommendations = {}
    for category in categories:
        category_recommendations[category] = BookRecommendationService.get_category_recommendations(category, 3)
    
    # 추천 통계
    stats = Book.get_recommendation_stats()
    
    return render(request, 'library/recommendations.html', {
        'personal_recommendations': personal_recommendations,
        'popular_books': popular_books,
        'category_recommendations': category_recommendations,
        'stats': stats,
        'categories': categories
    })

# 신규 서비스 2: [과제6] Request 객체 활용 도서 리뷰 서비스
def book_detail(request, book_id):
    """도서 상세 페이지 (리뷰 포함)"""
    book = get_object_or_404(Book, bookID=book_id)
    reviews = ReviewService.get_book_reviews(book)
    
    # 평균 평점 계산
    average_rating = None
    if reviews:
        total_rating = sum(review.rating for review in reviews)
        average_rating = round(total_rating / len(reviews), 1)
    
    # 사용자가 이미 리뷰를 작성했는지 확인
    user_review = None
    if request.user.is_authenticated:
        try:
            user_review = Review.objects.get(userID=request.user, bookID=book)
        except Review.DoesNotExist:
            pass
    
    return render(request, 'library/book_detail.html', {
        'book': book,
        'reviews': reviews,
        'average_rating': average_rating,
        'user_review': user_review,
        'can_review': request.user.is_authenticated and not user_review and 
                     Loan.objects.filter(userID=request.user, bookID=book).exists()
    })

@login_required
def create_review(request, book_id):
    """리뷰 작성 - Request 객체 정보 수집"""
    if request.method == 'POST':
        book = get_object_or_404(Book, bookID=book_id)
        rating = int(request.POST.get('rating'))
        content = request.POST.get('content')
        is_anonymous = request.POST.get('is_anonymous') == 'on'
        
        # Request 정보 수집 (과제6 요구사항)
        def get_client_ip(request):
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            return ip
        
        request_data = {
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'ip_address': get_client_ip(request),
            'method': request.method,
            'path': request.get_full_path(),
            'content_type': request.content_type
        }
        
        try:
            review = ReviewService.create_review(
                user=request.user,
                book=book,
                rating=rating,
                content=content,
                request_data=request_data,
                is_anonymous=is_anonymous
            )
            messages.success(request, '리뷰가 성공적으로 작성되었습니다.')
            return redirect('library:book_detail', book_id=book_id)
            
        except ReviewAlreadyExistsError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'리뷰 작성 중 오류가 발생했습니다: {str(e)}')
    
    return redirect('library:book_detail', book_id=book_id)

@login_required
def mark_review_helpful(request, review_id):
    """리뷰 도움됨 표시"""
    if request.method == 'POST':
        review = get_object_or_404(Review, reviewID=review_id)
        
        try:
            success = ReviewService.mark_helpful(request.user, review)
            if success:
                return JsonResponse({'success': True, 'message': '도움됨 표시가 완료되었습니다.'})
            else:
                return JsonResponse({'success': False, 'message': '이미 도움됨 표시를 하셨습니다.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '잘못된 요청입니다.'})

# 신규 서비스 3: [과제7] auth 활용 관리자 대시보드 서비스
@login_required
def admin_dashboard(request):
    """관리자 대시보드 - auth 활용"""
    if not request.user.is_admin:
        messages.error(request, '관리자 권한이 필요합니다.')
        return redirect('home')
    
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    try:
        # 시스템 통계 조회
        stats = AdminService.get_system_stats()
        
        # 관리자 액션 로깅
        AdminService.log_admin_action(
            admin_user=request.user,
            action="대시보드 접근",
            target_model="Dashboard",
            target_id=0,
            description="관리자 대시보드 페이지 접근",
            ip_address=get_client_ip(request)
        )
        
        # 최근 대출 현황
        recent_loans = Loan.objects.select_related('userID', 'bookID').order_by('-start_date')[:10]
        overdue_loans = Loan.objects.filter(
            return_date__isnull=True,
            due_date__lt=date.today()
        ).select_related('userID', 'bookID')
        
        return render(request, 'library/admin_dashboard.html', {
            'stats': stats,
            'recent_loans': recent_loans,
            'overdue_loans': overdue_loans,
        })
        
    except Exception as e:
        messages.error(request, f'대시보드 로딩 중 오류가 발생했습니다: {str(e)}')
        return redirect('home')

# 신규 서비스 5: [과제9] 서비스 레이어 분리된 대출 알림 서비스
@login_required
def user_notifications(request):
    """사용자 알림 조회"""
    unread_only = request.GET.get('unread_only') == 'true'
    notifications = NotificationService.get_user_notifications(request.user, unread_only)
    
    return render(request, 'library/notifications.html', {
        'notifications': notifications,
        'unread_only': unread_only
    })

@login_required
def mark_notification_read(request, notification_id):
    """알림 읽음 처리"""
    if request.method == 'POST':
        try:
            notification = get_object_or_404(
                LoanNotification, 
                id=notification_id, 
                user=request.user
            )
            
            success = NotificationService.mark_as_read(notification)
            
            if success:
                return JsonResponse({'success': True, 'message': '알림이 읽음 처리되었습니다.'})
            else:
                return JsonResponse({'success': False, 'message': '이미 읽은 알림입니다.'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '잘못된 요청입니다.'})

# 교과서 서비스 1: 스크롤 초기화 기능이 적용된 페이지
def book_list_with_scroll_reset(request):
    """스크롤 초기화 기능이 적용된 도서 목록"""
    books = Book.objects.all().order_by('-loan_count')
    categories = Book.objects.values_list('category', flat=True).distinct()
    
    selected_category = request.GET.get('category')
    if selected_category:
        books = books.filter(category=selected_category)
    
    return render(request, 'library/book_list_scroll.html', {
        'books': books,
        'categories': categories,
        'selected_category': selected_category
    })

# 향상된 대출/반납 서비스 (서비스 레이어 활용)
@login_required
def enhanced_borrow_book(request, book_id):
    """향상된 도서 대출 (서비스 레이어 활용)"""
    if request.method == 'POST':
        book = get_object_or_404(Book, bookID=book_id)
        
        try:
            loan = LoanService.borrow_book(request.user, book)
            messages.success(request, f"'{book.title}' 도서가 성공적으로 대출되었습니다.")
            return redirect('library:loan_history')
            
        except UserNotAllowedError as e:
            messages.error(request, str(e))
        except BookNotAvailableError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'대출 중 오류가 발생했습니다: {str(e)}')
    
    return redirect('library:search_books')

@login_required
def enhanced_return_book(request, loan_id):
    """향상된 도서 반납 (서비스 레이어 활용)"""
    if request.method == 'POST':
        loan = get_object_or_404(Loan, loanID=loan_id, userID=request.user)
        
        try:
            success = LoanService.return_book(loan)
            if success:
                messages.success(request, f"'{loan.bookID.title}' 도서가 성공적으로 반납되었습니다.")
            
        except Exception as e:
            messages.error(request, f'반납 중 오류가 발생했습니다: {str(e)}')
    
    return redirect('library:loan_history')