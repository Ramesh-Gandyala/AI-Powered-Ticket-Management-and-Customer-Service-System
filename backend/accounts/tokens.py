
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class AdminEmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """
    Generates secure tokens for Admin email verification.
    """

    def _make_hash_value(self, user, timestamp):
        return (
            str(user.pk)
            + str(timestamp)
            + str(user.is_email_verified)
            + str(user.is_active)
            + str(user.email)
        )


admin_email_verification_token = AdminEmailVerificationTokenGenerator()


class AgentEmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """
    Generates secure tokens for Agent email verification.
    """

    def _make_hash_value(self, user, timestamp):
        return (
            str(user.pk)
            + str(timestamp)
            + str(user.is_email_verified)
            + str(user.is_active)
            + str(user.email)
        )


agent_email_verification_token = AgentEmailVerificationTokenGenerator()


class CustomerEmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """
    Generates secure tokens for Customer email verification.
    """

    def _make_hash_value(self, user, timestamp):
        return (
            str(user.pk)
            + str(timestamp)
            + str(user.is_email_verified)
            + str(user.is_active)
            + str(user.email)
        )


customer_email_verification_token = CustomerEmailVerificationTokenGenerator()