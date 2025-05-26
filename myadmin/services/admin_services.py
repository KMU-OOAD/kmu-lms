from library.models import Book, Loan
from accounts.models import User
from datetime import timedelta, date

class AdminService:
    # 책 관리
    def new_book(self, title, author):
        return Book.objects.create(title=title, author=author)

    def edit_book(self, bookID, title=None, author=None, status=None):
        book = Book.objects.get(pk=bookID)
        if title: book.title = title
        if author: book.author = author
        if status: book.status = status
        book.save()
        return book

    def delete_book(self, bookID):
        book = Book.objects.get(pk=bookID)
        if book.status == 'loaned':
            raise Exception('대출 중인 도서는 삭제할 수 없습니다.')
        book.delete()
        
    # 대출 관리
    def manage_loan(self, loan_id):
        loan = Loan.objects.get(pk=loan_id)
        loan.dueDate += timedelta(days=7)  # 대출일 7일 연장
        loan.save()
        return loan

    # 연체 사용자 관리
    def impose_penalty(self, user_id):
            user = User.objects.get(pk=user_id)
            if user.penalty_until and user.penalty_until > date.today():
                raise Exception(f"{user.penalty_until}까지 이미 제재 중입니다.")
            user.can_borrow = False
            user.penalty_until = date.today() + timedelta(days=7)  # 7일 제재
            user.save()
            return user

    def release_penalty(self, user_id):
        user = User.objects.get(pk=user_id)
        if not user.penalty_until or user.penalty_until <= date.today():
            raise Exception("현재 제재 중인 사용자가 아닙니다.")
        user.can_borrow = True
        user.penalty_until = None
        user.save()
        return user