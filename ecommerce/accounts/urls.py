from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterUserAPIView.as_view(), name='register'),
    path('login/', LoginUserAPIView.as_view(), name='login'),
    path('email-verify/', EmailVerifyCodeView.as_view(), name='email-verify'),
    path('code-verify/', VerifyCodeView.as_view(), name='code-verify'),
    path('reset-forgot-password/', ForgotPasswordResetAPIView.as_view(), name='reset-forgot-password'),
]
