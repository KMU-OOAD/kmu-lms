# myadmin/management/commands/generate_sample_data.py

from django.core.management.base import BaseCommand
from faker import Faker
from datetime import timedelta, date
import random
from library.models import User, Book, Loan

fake = Faker('ko_KR')

class Command(BaseCommand):
    help = "LMS 기능 시험용 데이터 생성"

    def handle(self, *args, **kwargs):
        self.stdout.write("🚀 기능 시험용 데이터 생성 시작...")

        # 사용자 생성
        for _ in range(5):
            user = User.objects.create_user(
                student_id=fake.unique.numerify('2023######'),
                username=fake.name(),
                phone=fake.phone_number(),
                email=fake.unique.email(),
                password='testpass'
            )
            self.stdout.write(f"Created User: {user.username}")

        # 관리자 생성 (권장)
        admin = User.objects.create_superuser(
            student_id=fake.unique.numerify('2023######'),
            username='관리자',
            phone='010-1234-5678',
            email=fake.unique.email(),
            password='adminpass'
        )

        # 도서 생성
        for _ in range(10):
            book = Book.objects.create(
                title=fake.catch_phrase(),
                author=fake.name(),
                available=True,
            )
            self.stdout.write(f"Created Book: {book.title}")

        # 대출 생성 (연체 포함)
        users = User.objects.filter(is_admin=False)
        books = Book.objects.all()
        for _ in range(10):
            user = random.choice(users)
            book = random.choice(books)
            start_date = date.today() - timedelta(days=random.randint(1, 15))
            due_date = start_date + timedelta(days=7)
            is_overdue = due_date < date.today()

            loan = Loan.objects.create(
                userID=user,
                bookID=book,
                start_date=start_date,
                due_date=due_date,
                is_overdue=is_overdue
            )
            self.stdout.write(f"Created Loan: {user.username} → {book.title} (연체: {is_overdue})")

        self.stdout.write("🎉 기능 시험용 데이터 생성 완료!")
