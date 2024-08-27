import re

def mask_email(email):
    """Mask the email address by hiding the username."""
    parts = email.split("@")
    masked_email = parts[0][0] + "***@" + parts[1]
    return masked_email

def mask_credit_card(card_number):
    """Mask the credit card number by hiding the middle digits."""
    return card_number[:4] + " **** **** " + card_number[-4:]

def mask_sin(ssn):
    """Mask the SIN by hiding the first five digits."""
    return "***-**-" + ssn[-4:]

def mask_phone_number(phone_number):
    """Mask the phone number by hiding the middle digits."""
    if phone_number and len(phone_number) >= 7:
        return phone_number[:2] + "*****" + phone_number[-2:]
    return phone_number

def mask_data(row):
    """Apply masking logic to a row of data."""
    masked_row = {}
    for key, value in row.items():
        if re.search(r'email', key, re.IGNORECASE):
            masked_row[key] = mask_email(value)
        elif re.search(r'credit', key, re.IGNORECASE):
            masked_row[key] = mask_credit_card(value)
        elif re.search(r'ssn', key, re.IGNORECASE):
            masked_row[key] = mask_sin(value)
        elif re.search(r'phone', key, re.IGNORECASE):
            masked_row[key] = mask_phone_number(value)
        else:
            masked_row[key] = value
    return masked_row
