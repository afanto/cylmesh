"""
Utility classes and functions for the mesh generator.
"""

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class ColorFormatter:
    """ANSI color constants for formatted output."""
    
    BOLD = "\033[1m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    MAGENTA = "\033[95m"
    RESET = "\033[0m"


def validate_positive_float(value, name):
    """Validate that a value is a positive float."""
    if value <= 0:
        raise ValidationError(f"{name} must be positive")
    return value


def validate_positive_list(values, name):
    """Validate that all values in a list are positive."""
    if any(v <= 0 for v in values):
        raise ValidationError(f"All {name} must be positive")
    return values


def validate_matching_lengths(list1, list2, name1, name2):
    """Validate that two lists have the same length."""
    if len(list1) != len(list2):
        raise ValidationError(f"Number of {name1} ({len(list1)}) must match number of {name2} ({len(list2)})")
    return True
