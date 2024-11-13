from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers.receipt import ReceiptSerializer
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.permissions import AllowAny
from PIL import Image
import numpy as np
import cv2
from paddleocr import PaddleOCR
import logging

logger = logging.getLogger(__name__)
import os


class ReceiptView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ReceiptSerializer(data=request.data)
        if serializer.is_valid():
            receipt = serializer.validated_data["receipt"]
            # Read the image data once
            image_data = receipt.read()
            image = cv2.cvtColor(
                np.array(Image.open(ContentFile(image_data))), cv2.COLOR_RGB2GRAY
            )
            # Access PicscanConfig and retrieve the ocr instance
            logger.info("OCR running")
            paddle_ocr = PaddleOCR(
                use_angle_cls=True,
                use_tensorrt=True,
                lang="id",
                use_gpu=False,
                show_log=False,
            )
            result = paddle_ocr.ocr(image, cls=True)
            path = default_storage.save(
                "receipts/originals/" + receipt.name, ContentFile(image_data)
            )
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
