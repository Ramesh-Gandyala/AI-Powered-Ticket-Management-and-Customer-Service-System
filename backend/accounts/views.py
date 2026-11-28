
from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from .tokens import (
    admin_email_verification_token,
    agent_email_verification_token,
    customer_email_verification_token,
)

from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    AdminLoginSerializer,
    AgentLoginSerializer,
    AgentRegistrationSerializer,
    CustomerRegistrationSerializer,
    CustomerLoginSerializer,
     GoogleLoginSerializer,
)

from .email_utils import (
    send_agent_verification_email,
    send_customer_verification_email,
)


User = get_user_model()


class AdminEmailVerificationAPIView(APIView):

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, uid, token):

        # Step 1: Find the Admin account
        try:
            admin = User.objects.get(
                pk=uid,
                role=User.Role.ADMIN
            )
        except User.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Invalid verification link."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Step 2: Check whether email is already verified
        if admin.is_email_verified:
            return Response(
                {
                    "success": True,
                    "message": "Admin email is already verified."
                },
                status=status.HTTP_200_OK
            )

        # Step 3: Validate the verification token

        token_is_valid = admin_email_verification_token.check_token(
            admin,
            token
        )

        if not token_is_valid:
            return Response(
                {
                    "success": False,
                    "message": "Invalid or expired verification link."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Step 4: Activate the Admin account
        admin.is_email_verified = True
        admin.is_active = True

        admin.save(
            update_fields=[
                "is_email_verified",
                "is_active"
            ]
        )

        # Step 5: Return API response
        return Response(
            {
                "success": True,
                "message": "Admin email verified successfully. Your account is now active."
            },
            status=status.HTTP_200_OK
        )



class AdminLoginAPIView(APIView):

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):

        # Step 1: Validate login credentials
        serializer = AdminLoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Admin login failed.",
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Step 2: Get the validated Admin account
        admin = serializer.validated_data["admin"]

        # Step 3: Generate JWT tokens
        refresh = RefreshToken.for_user(admin)
        access = refresh.access_token

        # Step 4: Prepare Admin details
        admin_details = {
            "id": admin.id,
            "username": admin.username,
            "email": admin.email,
            "first_name": admin.first_name,
            "last_name": admin.last_name,
            "role": admin.role
        }

        # Step 5: Return successful response
        return Response(
            {
                "success": True,
                "message": "Admin login successful.",
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(access)
                },
                "admin": admin_details
            },
            status=status.HTTP_200_OK
        )


class AgentLoginAPIView(APIView):

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):

        # Step 1: Validate login credentials
        serializer = AgentLoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Agent login failed.",
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Step 2: Get the validated Agent account
        agent = serializer.validated_data["agent"]

        # Step 3: Generate JWT tokens
        refresh = RefreshToken.for_user(agent)
        access = refresh.access_token

        # Step 4: Prepare Agent details
        agent_details = {
            "id": agent.id,
            "username": agent.username,
            "email": agent.email,
            "first_name": agent.first_name,
            "last_name": agent.last_name,
            "role": agent.role
        }

        # Step 5: Return successful response
        return Response(
            {
                "success": True,
                "message": "Agent login successful.",
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(access)
                },
                "agent": agent_details
            },
            status=status.HTTP_200_OK
        )


