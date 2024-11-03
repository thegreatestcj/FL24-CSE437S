from django import template

register = template.Library()

@register.filter
def mask_email(email):
    """Masks the email to show only the first two characters and the domain."""
    try:
        username, domain = email.split('@')
        masked_username = f"{username[:2]}****"
        return f"{masked_username}@{domain}"
    except ValueError:
        return email