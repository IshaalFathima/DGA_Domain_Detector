"""
DGA SENTINEL — Domain normalization and public-suffix-aware DGA label extraction.

The same normalization is applied consistently for:
  - feature extraction
  - DGA-label extraction
  - TF-IDF inference
  - API output
"""

import tldextract


def clean_domain(domain: str) -> str:
    """
    Deterministic domain normalization.

    - Converts to lowercase
    - Strips leading/trailing whitespace
    - Removes a trailing dot (FQDN notation)
    - Returns empty string for empty or non-string input
    """
    if not isinstance(domain, str):
        return ""
    domain = domain.strip().lower()
    # Remove trailing dot for fully-qualified domain names
    if domain.endswith("."):
        domain = domain[:-1]
    return domain


def extract_dga_label_v2(domain: str) -> str:
    """
    Public-suffix-aware DGA label extraction.

    Uses tldextract so that domains like example.co.uk, example.co.nz,
    and example.co.id are handled correctly (the registered domain label
    is returned, not naively the second-last component).

    For domains with a subdomain, the first non-empty subdomain label is
    returned, which is the component most likely to be algorithmically
    generated.
    """
    domain = clean_domain(domain)
    if not domain:
        return ""

    ext = tldextract.extract(domain)
    registered_label = ext.domain
    subdomain = ext.subdomain

    if subdomain:
        sub_labels = subdomain.split(".")
        for label in sub_labels:
            if label:
                return label

    return registered_label
