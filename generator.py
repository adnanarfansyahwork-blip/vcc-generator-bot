import random
from datetime import datetime
from typing import List, Tuple, Optional

def calculate_luhn_check_digit(number_str: str) -> int:
    """
    Calculate Luhn MOD 10 check digit for a partial number string.
    """
    digits = [int(d) for d in number_str]
    # Reverse to apply double to every second digit from right
    reversed_digits = digits[::-1]
    total = 0
    for idx, digit in enumerate(reversed_digits):
        if idx % 2 == 0:  # first from right in partial number is doubled
            doubled = digit * 2
            total += doubled - 9 if doubled > 9 else doubled
        else:
            total += digit
    check_digit = (10 - (total % 10)) % 10
    return check_digit

def generate_card_number(bin_prefix: str, length: int = 16) -> str:
    """
    Generate a valid Luhn-compliant 16-digit card number from a given BIN.
    """
    # Clean non-digits
    clean_bin = "".join(filter(str.isdigit, bin_prefix))
    if not clean_bin:
        clean_bin = "5279262291"
        
    needed_random_digits = length - len(clean_bin) - 1
    if needed_random_digits < 0:
        clean_bin = clean_bin[:length - 1]
        needed_random_digits = 0
        
    random_part = "".join(str(random.randint(0, 9)) for _ in range(needed_random_digits))
    partial_number = clean_bin + random_part
    check_digit = calculate_luhn_check_digit(partial_number)
    return partial_number + str(check_digit)

def generate_expiry(start_years_ahead: int = 1, end_years_ahead: int = 6) -> Tuple[str, str]:
    """
    Generate random valid expiration month and year (e.g., '06', '2029').
    """
    current_year = datetime.now().year
    month = f"{random.randint(1, 12):02d}"
    year = str(random.randint(current_year + start_years_ahead, current_year + end_years_ahead))
    return month, year

def generate_cvv() -> str:
    """
    Generate random 3-digit CVV code.
    """
    return f"{random.randint(1, 999):03d}"

def generate_vcc(
    bin_prefix: str = "5279262291",
    count: int = 1,
    length: int = 16
) -> List[dict]:
    """
    Generate a list of VCC objects.
    """
    cards = []
    for _ in range(count):
        card_num = generate_card_number(bin_prefix, length)
        month, year = generate_expiry()
        cvv = generate_cvv()
        pipe_format = f"{card_num}|{month}|{year}|{cvv}"
        cards.append({
            "card_number": card_num,
            "month": month,
            "year": year,
            "cvv": cvv,
            "formatted": pipe_format
        })
    return cards
