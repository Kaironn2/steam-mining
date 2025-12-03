from typing import Optional

class TextUtils:
    @staticmethod
    def normalize(text: Optional[str]) -> Optional[str]:
        """
        Replaces specific Unicode characters in the input text with their ASCII equivalents.
        - Replaces Unicode right single quotation mark (’ - \u2019) with ASCII apostrophe (').
        - Replaces non-breaking space characters (\u00a0) with a regular space (' ').

        The input may be None, in which case the function returns None.
        """
        if not text:
            return None

        text = text.replace('\u2019', "'")
        text = text.replace('\u00a0', ' ')
        return text.strip()
