from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.serializers import *
from ecommerce.renderers import CustomRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import User
from django.contrib.auth.hashers import check_password

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
                    "status_code": status.HTTP_201_CREATED,
                },
                status=status.HTTP_201_CREATED,
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
                            "error": "Invalid email or password.",
                            "status_code": status.HTTP_401_UNAUTHORIZED,
                        }
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            
            # Manually check the password
            if not check_password(password, user.password):
                return Response(
                    {
                        "errors": {
                            "error": "Invalid email or password.",
                            "status_code": status.HTTP_401_UNAUTHORIZED,
                        }
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
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