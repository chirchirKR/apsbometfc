import re


def normalize_kenyan_phone(input):
    """
    Normalize a Kenyan phone number to:
    2547XXXXXXXX or 2541XXXXXXXX

    Returns normalized phone number if valid, otherwise None.
    """

    if not isinstance(input, str):
        return None

    # Remove spaces, hyphens, parentheses and dots
    phone = re.sub(r'[\s\-().]', '', input)

    # Normalize country code / leading zero
    if phone.startswith("+254"):
        phone = phone[1:]

    elif phone.startswith("254"):
        pass

    elif phone.startswith("0"):
        phone = "254" + phone[1:]

    elif re.fullmatch(r'[71]\d{8}', phone):
        phone = "254" + phone

    else:
        return None

    # Validate Kenyan mobile number
    if not re.fullmatch(r'254[71]\d{8}', phone):
        return None

    return phone


def is_valid_kenyan_phone(input):
    """
    Check whether a Kenyan phone number is valid.
    """
    return normalize_kenyan_phone(input) is not None

"""
# Examples
print(is_valid_kenyan_phone("+254712345678"))  # True
print(is_valid_kenyan_phone("254712345678"))   # True
print(is_valid_kenyan_phone("0712345678"))     # True
print(is_valid_kenyan_phone("0112345678"))     # True
print(is_valid_kenyan_phone("712345678"))      # True
print(is_valid_kenyan_phone("112345678"))      # True

print(is_valid_kenyan_phone("0812345678"))     # False
print(is_valid_kenyan_phone("071234567"))      # False
print(is_valid_kenyan_phone("+254812345678"))  # False

print(normalize_kenyan_phone("0712 345 678"))
# 254712345678
"""