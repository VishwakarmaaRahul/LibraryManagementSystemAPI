from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Avg


# ===================== Library =====================
class Library(models.Model):
    library_id = models.AutoField(primary_key=True)
    library_name = models.CharField(max_length=50, blank=False, null=False)
    campus_location = models.CharField(max_length=50)
    contact_email = models.EmailField(max_length=50, unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.library_name


# ===================== Book =====================
class Book(models.Model):
    book_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50, blank=False, null=False)
    isbn = models.CharField(max_length=20, unique=True)
    publication_date = models.DateField(null=True, blank=True)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    library = models.ForeignKey('Library', on_delete=models.CASCADE)
    authors = models.ManyToManyField('Author', through='BookAuthor')
    categories = models.ManyToManyField('Category', through='BookCategory')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def average_rating(self):
        avg = self.reviews.aggregate(Avg('rating'))['rating__avg']
        if avg is not None:
            return round(avg, 2)
        return None

    def clean(self):
        if self.available_copies < 0:
            raise ValidationError("Available copies cannot be negative.")

        if self.available_copies > self.total_copies:
            raise ValidationError("Available copies cannot exceed total copies.")

    def __str__(self):
        return self.title


# ===================== Author =====================
class Author(models.Model):
    author_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    birth_date = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=100, null=True, blank=True)
    biography = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# ===================== Category =====================
class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=50)
    descriptions = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.category


# ===================== Member =====================
class Member(models.Model):
    class MemberType(models.TextChoices):
        STUDENT = 'student', 'Student'
        FACULTY = 'faculty', 'Faculty'

    member_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    contact_email = models.EmailField(max_length=50, unique=True)
    phone_number = models.CharField(max_length=15)
    member_type = models.CharField(
        max_length=20,
        choices=MemberType.choices,
        default=MemberType.STUDENT
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def has_overdue_books(self):
        today = timezone.now().date()
        return (
            self.borrowing_set.filter(due_date__lt=today, return_date__isnull=True)
            .exists()
        )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# ===================== Borrowing =====================
class Borrowing(models.Model):
    borrowing_id = models.AutoField(primary_key=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateField()
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    late_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['member', 'book'],
                condition=models.Q(return_date__isnull=True),
                name='unique_active_borrowing_per_member_book'
            )
        ]

    def clean(self):
        if self.borrow_date > timezone.now().date():
            raise ValidationError("Borrow date cannot be in the future.")

        if self.due_date < self.borrow_date:
            raise ValidationError("Due date cannot be before borrow date.")

        if self.return_date and self.return_date < self.borrow_date:
            raise ValidationError("Return date cannot be before borrow date.")

        if self.late_fee is not None and self.late_fee < 0:
            raise ValidationError("Late fee cannot be negative.")

        if Borrowing.objects.filter(
            member=self.member,
            book=self.book,
            return_date__isnull=True
        ).exclude(pk=self.pk).exists():
            raise ValidationError("This member already has this book borrowed and not returned.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Always run validation
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Borrowing {self.borrowing_id} by {self.member}"


# ===================== Review =====================
class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(rating__gte=1) & models.Q(rating__lte=5),
                name='rating_between_1_and_5'
            ),
            models.UniqueConstraint(fields=['member', 'book'], name='unique_member_book')
        ]

    comment = models.TextField()
    review_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review {self.review_id} for {self.book}"


# ===================== BookAuthor =====================
class BookAuthor(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('book', 'author')

    def __str__(self):
        return f"{self.book.title} - {self.author}"


# ===================== BookCategory =====================
class BookCategory(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('book', 'category')

    def __str__(self):
        return f"{self.book.title} - {self.category.category}"
