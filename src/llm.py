import os
from google import genai
from google.genai import types

# Ensure this class name matches your pipeline's import exactly
class GeminiAnswerer:
    def __init__(self):
        # The new SDK automatically picks up GEMINI_API_KEY from your .env file
        self.client = genai.Client()
        # Target the recommended model
        self.model_name = "gemini-3.6-flash" 

    def answer(self, question: str, passages: list) -> str:
        # Build your RAG context context
        context = "\n\n".join([f"Source:\n{p}" for p in passages])
        
        user_prompt = f"""You are a helpful research assistant. Answer the question based strictly on the provided context. If the answer cannot be found, say so.

Context:
{context}

Question: {question}
Answer:"""

        # Call the new Google Gen AI SDK
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=user_prompt,
        )
        
        return response.text
