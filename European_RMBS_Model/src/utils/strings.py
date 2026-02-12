import re
import pandas as pd



def clean_string(s: str) -> str:
    """
    Cleans a string by removing whitespace and special characters.
    Does NOT lowercase - that happens later after case detection.

    Args:
        s (str): Input string

    Returns:
        str: Cleaned string with original case preserved
    """
    # Strip leading/trailing spaces
    s = s.strip()

    # REGEX: Remove newlines, tabs, carriage returns
    # Pattern: r'[\n\t\r]'
    # [...]  = Character class: matches any character inside brackets
    # \n     = Newline
    # \t     = Tab
    # \r     = Carriage return
    s = re.sub(r'[\n\t\r]', '', s)

    # Remove quotes and backslashes using string methods
    s = s.replace("'", "").replace('"', "").replace("\\", "")

    # REGEX: Replace multiple spaces with single space
    # Pattern: r'\s+'
    # \s     = Any whitespace character (space, tab, newline, etc.)
    # +      = One or more of the preceding pattern
    # Result: "hello    world" -> "hello world"
    s = re.sub(r'\s+', ' ', s)

    return s


def to_snake_case(s: str) -> str:
    """
    Converts a string to snake_case format.
    Handles camelCase, PascalCase, kebab-case, and space-separated strings.
    Also handles acronyms correctly (e.g., "HTTPResponse" -> "http_response").

    Args:
        s (str): Input string (cleaned but NOT lowercased)

    Returns:
        str: String in snake_case format
    """
    # REGEX 1: Handle transition from lowercase (or digit) to uppercase
    # Pattern: r'([a-z0-9])([A-Z])'
    # ([a-z0-9]) = Capture group 1: any lowercase letter or digit
    # ([A-Z])    = Capture group 2: any uppercase letter
    # This matches the boundary like "camel" + "Case" in "camelCase"
    # Replacement: r'\1_\2' means "group1 + underscore + group2"
    # Example: "camelCase" -> "camel_Case"
    # Example: "test123Value" -> "test123_Value"
    s = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s)

    # REGEX 2: Handle transition from multiple uppercase to lowercase
    # Pattern: r'([A-Z]+)([A-Z][a-z])'
    # ([A-Z]+)      = Capture group 1: one or more uppercase letters
    # ([A-Z][a-z])  = Capture group 2: uppercase letter followed by lowercase
    # This handles acronyms like "HTTPResponse" -> "HTTP_Response"
    # The last uppercase letter of the acronym stays with the next word
    # Replacement: r'\1_\2' means "group1 + underscore + group2"
    # Example: "HTTPResponse" -> "HTTP_Response"
    # Example: "XMLParser" -> "XML_Parser"
    s = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', s)

    # NOW convert to lowercase (after detecting all case boundaries)
    s = s.lower()

    # REGEX 3: Replace separators with underscores
    # Pattern: r'[-/\\,.\s]+'
    # [...]  = Character class
    # -      = Hyphen
    # /      = Forward slash
    # \\     = Backslash (escaped)
    # ,      = Comma
    # .      = Period
    # \s     = Whitespace
    # +      = One or more (groups consecutive separators)
    s = re.sub(r'[-/\\,.\s]+', '_', s)

    # REGEX 4: Remove non-alphanumeric characters (except underscore)
    # Pattern: r'[^a-z0-9_]'
    # [^...] = Negated character class (match anything NOT in brackets)
    # a-z    = Lowercase letters
    # 0-9    = Digits
    # _      = Underscore
    # Removes: @, #, $, %, &, *, etc.
    s = re.sub(r'[^a-z0-9_]', '', s)

    # REGEX 5: Collapse multiple underscores into one
    # Pattern: r'_+'
    # _      = Underscore
    # +      = One or more
    # Example: "hello___world" -> "hello_world"
    s = re.sub(r'_+', '_', s)

    # Remove leading/trailing underscores
    s = s.strip('_')

    return s


def clean_and_snake_case(s: str) -> str:
    """
    Convenience function that cleans a string and converts to snake_case.
    Handles camelCase/PascalCase conversion properly.

    Args:
        s (str): Input string

    Returns:
        str: Cleaned snake_case string
    """
    s = clean_string(s)  # Clean but preserve case
    s = to_snake_case(s)  # Detect case boundaries, then lowercase
    return s


# -----------------------------
# ALTERNATIVE: Single function version
# -----------------------------

def clean_to_snake_case(s: str) -> str:
    """
    All-in-one function that cleans and converts to snake_case.

    Args:
        s (str): Input string

    Returns:
        str: Cleaned snake_case string
    """
    # Strip leading/trailing spaces
    s = s.strip()

    # REGEX: Remove newlines, tabs, carriage returns
    # Pattern: r'[\n\t\r]'
    s = re.sub(r'[\n\t\r]', '', s)

    # Remove quotes and backslashes
    s = s.replace("'", "").replace('"', "").replace("\\", "")

    # REGEX: Replace multiple spaces with single space
    # Pattern: r'\s+'
    s = re.sub(r'\s+', ' ', s)

    # REGEX 1: Handle lowercase/digit to uppercase transition
    # Pattern: r'([a-z0-9])([A-Z])'
    # Example: "camelCase" -> "camel_Case"
    s = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s)

    # REGEX 2: Handle acronym to word transition
    # Pattern: r'([A-Z]+)([A-Z][a-z])'
    # Example: "HTTPResponse" -> "HTTP_Response"
    s = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', s)

    # Convert to lowercase AFTER case detection
    s = s.lower()

    # REGEX: Replace separators with underscores
    # Pattern: r'[-/\\,.\s]+'
    s = re.sub(r'[-/\\,.\s]+', '_', s)

    # REGEX: Remove non-alphanumeric characters (except underscore)
    # Pattern: r'[^a-z0-9_]'
    s = re.sub(r'[^a-z0-9_]', '', s)

    # REGEX: Collapse multiple underscores
    # Pattern: r'_+'
    s = re.sub(r'_+', '_', s)

    # Remove leading/trailing underscores
    s = s.strip('_')

    return s
