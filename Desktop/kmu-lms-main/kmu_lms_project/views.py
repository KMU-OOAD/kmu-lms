# main/views.py
from django.shortcuts import render
from notices.models import Notice
from library.models import Book
from library_info.models import LibraryInfo
import datetime

def home_view(request):
    notices = Notice.objects.order_by('-posted_date')[:3]  # 최신 3건

    # 오늘 요일에 맞는 도서관 정보
    day_map = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    today_key = day_map[datetime.datetime.today().weekday()]
    popular_books = Book.objects.order_by('-loan_count')[:3]
    try:
        today_info = LibraryInfo.objects.get(day=today_key)
    except LibraryInfo.DoesNotExist:
        today_info = None

    return render(request, 'main/home.html', {
        'notices': notices,
        'today_info': today_info,
        'popular_books': popular_books,
    })
