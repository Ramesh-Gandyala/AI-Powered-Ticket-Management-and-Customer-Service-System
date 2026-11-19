from django.contrib.auth import authenticate, get_user_model

from rest_framework import serializers

from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


User = get_user_model()

class AdminLoginSerializer(serializers.Serializer):

    login_identifier = serializers.CharField()
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"}
    )

    def validate(self, attrs):

        login_identifier = attrs.get("login_identifier")
        password = attrs.get("password")

        # Step 1: Find the Admin account
        try:
            admin = User.objects.get(
                username=login_identifier,
                role=User.Role.ADMIN
            )
        except User.DoesNotExist:
            try:
                admin = User.objects.get(
                    email__iexact=login_identifier,
                    role=User.Role.ADMIN
                )
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    "Invalid username/email or password."
                )

        # Step 2: Verify the password
        if not admin.check_password(password):
            raise serializers.ValidationError(
                "Invalid username/email or password."
            )

        # Step 3: Check account activation
        if not admin.is_active:
            raise serializers.ValidationError(
                "Your Admin account is inactive."
            )

        # Step 4: Check email verification
        if not admin.is_email_verified:
            raise serializers.ValidationError(
                "Please verify your email address before logging in."
            )

        # Step 5: Store the validated Admin
        attrs["admin"] = admin

        return attrs


class AgentLoginSerializer(serializers.Serializer):

    login_identifier = serializers.CharField()
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"}
    )

    def validate(self, attrs):

        login_identifier = attrs.get("login_identifier")
        password = attrs.get("password")

        # Step 1: Find the Agent account
        try:
            agent = User.objects.get(
                username=login_identifier,
                role=User.Role.AGENT
            )
        except User.DoesNotExist:
            try:
                agent = User.objects.get(
                    email__iexact=login_identifier,
                    role=User.Role.AGENT
                )
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    "Invalid username/email or password."
                )

        # Step 2: Verify the password
        if not agent.check_password(password):
            raise serializers.ValidationError(
                "Invalid username/email or password."
            )

        # Step 3: Check account activation
        if not agent.is_active:
            raise serializers.ValidationError(
                "Your Agent account is inactive."
            )

        # Step 4: Check email verification
        if not agent.is_email_verified:
            raise serializers.ValidationError(
                "Please verify your email address before logging in."
            )

        # Step 5: Store the validated Agent
        attrs["agent"] = agent

        return attrs



class CustomerLoginSerializer(serializers.Serializer):

    login_identifier = serializers.CharField()

    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"}
    )

    def validate(self, attrs):

        login_identifier = attrs.get("login_identifier")
        password = attrs.get("password")

        customer = User.objects.filter(
            role=User.Role.CUSTOMER
        ).filter(
            username__iexact=login_identifier
        ).first()

        if customer is None:
            customer = User.objects.filter(
                role=User.Role.CUSTOMER,
                email__iexact=login_identifier
            ).first()

        if customer is None or not customer.check_password(password):
            raise serializers.ValidationError(
                "Invalid username/email or password."
            )

        if not customer.is_active:
            raise serializers.ValidationError(
                "Your account is inactive. Please verify your email."
            )

        if not customer.is_email_verified:
            raise serializers.ValidationError(
                "Please verify your email before logging in."
            )

        attrs["customer"] = customer

        return attrs



class AgentRegistrationSerializer(serializers.Serializer):

    username = serializers.CharField(max_length=150)

    email = serializers.EmailField()

    first_name = serializers.CharField(max_length=150)

    last_name = serializers.CharField(max_length=150)

    phone_number = serializers.CharField(
        max_length=15,
        required=False,
        allow_blank=True
    )

    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"}
    )

    confirm_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"}
    )

    def validate_username(self, value):

        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(
                "This username is already taken."
            )

        return value

    def validate_email(self, value):

        value = value.lower()

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "An account with this email already exists."
            )

        return value

    def validate(self, attrs):

        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")

        # Step 1: Check password confirmation
        if password != confirm_password:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })

        # Step 2: Validate password strength
        try:
            validate_password(password)
        except ValidationError as error:
            raise serializers.ValidationError({
                "password": error.messages
            })

        return attrs

    def create(self, validated_data):

        # Step 1: Remove confirmation field
        validated_data.pop("confirm_password")

        # Step 2: Remove raw password
        password = validated_data.pop("password")

        # Step 3: Create Agent account
        agent = User(
            **validated_data,
            role=User.Role.AGENT,
            is_active=False,
            is_email_verified=False
        )

        # Step 4: Hash password
        agent.set_password(password)

        # Step 5: Save Agent account
        agent.save()

        return agent


class CustomerRegistrationSerializer(serializers.Serializer):

    username = serializers.CharField(max_length=150)

    email = serializers.EmailField()

    first_name = serializers.CharField(max_length=150)

    last_name = serializers.CharField(max_length=150)

    phone_number = serializers.CharField(
        max_length=15,
        required=False,
        allow_blank=True
    )

    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"}
    )

    confirm_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"}
    )

    def validate_username(self, value):

        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(
                "This username is already taken."
            )

        return value

    def validate_email(self, value):

        value = value.lower()

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "An account with this email already exists."
            )

        return value

    def validate(self, attrs):

        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")

        # Step 1: Check password confirmation
        if password != confirm_password:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })

        # Step 2: Validate password strength
        try:
            validate_password(password)
        except ValidationError as error:
            raise serializers.ValidationError({
                "password": error.messages
            })

        return attrs

    def create(self, validated_data):

        # Step 1: Remove confirmation field
        validated_data.pop("confirm_password")

        # Step 2: Remove raw password
        password = validated_data.pop("password")

        # Step 3: Create Customer account
        customer = User(
            **validated_data,
            role=User.Role.CUSTOMER,
            is_active=False,
            is_email_verified=False
        )

        # Step 4: Hash password
        customer.set_password(password)

        # Step 5: Save Customer account
        customer.save()

        return customer