
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

from .tokens import (
    admin_email_verification_token,
    agent_email_verification_token,
    customer_email_verification_token,
)


def send_admin_verification_email(user):

    # Step 1: Generate a unique user identifier
    uid = user.pk

    # Step 2: Generate the verification token
    token = admin_email_verification_token.make_token(user)

    # Step 3: Build the verification URL
    verification_path = reverse(
        "admin-email-verification",
        kwargs={
            "uid": uid,
            "token": token,
        }
    )

    verification_url = (
        f"http://127.0.0.1:8000{verification_path}"
    )

    # Step 4: Prepare email subject and message
    subject = "Verify Your Admin Email Address"

    message = (
        f"Hello {user.username},\n\n"
        "Please verify your email address by visiting the link below:\n\n"
        f"{verification_url}\n\n"
        "If you did not request this verification, please ignore this email."
    )

    # Step 5: Send the email
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

    return True


def send_agent_verification_email(user):

    # Step 1: Generate a unique user identifier
    uid = user.pk

    # Step 2: Generate the verification token
    token = agent_email_verification_token.make_token(user)

    # Step 3: Build the verification URL
    verification_path = reverse(
        "agent-email-verification",
        kwargs={
            "uid": uid,
            "token": token,
        }
    )

    verification_url = (
        f"http://127.0.0.1:8000{verification_path}"
    )

    # Step 4: Prepare email subject and message
    subject = "Verify Your Agent Email Address"

    message = (
        f"Hello {user.username},\n\n"
        "Please verify your email address by visiting the link below:\n\n"
        f"{verification_url}\n\n"
        "If you did not request this verification, please ignore this email."
    )

    # Step 5: Send the email
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

    return True


def send_customer_verification_email(user):

    # Step 1: Generate a unique user identifier
    uid = user.pk

    # Step 2: Generate the verification token
    token = customer_email_verification_token.make_token(user)

    # Step 3: Build the verification URL
    verification_path = reverse(
        "customer-email-verification",
        kwargs={
            "uid": uid,
            "token": token,
        }
    )

    verification_url = (
        f"http://127.0.0.1:8000{verification_path}"
    )

    # Step 4: Prepare email subject and message
    subject = "Verify Your Customer Email Address"

    message = (
        f"Hello {user.username},\n\n"
        "Please verify your email address by visiting the link below:\n\n"
        f"{verification_url}\n\n"
        "If you did not request this verification, please ignore this email."
    )

    # Step 5: Send the email
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

    return True