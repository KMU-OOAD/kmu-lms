from django.core.management.base import BaseCommand
from faker import Faker
from datetime import timedelta, date
import random

from myadmin.models import User, Book, Loan

fake = Faker('ko_KR')  # 한국어 데이터 생성

class Command(BaseCommand):
    help = "Generate sample Users, Books, Loans for testing"

    def handle(self, *args, **kwargs):
        # 1️⃣ 일반 사용자 생성 (연체 X, 제재 X)
        for _ in range(5):
            user = User.objects.create_user(
                username=fake.user_name(),
                password='password123',
                can_borrow=True,
                penalty_until=None
            )
            print(f"Created 일반 사용자: {user.username}")
                
        # 2️⃣ 도서 생성
        for _ in range(10):
            book = Book.objects.create(
                title=fake.catch_phrase(),
                author=fake.name(),
                status='available'
            )
            print(f"Created Book: {book.title}")
        
        users = User.objects.all()
        books = Book.objects.all()

        # 3️⃣ 연체 사용자 (제재 필요, can_borrow=True, penalty_until=None)
        for _ in range(3):
            user = User.objects.create_user(
                username=fake.user_name(),
                password='password123',
                can_borrow=True,
                penalty_until=None
            )
            book = random.choice(books)
            start_date = date.today() - timedelta(days=random.randint(10, 20))  # 랜덤화
            due_date = start_date + timedelta(days=7)

            loan = Loan.objects.create(
                userID=user,
                bookID=book,
                startDate=start_date,
                dueDate=due_date,
                is_overdue=True
            )

            book.status = 'loaned'  # Loan 생성 시 Book 상태 업데이트
            book.save()

            print(f"Created 연체 사용자 (제재 필요): {user.username} → {book.title}")

        # 4️⃣ 이미 제재 중인 사용자 (can_borrow=False, penalty_until=랜덤 날짜)
        for _ in range(2):
            penalty_days = random.randint(1, 7)
            user = User.objects.create_user(
                username=fake.user_name(),
                password='password123',
                can_borrow=False,
                penalty_until=date.today() + timedelta(days=penalty_days)
            )
            book = random.choice(books)
            start_date = date.today() - timedelta(days=14)
            due_date = start_date + timedelta(days=7)

            loan = Loan.objects.create(
                userID=user,
                bookID=book,
                startDate=start_date,
                dueDate=due_date,
                is_overdue=True
            )

            print(f"Created 연체 사용자 (이미 제재 중): {user.username} → {book.title} (penalty_until={user.penalty_until})")

        print("🎉 테스트 데이터 생성 완료!")
