# # References:
#     # https://huggingface.co/Leo97/KoELECTRA-small-v3-modu-ner

import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline


class NER(object):
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(
            "Leo97/KoELECTRA-small-v3-modu-ner",
        )
        self.model = AutoModelForTokenClassification.from_pretrained(
            "Leo97/KoELECTRA-small-v3-modu-ner",
        )
        self.ner_pipeline = pipeline("ner", model=self.model, tokenizer=self.tokenizer)

    @torch.inference_mode()
    def __call__(self, text):
        return self.ner_pipeline(text)
