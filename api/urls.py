from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_user, name='register_user'),   # leave your register view as-is
    path('users/', views.get_users, name='get_users'),
    path('users/<int:id>/delete/', views.delete_user, name='delete_user'),

    # Category & Expense
    path('categories/add/', views.add_category, name='add_category'),
    path('expenses/add/', views.add_expense, name='add_expense'),
    path('expenses/summary/', views.get_expense_summary, name='get_expense_summary'),
]
