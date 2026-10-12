
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


class AnswerGenerator:

    def __init__(self):

        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        self.model_name = "google/flan-t5-base"

        print(
            f"Loading {self.model_name} "
            f"on {self.device}..."
        )

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name
        )

        self.model = (
            AutoModelForSeq2SeqLM
            .from_pretrained(self.model_name)
            .to(self.device)
        )

        self.model.eval()

        print("✅ Generator loaded")

    def generate(
        self,
        question,
        retrieved_titles,
        corpus_dict
    ):

        context_parts = []

        for title in retrieved_titles:

            if title in corpus_dict:

                context_parts.append(
                    f"Title: {title}\n"
                    f"{corpus_dict[title]}"
                )

        context = "\n\n".join(
            context_parts
        )

        prompt = f"""
Answer the question using only the context below.

Give a short answer.
Do not explain your reasoning.

Context:
{context}

Question:
{question}

Answer:
""".strip()

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=1024
        ).to(self.device)

        with torch.no_grad():

            output = self.model.generate(
                **inputs,
                max_new_tokens=40,
                do_sample=False
            )

        answer = self.tokenizer.decode(
            output[0],
            skip_special_tokens=True
        ).strip()

        return answer
