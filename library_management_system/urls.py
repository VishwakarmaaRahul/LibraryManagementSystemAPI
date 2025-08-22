"""
URL configuration for library_management_system project.

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
from django.urls import path, include
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

# class HelloWorldView(APIView):
#     def get(self, request):
#         return Response({"message": "Hello, world!"})

urlpatterns = [

    # path('', HelloWorldView.as_view()),
    path('api/v1/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/v1/docs/', SpectacularSwaggerView.as_view(url_name='schema')),
    path('api/v1/redoc/', SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path('api/v1/', include('libraries_database.urls')),


    # Add other API URLs here
]





