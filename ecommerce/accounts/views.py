from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.serializers import *
from ecommerce.renderers import CustomRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import User
from django.contrib.auth.hashers import check_password
from django.utils.crypto import get_random_string
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination


class RegisterUserAPIView(APIView):
    renderer_classes = [CustomRenderer]

    def post(self, request):
        user_serializer = RegisterUserSerializer(data=request.data)
        if user_serializer.is_valid():
            user = user_serializer.save()

            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "message": "User registered successfully.",
                    "access": str(refresh.access_token),
                    "status_code": status.HTTP_200_OK,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "errors": user_serializer.errors,
                "status_code": status.HTTP_400_BAD_REQUEST,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    

class LoginUserAPIView(APIView):
    renderer_classes = [CustomRenderer]

    def post(self, request):
        serializer = LoginUserSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response(
                    {
                        "errors": {
                            "error": "Invalid email.",
                            "status_code": status.HTTP_200_OK,
                        }
                    },
                    status=status.HTTP_200_OK,
                )
            
            # Check if the user is active
            if not user.is_active:
                return Response(
                    {
                        "errors": {
                            "error": "This account is deactivated. Please contact support.",
                            "status_code": status.HTTP_200_OK,
                        }
                    },
                    status=status.HTTP_200_OK,
                )
            
            # Manually check the password
            if not check_password(password, user.password):
                return Response(
                    {
                        "errors": {
                            "error": "Invalid password.",
                            "status_code": status.HTTP_200_OK,
                        }
                    },
                    status=status.HTTP_200_OK,
                )
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "message": "Login successful.",
                    "access": str(refresh.access_token),
                    "status_code": status.HTTP_200_OK,
                },
                status=status.HTTP_200_OK,
            )
        
        return Response(
            {
                "errors": serializer.errors,
                "status_code": status.HTTP_400_BAD_REQUEST,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    

class EmailVerifyCodeView(APIView):
    renderer_classes = [CustomRenderer]

    def send_verification_email(self, email, verification_code):
        subject = 'Email Verification Code'
        plain_message = f'Your verification code is: {verification_code}'
        html_message = render_to_string('verification_email.html', {'verification_code': verification_code})
        send_mail(subject, plain_message, settings.EMAIL_HOST_USER, [email], html_message=html_message)

    def post(self, request, format=None):
        serializer = EmailVerifyCodeSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']

            if User.objects.filter(email=email).exists():
                verification_code = get_random_string(length=4, allowed_chars='1234567890')
                cache.set(email, verification_code, timeout=300)  # Store in cache for 5 minutes
                self.send_verification_email(email, verification_code)  # Custom function to send email
                return Response(
                    {
                        "message": "Verification code sent successfully.",
                        "status_code": status.HTTP_200_OK,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                {
                    "errors": {
                        "email": "Email not found.",
                        "status_code": status.HTTP_200_OK,
                    }
                },
                status.HTTP_200_OK,
            )
        return Response(
            {
                "errors": serializer.errors,
                "status_code": status.HTTP_400_BAD_REQUEST,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    

class VerifyCodeView(APIView):
    renderer_classes = [CustomRenderer]
    def post(self, request, format=None):
        serializer = VerificationCodeSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            verification_code = serializer.validated_data['code']
            stored_code = cache.get(email)
            if stored_code and stored_code == verification_code:
                # Code is valid, allow the user to reset password
                return Response(
                    {
                        "message": "Verification successful.",
                        "status_code": status.HTTP_200_OK,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                {
                    "errors": {
                        "code": "Invalid verification code.",
                        "status_code": status.HTTP_200_OK,
                    }
                },
                status.HTTP_200_OK,
            )
        return Response(
            {
                "errors": serializer.errors,
                "status_code": status.HTTP_400_BAD_REQUEST,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    

class ForgotPasswordResetAPIView(APIView):
    renderer_classes = [CustomRenderer]

    def post(self, request):
        serializer = ForgotPasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            new_password = serializer.validated_data['new_password']
            confirm_password = serializer.validated_data['confirm_password']

            if new_password!= confirm_password:
                return Response(
                    {
                        "errors": {
                            "confirm_password": "New password and confirm password do not match.",
                            "status_code": status.HTTP_200_OK,
                        }
                    },
                    status=status.HTTP_200_OK,
                )
            try:
                user = User.objects.get(email=email)
                user.set_password(new_password)
                user.save()
                return Response(
                    {
                        "message": "Password has been reset successfully.",
                        "status_code": status.HTTP_200_OK,
                    },
                    status=status.HTTP_200_OK,
                )
            except User.DoesNotExist:
                return Response(
                    {
                        "errors": {
                            "user": "User not found.",
                            "status_code": status.HTTP_200_OK,
                        }
                    },
                    status.HTTP_200_OK,
                )
        return Response(
            {"errors": serializer.errors, "status_code": status.HTTP_400_BAD_REQUEST},
            status=status.HTTP_400_BAD_REQUEST,
        )


class GetUserAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [CustomRenderer]

    def get(self, request):
        users = User.objects.filter(deleted=False)
        
        paginator = PageNumberPagination()
        paginator.page_size = 20

        paginated_users = paginator.paginate_queryset(users, request)

        serializer = GetUserSerializer(paginated_users, many=True)

        return paginator.get_paginated_response(
            {
                "User_data": serializer.data,
                "message": "Users retrieved successfully.",
                "status_code": status.HTTP_200_OK,
            }
        )
    
    def put(self, request, user_id):
        try:
            user = User.objects.get(user_id=user_id, deleted=False)
        except User.DoesNotExist:
            return Response(
                {
                    "message": "User not found.",
                    "status_code": status.HTTP_200_OK,
                },
                status=status.HTTP_200_OK,
            )

        serializer = GetUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "User updated successfully.",
                    "status_code": status.HTTP_200_OK,
                    "user": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "message": "Invalid data.",
                "errors": serializer.errors,
                "status_code": status.HTTP_400_BAD_REQUEST,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, user_id):
        try:
            user = User.objects.get(user_id=user_id, deleted=False)
        except User.DoesNotExist:
            return Response(
                {
                    "message": "User not found.",
                    "status_code": status.HTTP_200_OK,
                },
                status=status.HTTP_200_OK,
            )

        user.deleted = True
        user.save()

        return Response(
            {
                "message": "User deleted successfully.",
                "status_code": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )


class ToggleUserActiveStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [CustomRenderer]

    def post(self, request, user_id):
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response(
                {
                    "errors": {
                        "user": "User not found.",
                        "status_code": status.HTTP_200_OK,
                    }
                },
                status=status.HTTP_200_OK,
            )

        new_status = not user.is_active
        serializer = DeactivateUserSerializer(user, data={'is_active': new_status}, partial=True)

        if serializer.is_valid():
            serializer.save()
            message = "User activated successfully." if new_status else "User deactivated successfully."
            return Response(
                {
                    "message": message,
                    "status_code": status.HTTP_200_OK,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"errors": serializer.errors, "status_code": status.HTTP_400_BAD_REQUEST},
            status=status.HTTP_400_BAD_REQUEST,
        )




