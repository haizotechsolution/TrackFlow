import logging

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils.translation import gettext_lazy as _


logger = logging.getLogger(__name__)


class MerchantPasswordResetForm(PasswordResetForm):
    error_messages = {
        "unknown_merchant": _(
            "No merchant account found with this email address."
        ),
    }

    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                "autocomplete": "email",
                "class": "form-control",
            }
        ),
    )

    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()
        User = get_user_model()
        merchant_exists = User.objects.filter(
            email__iexact=email,
            role=User.ROLE_MERCHANT,
            is_active=True,
            merchant_profile__isnull=False,
        ).exists()

        if not merchant_exists:
            raise forms.ValidationError(
                self.error_messages["unknown_merchant"],
                code="unknown_merchant",
            )

        return email

    def get_users(self, email):
        User = get_user_model()
        email_field_name = User.get_email_field_name()
        active_merchants = User._default_manager.filter(
            **{
                f"{email_field_name}__iexact": email,
                "role": User.ROLE_MERCHANT,
                "is_active": True,
                "merchant_profile__isnull": False,
            }
        )
        return (
            user
            for user in active_merchants
            if user.has_usable_password()
        )

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        subject = loader.render_to_string(subject_template_name, context)
        subject = "".join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(
            subject,
            body,
            from_email,
            [to_email],
        )
        if html_email_template_name is not None:
            html_email = loader.render_to_string(
                html_email_template_name,
                context,
            )
            email_message.attach_alternative(html_email, "text/html")

        try:
            email_message.send()
        except Exception:
            logger.exception(
                "Failed to send merchant password reset email to user_id=%s",
                context["user"].pk,
            )
