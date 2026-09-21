class TokenBudgetExceededError(Exception):
    """Raised when TokenGuard predicts a request will exceed its cost budget."""

    pass