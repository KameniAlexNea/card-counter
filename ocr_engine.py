# Load model directly
import os
import torch
from transformers import AutoModel, AutoTokenizer
from PIL import Image
import uuid

UPLOAD_FOLDER = "./uploads"
RESULTS_FOLDER = "./results"

for folder in [UPLOAD_FOLDER, RESULTS_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

class OCRModel:
    tokenizer: AutoTokenizer
    model: AutoModel

    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained('ucaslcl/GOT-OCR2_0', trust_remote_code=True)
        self.model = AutoModel.from_pretrained('ucaslcl/GOT-OCR2_0', trust_remote_code=True, low_cpu_mem_usage=True, device_map='cuda' if torch.cuda.is_available() else "cpu", use_safetensors=True, pad_token_id=self.tokenizer.eos_token_id)
        self.model = self.model.eval()
        if torch.cuda.is_available():
            self.model = self.model.cuda()

    def chat(self, image: Image.Image) -> str:
        unique_id = str(uuid.uuid4())
        image_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}.png")
        result_path = os.path.join(RESULTS_FOLDER, f"{unique_id}.txt")

        image.save(image_path)
        
        res = self.model.chat(self.tokenizer, image_path, ocr_type='ocr')
        with open(result_path, 'w') as f:
            f.write(res)
        return res

ocr_model = OCRModel()
