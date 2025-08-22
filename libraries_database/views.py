# Create your views here.
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone

from .filters import *
from .serializers import *
from .models import *

# drf-spectacular imports
from drf_spectacular.utils import (
    extend_schema, extend_schema_view,
    OpenApiExample
)


# -------------------------
# LIBRARY VIEWSET
# -------------------------
@extend_schema_view(
    list=extend_schema(
        description="Retrieve a list of libraries.",
        examples=[OpenApiExample(
            "Library list response",
            value=[{"library_id": 1, "library_name": "Central Library"}],
            response_only=True
        )]
    ),
    retrieve=extend_schema(description="Retrieve details of a single library."),
    create=extend_schema(description="Create a new library."),
    update=extend_schema(description="Update an existing library."),
    partial_update=extend_schema(description="Partially update an existing library."),
    destroy=extend_schema(description="Delete a library."),
)
class LibraryViewSet(viewsets.ModelViewSet):
    queryset = Library.objects.all()
    queryset = Library.objects.all()
    serializer_class = LibrarySerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = LibraryFilter
    ordering_fields = '__all__'
    ordering = ['library_id']

    @extend_schema(
        description="Retrieve details of a specific book within a library.",
        responses={200: OpenApiExample(
            "Book detail with rating",
            value={"book_title": "1984", "average_rating": 4.5},
            response_only=True,
        )}
    )
    @action(detail=True, methods=['get'], url_path='book-detail/(?P<book_id>[^/.]+)')
    def book_detail(self, request, pk=None, book_id=None):
        book = get_object_or_404(Book, id=book_id)
        avg_rating = book.average_rating()
        return Response({
            'book_id': book.book_id,
            'average_rating': avg_rating
        })


# -------------------------
# BOOK VIEWSET
# -------------------------
@extend_schema_view(
    list=extend_schema(description="Retrieve a list of all books with filters."),
    retrieve=extend_schema(description="Retrieve details of a single book."),
    create=extend_schema(description="Add a new book."),
    update=extend_schema(description="Update a book."),
    partial_update=extend_schema(description="Partially update a book."),
    destroy=extend_schema(description="Delete a book."),
)
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = BookFilter
    ordering_fields = '__all__'
    ordering = ['book_id']
    search_fields = ['title', 'authors__first_name', 'authors__last_name', 'categories__category']

    @extend_schema(
        description="Check availability of a book (available vs total copies).",
        responses={200: OpenApiExample(
            "Availability response",
            value={"title": "The Great Gatsby", "available_copies": 3, "total_copies": 5},
            response_only=True,
        )}
    )
    @action(detail=True, methods=['get'], url_path='availability')
    def availability(self, request, pk=None):
        book = self.get_object()
        return Response({
            'book_id': book.book_id,
            'available_copies': book.available_copies,
            'total_copies': book.total_copies
        })

    @extend_schema(
        description="Borrow a book for a member.",
        examples=[
            OpenApiExample(
                "Borrow request",
                value={"book_id": 1, "member_id": 2, "borrow_date": "2025-08-10", "due_date": "2025-08-24"},
                request_only=True,
            ),
            OpenApiExample(
                "Borrow success response",
                value={"status": "Book borrowed successfully."},
                response_only=True,
            )
        ]
    )
    @action(detail=False, methods=['post'], url_path='borrow')
    def borrow_book(self, request):
        try:
            book_id = request.data.get('book_id')
            member_id = request.data.get('member_id')
            borrow_date = request.data.get('borrow_date')
            due_date = request.data.get('due_date')

            book = Book.objects.get(pk=book_id)
            member = Member.objects.get(pk=member_id)

            if book.available_copies < 1:
                return Response({'error': 'No copies available.'}, status=400)

            Borrowing.objects.create(
                member=member,
                book=book,
                borrow_date=borrow_date,
                due_date=due_date,
                late_fee=0
            )

            book.available_copies -= 1
            book.save()
            return Response({'status': 'Book borrowed successfully.'}, status=200)

        except Exception as e:
            return Response({'error': str(e)}, status=400)

    @extend_schema(
        description="Return a borrowed book. Calculates late fee if overdue.",
        examples=[
            OpenApiExample(
                "Return request",
                value={"borrowing_id": 10},
                request_only=True
            ),
            OpenApiExample(
                "Return response",
                value={"status": "Book returned.", "late_fee": 20},
                response_only=True
            )
        ]
    )
    @action(detail=False, methods=['post'], url_path='return')
    def return_book(self, request):
        try:
            borrowing_id = request.data.get('borrowing_id')
            borrowing = Borrowing.objects.get(pk=borrowing_id)

            if borrowing.return_date:
                return Response({'error': 'Book already returned.'}, status=400)

            borrowing.return_date = timezone.now().date()
            if borrowing.return_date > borrowing.due_date:
                days_late = (borrowing.return_date - borrowing.due_date).days
                borrowing.late_fee = days_late * 5
            else:
                borrowing.late_fee = 0
            borrowing.save()

            book = borrowing.book
            book.available_copies += 1
            book.save()

            return Response({'status': 'Book returned.', 'late_fee': borrowing.late_fee}, status=200)

        except Exception as e:
            return Response({'error': str(e)}, status=400)

    @extend_schema(
        description="Get all active borrowings for a member.",
        responses={200: BorrowingSerializer(many=True)}
    )
    @action(detail=True, methods=['get'], url_path='active-borrowings')
    def active_borrowings(self, request, pk=None):
        """Get all active borrowings (not returned yet) for a specific member"""
        borrowings = Borrowing.objects.filter(member_id=pk, return_date__isnull=True)
        serializer = BorrowingSerializer(borrowings, many=True)
        return Response(serializer.data, status=200)



