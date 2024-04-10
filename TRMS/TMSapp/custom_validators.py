from django.core.exceptions import ValidationError
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _


class ComprehensivePasswordValidator:
    """
    Validate whether the password meets the comprehensive requirements.
    """
    def validate(self, password, user=None):
        special_characters = "!@#$%^&*()-_=+[]{}|;:'\",.<>/?`~"
        
        errors = []
        if len(password) < 8:
            errors.append(force_str(_("at least 8 characters")))
        if not any(char.isupper() for char in password):
            errors.append(force_str(_("at least one uppercase letter")))
        if not any(char.islower() for char in password):
            errors.append(force_str(_("at least one lowercase letter")))
        if not any(char.isdigit() for char in password):
            errors.append(force_str(_("at least one digit")))
        if not any(char in special_characters for char in password):
            errors.append(force_str(_("at least one special character: %(special_characters)s") % {'special_characters': special_characters}))

        if errors:
            raise ValidationError(_("Your password must contain %(requirements)s.") % {'requirements': ", ".join(errors)})

    def get_help_text(self):
        return _(
            "Your password must contain at least 8 characters, "
            "include at least one uppercase letter, one lowercase letter, "
            "one digit, and one special character: !@#$%^&*()-_=+[]{}|;:'\",.<>/?`~"
        )
