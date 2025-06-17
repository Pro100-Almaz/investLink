import fastapi

from src.utilities.messages.exceptions.http.exc_details import http_500_server_error_details

async def http_500_server_side_error(error_msg: str) -> Exception:
    return fastapi.HTTPException(
        status_code=fastapi.status.HTTP_404_NOT_FOUND,
        detail=http_500_server_error_details(error_msg=error_msg),
    )