# -------------------------
# AUTHOR VIEWSET
# -------------------------
@extend_schema_view(
    list=extend_schema(description="Retrieve all authors."),
    retrieve=extend_schema(description="Get details of an author."),
    create=extend_schema(description="Create a new author."),
)
class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = AuthorFilter
    ordering_fields = '__all__'
    ordering = ['author_id']


# -------------------------
# CATEGORY VIEWSET
# -------------------------
@extend_schema_view(
    list=extend_schema(description="Retrieve all categories."),
    retrieve=extend_schema(description="Get details of a category."),
    create=extend_schema(description="Create a new category."),
)
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = CategoryFilter
    ordering_fields = '__all__'
    ordering = ['category_id']


# -------------------------
# MEMBER VIEWSET
# -------------------------
@extend_schema_view(
    list=extend_schema(description="Retrieve all members."),
    retrieve=extend_schema(description="Get details of a member."),
    create=extend_schema(description="Register a new member."),
)
# class MemberViewSet(viewsets.ModelViewSet):
#     queryset = Member.objects.all()
#     serializer_class = MemberSerializer
#     filter_backends = [DjangoFilterBackend, OrderingFilter]
#     filterset_class = MemberFilter
#     ordering_fields = '__all__'
#     ordering = ['member_id']
#
#     @extend_schema(
#         description="Get borrowing history of a member.",
#         responses={200: BorrowingSerializer(many=True)}
#     )
#     @action(detail=True, methods=['get'], url_path='borrowings')
#     def borrowings(self, request, pk=None):
#         member = self.get_object()
#         qs = Borrowing.objects.filter(member=member)
#         serializer = BorrowingSerializer(qs, many=True)
#         return Response(serializer.data)
#
#     @action(detail=True, methods=['get'], url_path='active-borrowings')
#     def active_borrowings(self, request, pk=None):
#         """Get all active borrowings (not returned yet) for a specific member"""
#         borrowings = Borrowing.objects.filter(member_id=pk, return_date__isnull=True)
#         serializer = BorrowingSerializer(borrowings, many=True)
#         return Response(serializer.data)

class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = MemberFilter
    ordering_fields = '__all__'
    ordering = ['member_id']

    @extend_schema(
        description="Get borrowing history of a member.",
        responses={200: BorrowingSerializer(many=True)}
    )
    @action(detail=True, methods=['get'], url_path='borrowings')
    def borrowings(self, request, pk=None):
        member = self.get_object()
        qs = Borrowing.objects.filter(member=member)
        serializer = BorrowingSerializer(qs, many=True)
        return Response(serializer.data)

    @extend_schema(
        description="Get active borrowings (not returned yet) for a member.",
        responses={200: BorrowingSerializer(many=True)}
    )
    @action(detail=True, methods=['get'], url_path='active-borrowings')
    def active_borrowings(self, request, pk=None):
        borrowings = Borrowing.objects.filter(member_id=pk, return_date__isnull=True)
        serializer = BorrowingSerializer(borrowings, many=True)
        return Response(serializer.data)



# -------------------------
# BORROWING VIEWSET
# -------------------------
@extend_schema_view(
    list=extend_schema(description="Retrieve all borrowings."),
    retrieve=extend_schema(description="Get details of a borrowing."),
    create=extend_schema(description="Create a new borrowing record."),
)
class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = BorrowingFilter
    ordering_fields = '__all__'
    ordering = ['borrowing_id']


# -------------------------
# REVIEW VIEWSET
# -------------------------
@extend_schema_view(
    list=extend_schema(description="Retrieve all reviews."),
    retrieve=extend_schema(description="Get details of a review."),
    create=extend_schema(description="Submit a new review."),
)
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ReviewFilter
    ordering_fields = '__all__'
    ordering = ['review_id']


# -------------------------
# BOOKAUTHOR VIEWSET
# -------------------------
class BookAuthorViewSet(viewsets.ModelViewSet):
    queryset = BookAuthor.objects.all()
    serializer_class = BookAuthorSerializer


# -------------------------
# BOOKCATEGORY VIEWSET
# -------------------------
class BookCategoryViewSet(viewsets.ModelViewSet):
    queryset = BookCategory.objects.all()
    serializer_class = BookCategorySerializer


# -------------------------
# STATISTICS API
# -------------------------
@extend_schema(
    description="Get overall statistics about the library (books, members, borrowings).",
    responses={200: OpenApiExample(
        "Statistics response",
        value={"total_books": 120, "total_members": 45, "total_borrowings": 320, "active_borrowings": 12},
        response_only=True
    )}
)
class StatisticsView(APIView):
    def get(self, request):
        total_books = Book.objects.count()
        total_members = Member.objects.count()
        total_borrowings = Borrowing.objects.count()
        active_borrowings = Borrowing.objects.filter(return_date__isnull=True).count()
        return Response({
            'total_books': total_books,
            'total_members': total_members,
            'total_borrowings': total_borrowings,
            'active_borrowings': active_borrowings
        })


# -------------------------
# MEMBER BORROWING HISTORY API
# -------------------------
@extend_schema(
    description="Get borrowing history for a specific member.",
    responses={200: BorrowingSerializer(many=True)}
)
class MemberBorrowingHistoryView(APIView):
    serializer_class = BorrowingSerializer

    def get_queryset(self):
        member_id = self.kwargs.get('member_id')
        return Borrowing.objects.filter(member_id=member_id)

    def get(self, request, member_id):
        borrowings = Borrowing.objects.filter(member_id=member_id)
        serializer = BorrowingSerializer(borrowings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BookAvailabilityView(APIView):
    def get(self, request, book_id):
        try:
            book = Book.objects.get(pk=book_id)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "book_id": book.book_id,
            "title": book.title,
            "available_copies": book.available_copies,
            "total_copies": book.total_copies
        })