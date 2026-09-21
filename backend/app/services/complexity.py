from dataclasses import dataclass

from app.schemas.chat import ChatCompletionRequest


@dataclass
class ComplexityResult:
    level: int
    score: int
    reason: str


class ComplexityClassifier:
    REASONING_KEYWORDS = {
        "analyze",
        "compare",
        "evaluate",
        "reason",
        "trade-off",
        "tradeoff",
        "architecture",
        "design",
        "optimize",
        "debug",
        "algorithm",
        "distributed",
        "scalable",
    }

    CODE_KEYWORDS = {
        "code",
        "python",
        "java",
        "javascript",
        "sql",
        "function",
        "class",
        "api",
        "database",
        "implement",
    }

    def classify(
        self,
        request: ChatCompletionRequest,
    ) -> ComplexityResult:
        text = " ".join(
            message.content
            for message in request.messages
        ).lower()

        word_count = len(text.split())
        score = 0
        reasons = []

        # Prompt length
        if word_count > 300:
            score += 2
            reasons.append("long prompt")
        elif word_count > 100:
            score += 1
            reasons.append("medium-length prompt")

        # Reasoning indicators
        reasoning_matches = sum(
            keyword in text
            for keyword in self.REASONING_KEYWORDS
        )

        if reasoning_matches >= 3:
            score += 2
            reasons.append("multiple reasoning indicators")
        elif reasoning_matches >= 1:
            score += 1
            reasons.append("reasoning indicator")

        # Coding / technical indicators
        code_matches = sum(
            keyword in text
            for keyword in self.CODE_KEYWORDS
        )

        if code_matches >= 3:
            score += 2
            reasons.append("multiple technical indicators")
        elif code_matches >= 1:
            score += 1
            reasons.append("technical indicator")

        # Multi-step instructions
        if (
            "step by step" in text
            or "multiple steps" in text
            or "first" in text and "then" in text
        ):
            score += 1
            reasons.append("multi-step task")

        # Convert score to capability requirement
        if score <= 1:
            level = 1
        elif score <= 3:
            level = 2
        else:
            level = 3

        return ComplexityResult(
            level=level,
            score=score,
            reason=", ".join(reasons) if reasons else "simple request",
        )