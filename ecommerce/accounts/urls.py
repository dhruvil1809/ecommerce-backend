from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterUserAPIView.as_view(), name='register'),
    path('login/', LoginUserAPIView.as_view(), name='login'),
    path('email-verify/', EmailVerifyCodeView.as_view(), name='email-verify'),
    path('code-verify/', VerifyCodeView.as_view(), name='code-verify'),
    path('reset-forgot-password/', ForgotPasswordResetAPIView.as_view(), name='reset-forgot-password'),
    path('all-user-details/', GetUserAPIView.as_view(), name='all-user-details'),
    path('users-status/<int:user_id>', ToggleUserActiveStatusAPIView.as_view(), name='users-status'),
    path('users-update/<int:user_id>', GetUserAPIView.as_view(), name='update-user'),
    path('users-delete/<int:user_id>', GetUserAPIView.as_view(), name='delete-user'),
]