class AgentEmailVerificationAPIView(APIView):

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, uid, token):

        # Step 1: Find the Agent account
        try:
            agent = User.objects.get(
                pk=uid,
                role=User.Role.AGENT
            )
        except User.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Invalid verification link."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Step 2: Check whether email is already verified
        if agent.is_email_verified:
            return Response(
                {
                    "success": True,
                    "message": "Agent email is already verified."
                },
                status=status.HTTP_200_OK
            )

        # Step 3: Validate the verification token
        token_is_valid = agent_email_verification_token.check_token(
            agent,
            token
        )

        if not token_is_valid:
            return Response(
                {
                    "success": False,
                    "message": "Invalid or expired verification link."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Step 4: Verify email and activate Agent account
        agent.is_email_verified = True
        agent.is_active = True

        agent.save(
            update_fields=[
                "is_email_verified",
                "is_active"
            ]
        )

        # Step 5: Return API response
        return Response(
            {
                "success": True,
                "message": "Agent email verified successfully. Your account is now active."
            },
            status=status.HTTP_200_OK
        )


class AgentRegistrationAPIView(APIView):

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):

        # Step 1: Validate registration information
        serializer = AgentRegistrationSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Agent registration failed.",
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Step 2: Create Agent account
        agent = serializer.save()

        # Step 3: Send verification email
        try:
            send_agent_verification_email(agent)

        except Exception:
            agent.delete()

            return Response(
                {
                    "success": False,
                    "message": "Unable to send verification email. Please try again."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Step 4: Return successful response
        return Response(
            {
                "success": True,
                "message": (
                    "Agent account created successfully. "
                    "Please verify your email address."
                ),
                "agent": {
                    "id": agent.id,
                    "username": agent.username,
                    "email": agent.email,
                    "first_name": agent.first_name,
                    "last_name": agent.last_name,
                    "role": agent.role,
                    "is_active": agent.is_active,
                    "is_email_verified": agent.is_email_verified
                }
            },
            status=status.HTTP_201_CREATED
        )


class CustomerEmailVerificationAPIView(APIView):

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, uid, token):

        # Step 1: Find the Customer account
        try:
            customer = User.objects.get(
                pk=uid,
                role=User.Role.CUSTOMER
            )
        except User.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Invalid verification link."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Step 2: Check whether email is already verified
        if customer.is_email_verified:
            return Response(
                {
                    "success": True,
                    "message": "Customer email is already verified."
                },
                status=status.HTTP_200_OK
            )

        # Step 3: Validate the verification token
        token_is_valid = customer_email_verification_token.check_token(
            customer,
            token
        )

        if not token_is_valid:
            return Response(
                {
                    "success": False,
                    "message": "Invalid or expired verification link."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Step 4: Verify email and activate Customer account
        customer.is_email_verified = True
        customer.is_active = True

        customer.save(
            update_fields=[
                "is_email_verified",
                "is_active"
            ]
        )

        # Step 5: Return API response
        return Response(
            {
                "success": True,
                "message": "Customer email verified successfully. Your account is now active."
            },
            status=status.HTTP_200_OK
        )


class CustomerRegistrationAPIView(APIView):

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):

        # Step 1: Validate registration information
        serializer = CustomerRegistrationSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Customer registration failed.",
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Step 2: Create Customer account
        customer = serializer.save()

        # Step 3: Send verification email
        try:
            send_customer_verification_email(customer)

        except Exception:
            customer.delete()

            return Response(
                {
                    "success": False,
                    "message": "Unable to send verification email. Please try again."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Step 4: Return successful response
        return Response(
            {
                "success": True,
                "message": (
                    "Customer account created successfully. "
                    "Please verify your email address."
                ),
                "customer": {
                    "id": customer.id,
                    "username": customer.username,
                    "email": customer.email,
                    "first_name": customer.first_name,
                    "last_name": customer.last_name,
                    "role": customer.role,
                    "is_active": customer.is_active,
                    "is_email_verified": customer.is_email_verified
                }
            },
            status=status.HTTP_201_CREATED
        )




class CustomerLoginAPIView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = CustomerLoginSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        customer = serializer.validated_data["customer"]

        refresh = RefreshToken.for_user(customer)

        access = refresh.access_token

        return Response(
            {
                "success": True,
                "message": "Customer login successful.",
                "refresh": str(refresh),
                "access": str(access),
                "customer": {
                    "id": customer.id,
                    "username": customer.username,
                    "email": customer.email,
                    "first_name": customer.first_name,
                    "last_name": customer.last_name,
                    "role": customer.role,
                }
            },
            status=status.HTTP_200_OK
        )


class GoogleLoginAPIView(APIView):

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):

        # Step 1: Validate the Google ID token
        serializer = GoogleLoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Google login failed.",
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Step 2: Get the authenticated user
        user = serializer.validated_data["user"]

        # Step 3: Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        # Step 4: Prepare user details
        user_details = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role
        }

        # Step 5: Return successful response
        return Response(
            {
                "success": True,
                "message": "Google login successful.",
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(access)
                },
                "user": user_details
            },
            status=status.HTTP_200_OK
        )

