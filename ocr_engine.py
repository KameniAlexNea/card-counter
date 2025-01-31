from PIL import Image
import easyocr
import io
from loguru import logger


class EasyOCRReader:
    def __init__(self):
        self.reader = easyocr.Reader(["fr", "en"], gpu=False)

    def chat(self, image: Image.Image):
        # Convert image to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        # Call readtext with image bytes
        texts = self.reader.readtext(img_byte_arr, detail=0)
        logger.info(" ".join(texts))
        return " ".join(texts)

ocr_model = EasyOCRReader()
