# app/utils/validation.py
def validate_update_payload(payload: dict, allowed_fields: set) -> dict:
    """
    Validate the update payload to allow only certain fields.

    Args:
        payload (dict): The input dictionary containing user-provided fields.
        allowed_fields (set): A set of fields allowed for updates.

    Returns:
        dict: A filtered dictionary containing only allowed fields.
    """
    return {key: value for key, value in payload.items() if key in allowed_fields}
