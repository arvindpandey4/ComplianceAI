import tiktoken
from typing import List
from loguru import logger

class TokenManager:
    def __init__(self, model_name: str = "cl100k_base", max_input_tokens: int = 6000):
        try:
            self.encoder = tiktoken.get_encoding(model_name)
        except:
            self.encoder = tiktoken.get_encoding("cl100k_base")
        
        self.max_input_tokens = max_input_tokens

    def count_tokens(self, text: str) -> int:
        if not text:
            return 0
        return len(self.encoder.encode(text))

    def validate_and_truncate(self, history: str, regulatory_context: str, query: str) -> str:
        query_tokens = self.count_tokens(query)
        history_tokens = self.count_tokens(history)
        
        available_info_tokens = self.max_input_tokens - query_tokens - 500
        
        if available_info_tokens < 0:
            logger.warning("Query is too large! Truncating inputs heavily.")
            return ""

        current_context_tokens = self.count_tokens(regulatory_context)
        
        if history_tokens + current_context_tokens <= available_info_tokens:
            return f"{history}\n\nRegulatory Documents:\n{regulatory_context}" if history else regulatory_context

        logger.info(f"Token Limit Exceeded: {history_tokens + current_context_tokens} > {available_info_tokens}. Truncating...")

        remaining_for_context = available_info_tokens - history_tokens
        
        if remaining_for_context < 1000:
            history = history[-2000:]
            history_tokens = self.count_tokens(history)
            remaining_for_context = available_info_tokens - history_tokens

        encoded_context = self.encoder.encode(regulatory_context)
        safe_context_tokens = encoded_context[:remaining_for_context]
        safe_context = self.encoder.decode(safe_context_tokens)
        
        return f"{history}\n\nRegulatory Documents:\n{safe_context} ...[TRUNCATED]" if history else safe_context

token_manager = TokenManager()
