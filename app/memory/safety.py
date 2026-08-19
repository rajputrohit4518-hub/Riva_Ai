from app.memory.policy import MemoryAction, MemoryCategory, MemoryDecision


class MemorySafetyPolicy:
    BLOCKED_CATEGORIES = {
        "password",
        "secret",
        "credential",
        "api_key",
        "token",
        "financial",
        "medical",
    }

    BLOCKED_KEYWORDS = {
        "password",
        "passwd",
        "api key",
        "secret key",
        "credit card",
        "cvv",
        "otp",
        "token",
    }

    def evaluate(self, key: str, value: str, category: str = "general") -> MemoryDecision:
        text = f"{key} {value} {category}".lower()

        if category.lower() in self.BLOCKED_CATEGORIES:
            return MemoryDecision(
                action=MemoryAction.IGNORE,
                category=MemoryCategory.GENERAL,
                reason="Sensitive memory category is not allowed.",
            )

        if any(keyword in text for keyword in self.BLOCKED_KEYWORDS):
            return MemoryDecision(
                action=MemoryAction.IGNORE,
                category=MemoryCategory.GENERAL,
                reason="Potentially sensitive memory data is not allowed.",
            )

        try:
            resolved = MemoryCategory(category)
        except ValueError:
            resolved = MemoryCategory.GENERAL

        return MemoryDecision(
            action=MemoryAction.REMEMBER,
            category=resolved,
            reason="Memory passed safety policy.",
        )
