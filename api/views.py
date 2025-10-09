from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
from .models import Expense
from .models import Category, Expense
from decimal import Decimal, InvalidOperation


def index(request):
    return render(request, 'api/index.html')


# ---------- REGISTER USER ----------
@api_view(['POST'])
def register_user(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    first_name = request.data.get('first_name', '')
    last_name = request.data.get('last_name', '')

    # --- Validation checks ---
    if not all([username, email, password]):
        return Response({"error": "All fields (username, email, password) are required"}, status=status.HTTP_400_BAD_REQUEST)

    if len(username) < 5:
        return Response({"error": "Username must be at least 5 characters"}, status=status.HTTP_400_BAD_REQUEST)

    import re
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return Response({"error": "Invalid email format"}, status=status.HTTP_400_BAD_REQUEST)

    if len(password) < 8 or not any(ch.isdigit() for ch in password):
        return Response({"error": "Password must be at least 8 characters long and include a number"}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)

    # --- Create user ---
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )

    return Response({
        "message": "User registered successfully!",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
    }, status=status.HTTP_201_CREATED)


# ---------- GET USERS ----------
@api_view(['GET'])
def get_users(request):
    users = User.objects.all().values('id', 'username', 'email', 'first_name', 'last_name')
    return Response(list(users))


# ---------- DELETE USER ----------
@api_view(['DELETE'])
def delete_user(request, id):
    try:
        user = User.objects.get(id=id)
        user.delete()
        return Response({"message": "User deleted successfully"}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


# ---------- CATEGORY ----------
@api_view(['POST'])
def add_category(request):
    # Accept either 'name' or 'category_name' from frontend
    name = request.data.get('name') or request.data.get('category_name')
    if not name:
        return Response({"error": "Category name required"}, status=status.HTTP_400_BAD_REQUEST)

    category, created = Category.objects.get_or_create(name=name)
    return Response({
        "message": "Category saved",
        "category": {"id": category.id, "name": category.name},
        "created": created
    }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


# ---------- EXPENSE ----------
@api_view(['POST'])
def add_expense(request):
    # Frontend should send: title, amount, category_id, date (optional), username (optional)
    title = request.data.get('title') or request.data.get('expense_title')
    amount = request.data.get('amount') or request.data.get('expense_amount')
    category_id = request.data.get('category_id') or request.data.get('expense_category_id')
    date = request.data.get('date') or request.data.get('expense_date')
    username = request.data.get('username')  # optional

    # Validate required fields
    if not title or not amount or not category_id:
        return Response({"error": "title, amount and category_id are required"}, status=status.HTTP_400_BAD_REQUEST)

    # parse amount
    try:
        amount_dec = Decimal(str(amount))
    except (InvalidOperation, TypeError, ValueError):
        return Response({"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)

    # find category
    try:
        category = Category.objects.get(id=int(category_id))
    except (Category.DoesNotExist, ValueError):
        return Response({"error": "Category not found (invalid category_id)"}, status=status.HTTP_400_BAD_REQUEST)

    # determine user
    user = None
    if username:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"error": "User not found (username)"}, status=status.HTTP_404_NOT_FOUND)
    else:
        # If there is exactly one user in system, use it automatically (useful for demos)
        if User.objects.count() == 1:
            user = User.objects.first()
        else:
            return Response({"error": "No username supplied — provide 'username' or ensure exactly one user exists"}, status=status.HTTP_400_BAD_REQUEST)

    # create expense
    expense = Expense.objects.create(
        user=user,
        title=title,
        amount=amount_dec,
        category=category,
        date=date or None
    )

    return Response({
        "message": "Expense added successfully",
        "expense": {
            "id": expense.id,
            "title": expense.title,
            "amount": str(expense.amount),
            "category": {"id": category.id, "name": category.name},
            "user": user.username,
            "date": expense.date.isoformat() if expense.date else None
        }
    }, status=status.HTTP_201_CREATED)


# ---------- SUMMARY ----------
@api_view(['GET'])
def get_expense_summary(request):
    qs = Expense.objects.values('category__name').annotate(total=Sum('amount'))
    result = { item['category__name']: float(item['total'] or 0) for item in qs }
    return Response(result)