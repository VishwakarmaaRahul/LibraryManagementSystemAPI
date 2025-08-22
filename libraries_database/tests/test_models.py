# libraries_database/tests/test_models.py
from django.test import TestCase
from libraries_database.models import*

class LibraryModelTest(TestCase):
    def test_create_library(self):
        library = Library.objects.create(
            library_name="Central Library",
            campus_location="Main Campus",
            contact_email="central@example.com",
            phone_number="1234567890",
        )
        self.assertEqual(str(library), "Central Library")

class BookModelTest(TestCase):
    def setUp(self):
        self.library = Library.objects.create(
            library_name="Test Library",
            campus_location="Campus A",
            contact_email="lib@example.com",
            phone_number="9876543210",
        )
        self.book = Book.objects.create(
            title="Django for Beginners",
            isbn="1234567890",
            total_copies=5,
            available_copies=3,
            library=self.library,
        )

    def test_book_str(self):
        self.assertEqual(str(self.book), "Django for Beginners")

    def test_invalid_available_copies(self):
        self.book.available_copies = 10  # more than total
        with self.assertRaises(Exception):
            self.book.full_clean()

class MemberModelTest(TestCase):
    def test_member_str_and_overdue(self):
        member = Member.objects.create(
            first_name="Rahul",
            last_name="Vishwakarma",
            contact_email="rahul@example.com",
            phone_number="9999999999",
        )
        self.assertEqual(str(member), "Rahul Vishwakarma")
        self.assertFalse(member.has_overdue_books())

class BorrowingModelTest(TestCase):
    def setUp(self):
        self.library = Library.objects.create(
            library_name="Borrow Lib",
            campus_location="Campus B",
            contact_email="borrow@example.com",
            phone_number="1234560000",
        )
        self.book = Book.objects.create(
            title="Clean Code",
            isbn="111222333",
            total_copies=2,
            available_copies=2,
            library=self.library,
        )
        self.member = Member.objects.create(
            first_name="John",
            last_name="Doe",
            contact_email="john@example.com",
            phone_number="8888888888",
        )

    def test_valid_borrowing(self):
        borrowing = Borrowing.objects.create(
            member=self.member,
            book=self.book,
            borrow_date=timezone.now().date(),
            due_date=timezone.now().date() + timezone.timedelta(days=7),
        )
        self.assertIn("Borrowing", str(borrowing))

    def test_invalid_future_borrow_date(self):
        with self.assertRaises(Exception):
            Borrowing.objects.create(
                member=self.member,
                book=self.book,
                borrow_date=timezone.now().date() + timezone.timedelta(days=1),
                due_date=timezone.now().date() + timezone.timedelta(days=10),
            )

class ReviewModelTest(TestCase):
    def setUp(self):
        self.library = Library.objects.create(
            library_name="Review Lib",
            campus_location="Campus C",
            contact_email="review@example.com",
            phone_number="1234500000",
        )
        self.book = Book.objects.create(
            title="Python Tricks",
            isbn="444555666",
            total_copies=1,
            available_copies=1,
            library=self.library,
        )
        self.member = Member.objects.create(
            first_name="Alice",
            last_name="Smith",
            contact_email="alice@example.com",
            phone_number="7777777777",
        )

    def test_review_str(self):
        review = Review.objects.create(
            member=self.member,
            book=self.book,
            rating=5,
            comment="Excellent!",
            review_date=timezone.now().date(),
        )
        self.assertIn("Review", str(review))
