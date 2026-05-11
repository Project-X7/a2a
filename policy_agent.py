#import base64
#from pathlib import Path
import litellm
from helpers import setup_env, pdf_to_text
#import io


class PolicyAgent:
    def __init__(self) -> None:
        setup_env()
        # with Path("/Users/priyakhoesial/Dev/projects/agentic-ai/protocols/agent2agent/test data/2026AnthemgHIPSBC.pdf").open("rb") as file:
        #     self.file_content = base64.standard_b64encode(file.read()).decode("utf-8")
        # pdf_bytes = base64.b64decode(self.file_content)
        # reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        self.file_content_text = pdf_to_text("/Users/priyakhoesial/Dev/ai/agentic-ai/protocols/a2a/test data/2026AnthemgHIPSBC.pdf")
    def answer_query(self, query: str) -> str:
        response = litellm.completion(
            model="groq/openai/gpt-oss-120b",
            reasoning_effort= "low",
            max_tokens= 1000,
            messages = [
                {"role": "system",
                "content": f"""
                You are an expert insurance agent designed to assist with health insurance policy coverage queries. 
                Use only the provided documents to answer questions about insurance policies. If the information is not available in the documents, respond with 'I don't know"
                do not explain too state the facts based on the provided documents.
                """},
                {
                    "role": "user",
                    "content": [
                        {"type": "text",
                         "text": query
                         },
                         {
                            "type": "text",
                            "text": self.file_content_text,
                         },


                    ],
                },

                ],
        )
        return response.choices[0].message.content.replace("$", r"\$")