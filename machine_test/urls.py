"""
URL configuration for machine_test project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
# from django.urls import path, include
# from django.http import HttpResponse
# from django.shortcuts import redirect
# from api.views import home_view

# # def home(request):
# #     return HttpResponse("Welcome to the Python Machine Test API! Visit /api/ to explore endpoints.")
# def redirect_to_home(request):
#     return redirect('/api/')
# urlpatterns = [
#     # path('', home),
#     path('admin/', admin.site.urls),
#     path('api/', include('api.urls')),
#      path('', home_view, name='home'), 
#     # path("", home),
#     # path('', redirect_to_home),
# ]

from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('api:index')),  # Redirect home to your API index page
    path('api/', include('api.urls')),                # Include your API URLs
]