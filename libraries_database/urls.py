from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .views import *

router = DefaultRouter()
router.register(r'libraries',LibraryViewSet)
router.register(r'books', BookViewSet)
router.register(r'authors', AuthorViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'members',MemberViewSet)
router.register(r'borrowings',BorrowingViewSet)
router.register(r'reviews',ReviewViewSet)
router.register(r'bookauthors', BookAuthorViewSet)
router.register(r'bookcategories', BookCategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('statistics/', StatisticsView.as_view(), name='library-statistics'),
    path('statistics/', StatisticsView.as_view(), name='statistics-view'),

    path(
        'member/<int:member_id>/borrowings/',
        MemberBorrowingHistoryView.as_view(),
        name='member-borrowing-history'
    ),
    path(
        'books/<int:book_id>/availability/',
        views.BookAvailabilityView.as_view(),
        name='book-availability'
    ),
    path('books/<int:pk>/availability/', BookAvailabilityView.as_view(), name='book-availability'),

]
