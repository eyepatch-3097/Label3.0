GENERIC_EMAIL_DOMAINS = {
    'gmail.com', 'yahoo.com', 'yahoo.co.in', 'outlook.com', 'hotmail.com',
    'live.com', 'icloud.com', 'protonmail.com', 'zoho.com', 'rediffmail.com',
}


def split_email_domain(email: str) -> str:
    return email.split('@')[-1].lower().strip()


def is_generic_email_domain(domain: str) -> bool:
    return domain in GENERIC_EMAIL_DOMAINS
