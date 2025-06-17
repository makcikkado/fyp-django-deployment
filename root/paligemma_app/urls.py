"""
URL configuration for paligemma project.

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
from django.urls import path
from django.conf import settings
from . import views
from django.conf.urls.static import static
# from .views import image_upload_view 



# app_name = "app"

urlpatterns = [
    path('', views.mainView, name='main'),
    path('home/', views.HomePageView, name='home'),
    path('register/', views.RegisterView, name='register'),
    path('login/', views.LoginView, name='login'),
    path('logout/', views.LogoutView, name='logout'),
    path('forgot-password/', views.ForgotPassword, name='forgot-password'),
    path('password-reset-sent/<str:reset_id>/', views.PasswordResetSent, name='password-reset-sent'),
    path('reset-password/<str:reset_id>/', views.ResetPassword, name='reset-password'),
    path('response/<int:pk>/', views.ResponseView, name='response'),
    path('response_logged/<int:pk>/', views.ResponseLoggedView, name='response-logged'),
    path('history/', views.HistoryView, name='history'),
    path('language/', views.LanguageView, name='languages'),
    path('help/', views.HelpView, name='help-menu')
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
