# libraries_database/tests/test_serializers.py
from django.test import TestCase
from django.utils import timezone
from libraries_database.models import*
from libraries_database.serializers import (
    LibrarySerializer,
    BookSerializer,
    AuthorSerializer,
    CategorySerializer,
    MemberSerializer,
    ReviewSerializer,
)

class LibrarySerializerTest(TestCase):
    def test_valid_data(self):
        data = {
            "library_name": "Central Library",
            "campus_location": "Main Campus",
            "contact_email": "central@example.com",
            "phone_number": "1234567890",
        }
        serializer = LibrarySerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

class BookSerializerTest(TestCase):
    def setUp(self):
        self.library = Library.objects.create(
            library_name="Book Lib",
            campus_location="Campus D",
            contact_email="book@example.com",
            phone_number="1212121212",
        )
        self.author = Author.objects.create(
            first_name="Robert", last_name="Martin",
            birth_date="1952-12-05", nationality="USA"
        )
        self.category = Category.objects.create(
            category="Programming", descriptions="Programming related books"
        )

    def test_book_serializer_create(self):
        data = {
            "title": "Clean Architecture",
            "isbn": "777888999",
            "total_copies": 3,
            "available_copies": 3,
            "library": self.library.library_id,
            "authors": [self.author.author_id],
            "categories": [self.category.category_id],
        }
        serializer = BookSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        book = serializer.save()
        self.assertEqual(book.title, "Clean Architecture")

class AuthorSerializerTest(TestCase):
    def test_name_formatting(self):
        data = {"first_name": "  robert ", "last_name": " martin "}
        serializer = AuthorSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        validated = serializer.validated_data
        self.assertEqual(validated["first_name"], "Robert")
        self.assertEqual(validated["last_name"], "Martin")

class MemberSerializerTest(TestCase):
    def test_member_serializer(self):
        data = {
            "first_name": "Rahul",
            "last_name": "Vishwakarma",
            "contact_email": "rahul@example.com",
            "phone_number": "9999999999",
            "member_type": "student"
        }
        serializer = MemberSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

class ReviewSerializerTest(TestCase):
    def setUp(self):
        self.library = Library.objects.create(
            library_name="Review Lib",
            campus_location="Campus E",
            contact_email="reviewser@example.com",
            phone_number="5656565656",
        )
        self.book = Book.objects.create(
            title="Test Driven Development",
            isbn="222333444",
            total_copies=2,
            available_copies=2,
            library=self.library,
        )
        self.member = Member.objects.create(
            first_name="Test",
            last_name="User",
            contact_email="testuser@example.com",
            phone_number="4545454545",
        )

    def test_valid_review(self):
        data = {
            "member": self.member.member_id,
            "book": self.book.book_id,
            "rating": 4,
            "comment": "Great book",
            "review_date": timezone.now().date(),
        }
        serializer = ReviewSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
