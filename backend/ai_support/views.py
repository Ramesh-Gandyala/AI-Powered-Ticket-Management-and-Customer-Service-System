from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .services import get_ultron_ollama_response

import logging
logger = logging.getLogger(__name__)

class ULTRONChatAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        customer_message = request.data.get("message")

        if not customer_message:
            return Response(
                {
                    "success": False,
                    "message": "Please provide a message."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            ultron_response = get_ultron_ollama_response(customer_message)

            return Response(
                {
                    "success": True,
                    "assistant": "ULTRON",
                    "customer_message": customer_message,
                    "response": ultron_response
                },
                status=status.HTTP_200_OK
            )

        except Exception:
            logger.exception("ULTRON failed to process the customer request.")

            return Response(
                {
                    "success": False,
                    "message": "ULTRON is temporarily unavailable. Please try again later."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )