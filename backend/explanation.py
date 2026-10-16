"""
DGA SENTINEL — Deterministic feature-based explanation system.

Observations are generated exclusively from actual extracted feature values.
No generic explanations are returned for every domain.
"""


def generate_observations(features: dict, classification: str) -> list[str]:
    """
    Produce a deterministic list of observations supported by the actual
    feature values.  Only observations whose thresholds are crossed are
    included — nothing is emitted unconditionally.

    Parameters
    ----------
    features       : the 24-feature dict returned by extract_features()
    classification : "DGA" or "NOT DGA-LIKE"

    Returns
    -------
    List of human-readable observation strings.
    """
    observations: list[str] = []

    domain_length = features.get("domain_length", 0)

    if domain_length == 0:
        return ["Insufficient domain label length for detailed structural analysis."]

    entropy = features.get("shannon_entropy", 0.0)
    digit_ratio = features.get("digit_ratio", 0.0)
    vowel_ratio = features.get("vowel_ratio", 0.0)
    consonant_ratio = features.get("consonant_ratio", 0.0)
    num_letters = features.get("num_letters", 0)
    unique_char_ratio = features.get("unique_char_ratio", 0.0)
    character_transitions = features.get("character_transitions", 0)
    max_consecutive_digits = features.get("max_consecutive_digits", 0)
    max_consecutive_consonants = features.get("max_consecutive_consonants", 0)
    letter_digit_transitions = features.get("letter_digit_transitions", 0)
    digit_letter_transitions = features.get("digit_letter_transitions", 0)

    # -----------------------------------------------------------------------
    # Shannon entropy
    # -----------------------------------------------------------------------
    if entropy > 3.5:
        observations.append(
            "High character entropy suggests a less predictable character sequence."
        )
    elif entropy < 2.0 and domain_length > 4:
        observations.append(
            "Low character entropy indicates a repetitive or low-diversity character pattern."
        )

    # -----------------------------------------------------------------------
    # Digit ratio
    # -----------------------------------------------------------------------
    if digit_ratio > 0.30:
        observations.append(
            "High digit ratio is often associated with algorithmically generated patterns."
        )

    # -----------------------------------------------------------------------
    # Vowel ratio
    # -----------------------------------------------------------------------
    if vowel_ratio < 0.18 and domain_length > 5:
        observations.append(
            "Low vowel ratio indicates unusual character composition."
        )

    # -----------------------------------------------------------------------
    # Consonant density (relative to letters only)
    # -----------------------------------------------------------------------
    if consonant_ratio > 0.80 and num_letters > 3:
        observations.append(
            "High consonant density is characteristic of algorithmically generated strings."
        )

    # -----------------------------------------------------------------------
    # Domain length
    # -----------------------------------------------------------------------
    if domain_length > 20:
        observations.append(
            "Elevated domain length is consistent with algorithmically generated domain patterns."
        )

    # -----------------------------------------------------------------------
    # Character transition rate
    # -----------------------------------------------------------------------
    if domain_length > 1:
        transition_rate = character_transitions / (domain_length - 1)
        if transition_rate > 0.85:
            observations.append(
                "Elevated character transition rate contributes to DGA-like characteristics."
            )

    # -----------------------------------------------------------------------
    # Consecutive digit runs
    # -----------------------------------------------------------------------
    if max_consecutive_digits >= 4:
        observations.append(
            f"Long consecutive digit sequence ({max_consecutive_digits} digits) detected."
        )

    # -----------------------------------------------------------------------
    # Consecutive consonant runs
    # -----------------------------------------------------------------------
    if max_consecutive_consonants >= 6:
        observations.append(
            f"Long consecutive consonant sequence ({max_consecutive_consonants} consonants) detected."
        )

    # -----------------------------------------------------------------------
    # Letter-digit alternations
    # -----------------------------------------------------------------------
    total_ld = letter_digit_transitions + digit_letter_transitions
    if total_ld >= 3:
        observations.append(
            "Multiple letter-digit alternations are characteristic of mixed-pattern generation."
        )

    # -----------------------------------------------------------------------
    # High character diversity
    # -----------------------------------------------------------------------
    if unique_char_ratio > 0.85 and domain_length > 6:
        observations.append(
            "High character diversity suggests generated or high-randomness patterns."
        )

    return observations
