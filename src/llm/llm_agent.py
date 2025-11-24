import os
import openai

class LLMAgent:
    """Generates natural-language explanations using ASI Cloud LLM."""

    def __init__(self, api_key=None, model="openai/gpt-oss-20b"):
        self.api_key = api_key or os.environ.get("ASI_API_KEY")
        if not self.api_key:
            raise ValueError("ASI_API_KEY not provided!")

        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url="https://inference.asicloud.cudos.org/v1"
        )
        self.model = model

    def ask(self, prompt, temperature=0.4, max_tokens=300):
        """Send prompt to ASI LLM (OpenAI chat-completion format)."""

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                temperature=temperature,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )

            return resp.choices[0].message.content

        except Exception as e:
            return f"[LLMAgent ERROR] {str(e)}"
