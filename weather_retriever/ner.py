# # References:
#     # https://huggingface.co/Leo97/KoELECTRA-small-v3-modu-ner

import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
import re


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

    @staticmethod
    def parse(ner_out):
        word = ""
        words = []
        for token in ner_out:
            subword = token["word"]
            pref, suff = token["entity"].split("-")
            if suff not in ["DT", "LC"]:
                continue

            if pref == "I" and words:
                word, prev_suff = words.pop()
                if suff != prev_suff:
                    continue

                if re.match(r"##(?!##)\S+", subword):
                    word += f"{subword[2:]}"
                else:
                    word += f" {subword}"
            elif pref == "B":
                word = subword
            words.append((word, suff))

        dates = []
        cities = []
        for word, entity in words:
            if entity == "DT":
                dates.append(word)
            else:
                cities.append(word)
        return dates, cities


if __name__ == "__main__":
    ner = NER()
    ner("내일과 모레 시드니 날씨 말해 줘.")
