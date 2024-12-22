import six
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        """
        Hash using user pk, timestamp, email, and verification status
        to ensure token becomes invalid if any of these change
        """
        return (
            six.text_type(user.pk)
            + six.text_type(timestamp)
            + six.text_type(user.email)
            + six.text_type(user.is_verified)
            + six.text_type(user.password)
        )


email_verification_token = EmailVerificationTokenGenerator()
