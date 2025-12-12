from typing import Dict, Any, Tuple, List

VALID_SKIN_TYPES = ['oily', 'dry', 'combination', 'normal', 'sensitive']
VALID_CONCERNS = ['acne', 'redness', 'wrinkles', 'dark-spots', 'dryness', 'oiliness', 'sensitivity', 'pores', 'aging',
                  'dullness']


def validate_quiz_input(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate quiz/profile input data

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Check required fields
    if 'user_id' not in data:
        errors.append("user_id is required")

    if 'skin_type' not in data:
        errors.append("skin_type is required")
    elif data['skin_type'].lower() not in VALID_SKIN_TYPES:
        errors.append(f"skin_type must be one of: {', '.join(VALID_SKIN_TYPES)}")

    # Validate concerns
    if 'concerns' in data:
        if not isinstance(data['concerns'], list):
            errors.append("concerns must be a list")
        else:
            invalid_concerns = [c for c in data['concerns'] if c.lower() not in VALID_CONCERNS]
            if invalid_concerns:
                errors.append(f"Invalid concerns: {', '.join(invalid_concerns)}")

    # Validate budget
    if 'budget_min' in data and 'budget_max' in data:
        try:
            budget_min = float(data['budget_min'])
            budget_max = float(data['budget_max'])
            if budget_min > budget_max:
                errors.append("budget_min cannot be greater than budget_max")
            if budget_min < 0 or budget_max < 0:
                errors.append("budget values must be positive")
        except (ValueError, TypeError):
            errors.append("budget values must be numeric")

    # Validate ingredients
    if 'preferred_ingredients' in data:
        if not isinstance(data['preferred_ingredients'], list):
            errors.append("preferred_ingredients must be a list")

    if 'avoided_ingredients' in data:
        if not isinstance(data['avoided_ingredients'], list):
            errors.append("avoided_ingredients must be a list")

    return len(errors) == 0, errors


def validate_recommend_input(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate recommendation input data

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Must have either user_id or full profile
    has_user_id = 'user_id' in data
    has_skin_type = 'skin_type' in data

    if not has_user_id and not has_skin_type:
        errors.append("Either user_id or skin_type must be provided")

    # If providing profile directly, validate it
    if has_skin_type:
        if data['skin_type'].lower() not in VALID_SKIN_TYPES:
            errors.append(f"skin_type must be one of: {', '.join(VALID_SKIN_TYPES)}")

        if 'concerns' in data:
            if not isinstance(data['concerns'], list):
                errors.append("concerns must be a list")

        if 'budget_min' in data and 'budget_max' in data:
            try:
                budget_min = float(data['budget_min'])
                budget_max = float(data['budget_max'])
                if budget_min > budget_max:
                    errors.append("budget_min cannot be greater than budget_max")
            except (ValueError, TypeError):
                errors.append("budget values must be numeric")

    return len(errors) == 0, errors


def sanitize_string(value: str, max_length: int = 255) -> str:
    """Sanitize string input"""
    if not value:
        return ""
    return str(value).strip()[:max_length]


def sanitize_list(value: Any) -> List[str]:
    """Sanitize list input"""
    if not value:
        return []
    if not isinstance(value, list):
        return []
    return [str(item).strip().lower() for item in value if item]