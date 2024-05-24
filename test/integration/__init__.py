import uuid

UNAUTHORIZED_RESPONSE = {
    "detail": "Unauthorized. Only managers can access this endpoint."
}

NON_EXISTING_PRODUCT_ID = 1_000_000


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False
