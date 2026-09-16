"""
DGA SENTINEL — Exact 24 structural feature extraction.

Feature definitions, order, and logic are FROZEN.
Do NOT alter feature names, order, or computation logic.
"""

import math
from collections import Counter

from domain_utils import clean_domain, extract_dga_label_v2

VOWELS = set("aeiou")


def shannon_entropy(s: str) -> float:
    """Compute Shannon entropy (bits) for string s."""
    if not s:
        return 0.0
    counts = Counter(s)
    n = len(s)
    return -sum(
        (count / n) * math.log2(count / n)
        for count in counts.values()
    )


def max_consecutive(s: str, condition) -> int:
    """Return the length of the longest consecutive run satisfying condition."""
    best = 0
    current = 0
    for char in s:
        if condition(char):
            current += 1
            best = max(best, current)
        else:
            current = 0
    return best


def extract_features(domain: str, dga_string: str | None = None) -> dict:
    """
    Extract exactly 24 structural features in the frozen order.

    Parameters
    ----------
    domain      : cleaned domain string
    dga_string  : pre-extracted DGA label; if None it is derived via
                  extract_dga_label_v2(domain)

    Returns
    -------
    dict mapping each of the 24 feature names to its value.
    """
    domain = clean_domain(domain)

    if dga_string is None:
        dga_string = extract_dga_label_v2(domain)

    # Build the analysis string s from the DGA label
    s = str(dga_string).lower().strip()
    s = "".join(c for c in s if c.isalnum() or c == "-")

    length = len(s)

    labels = domain.split(".") if domain else []
    dot_count = domain.count(".")
    subdomain_count = max(len(labels) - 2, 0)

    special_char_count = sum(not c.isalnum() for c in domain)
    special_char_ratio = (
        special_char_count / len(domain) if domain else 0
    )

    # -----------------------------------------------------------------------
    # Zero-length guard
    # -----------------------------------------------------------------------
    if length == 0:
        return {
            "domain_length": 0,
            "num_digits": 0,
            "digit_ratio": 0.0,
            "num_letters": 0,
            "num_vowels": 0,
            "num_consonants": 0,
            "vowel_ratio": 0.0,
            "consonant_ratio": 0.0,
            "num_special_chars": special_char_count,
            "special_char_ratio": special_char_ratio,
            "hyphen_count": domain.count("-"),
            "dot_count": dot_count,
            "subdomain_count": subdomain_count,
            "unique_chars": 0,
            "unique_char_ratio": 0.0,
            "shannon_entropy": 0.0,
            "max_consecutive_digits": 0,
            "max_consecutive_consonants": 0,
            "character_transitions": 0,
            "repeated_chars": 0,
            "repeated_ratio": 0.0,
            "max_consecutive_vowels": 0,
            "letter_digit_transitions": 0,
            "digit_letter_transitions": 0,
        }

    # -----------------------------------------------------------------------
    # Core counts
    # -----------------------------------------------------------------------
    num_digits = sum(c.isdigit() for c in s)
    num_letters = sum(c.isalpha() for c in s)
    num_vowels = sum(c in VOWELS for c in s)
    num_consonants = sum(c.isalpha() and c not in VOWELS for c in s)
    unique_chars = len(set(s))
    repeated_chars = length - unique_chars

    # -----------------------------------------------------------------------
    # Ratios
    # -----------------------------------------------------------------------
    digit_ratio = num_digits / length
    vowel_ratio = num_vowels / length
    consonant_ratio = (
        num_consonants / num_letters if num_letters else 0.0
    )
    unique_char_ratio = unique_chars / length
    repeated_ratio = repeated_chars / length

    # -----------------------------------------------------------------------
    # Consecutive run features
    # -----------------------------------------------------------------------
    max_consecutive_digits = max_consecutive(s, lambda c: c.isdigit())
    max_consecutive_vowels = max_consecutive(
        s, lambda c: c.isalpha() and c in VOWELS
    )
    max_consecutive_consonants = max_consecutive(
        s, lambda c: c.isalpha() and c not in VOWELS
    )

    # -----------------------------------------------------------------------
    # Transition features
    # -----------------------------------------------------------------------
    letter_digit_transitions = 0
    digit_letter_transitions = 0
    character_transitions = 0

    for i in range(1, len(s)):
        previous = s[i - 1]
        current = s[i]

        if previous.isalpha() and current.isdigit():
            letter_digit_transitions += 1
        if previous.isdigit() and current.isalpha():
            digit_letter_transitions += 1
        if previous != current:
            character_transitions += 1

    return {
        "domain_length": length,
        "num_digits": num_digits,
        "digit_ratio": digit_ratio,
        "num_letters": num_letters,
        "num_vowels": num_vowels,
        "num_consonants": num_consonants,
        "vowel_ratio": vowel_ratio,
        "consonant_ratio": consonant_ratio,
        "num_special_chars": special_char_count,
        "special_char_ratio": special_char_ratio,
        "hyphen_count": s.count("-"),
        "dot_count": dot_count,
        "subdomain_count": subdomain_count,
        "unique_chars": unique_chars,
        "unique_char_ratio": unique_char_ratio,
        "shannon_entropy": shannon_entropy(s),
        "max_consecutive_digits": max_consecutive_digits,
        "max_consecutive_consonants": max_consecutive_consonants,
        "character_transitions": character_transitions,
        "repeated_chars": repeated_chars,
        "repeated_ratio": repeated_ratio,
        "max_consecutive_vowels": max_consecutive_vowels,
        "letter_digit_transitions": letter_digit_transitions,
        "digit_letter_transitions": digit_letter_transitions,
    }
