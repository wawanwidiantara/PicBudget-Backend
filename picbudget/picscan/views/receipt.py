from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers.receipt import ReceiptSerializer
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.permissions import AllowAny

from django.apps import apps
from PIL import Image
import numpy as np
import cv2
from ..utils.processors import (
    image_processing,
    extract_text,
)

import os
from paddleocr import PaddleOCR

import logging

logger = logging.getLogger(__name__)


class ReceiptView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ReceiptSerializer(data=request.data)
        if serializer.is_valid():
            receipt = serializer.validated_data["receipt"]
            image_data = receipt.read()
            path = default_storage.save(
                "receipts/originals/" + receipt.name, ContentFile(image_data)
            )

            # Image processing
            logger.info("Image processing running")
            image = cv2.cvtColor(
                np.array(Image.open(ContentFile(image_data))), cv2.COLOR_RGB2BGR
            )
            image_processor = image_processing.ImageProcessor(image)
            image = image_processor.preprocess_image()

            # OCR
            logger.info("OCR running")
            extract_text_processor = extract_text.TextExtractor(image)
            extracted_text = extract_text_processor.extracted_text

            # Model processing
            logger.info("Model processing running")
            picscan_app = apps.get_app_config("picscan")
            processor = picscan_app.receipt_processor
            result = processor.process_receipt(extracted_text)

            # return absolute path to the image
            url = request.build_absolute_uri(default_storage.url(path))
            return Response(
                {
                    "path": url,
                    "result": result,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
