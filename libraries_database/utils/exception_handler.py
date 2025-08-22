from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status as drf_status
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns consistent error response structure.
    """
    # Call DRF's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Log the error (optional)
        logger.warning(f"Exception in {context['view'].__class__.__name__}: {exc}")

        # Uniform error response structure
        response.data = {
            "success": False,
            "status_code": response.status_code,
            "errors": response.data
        }
    else:
        # If DRF didn't handle it, return a generic 500 error
        logger.error(f"Unhandled exception: {exc}", exc_info=True)

        return Response({
            "success": False,
            "status_code": drf_status.HTTP_500_INTERNAL_SERVER_ERROR,
            "errors": {"detail": "Internal server error. Please contact support."}
        }, status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response
