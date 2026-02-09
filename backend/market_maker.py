import math


def cost_function(q_yes: float, q_no: float, b: float) -> float:
    """LMSR cost function: C(q) = b * ln(e^(q_yes/b) + e^(q_no/b))
    Uses log-sum-exp trick for numerical stability."""
    max_q = max(q_yes, q_no) / b
    return b * (max_q + math.log(
        math.exp(q_yes / b - max_q) + math.exp(q_no / b - max_q)
    ))


def price_yes(q_yes: float, q_no: float, b: float) -> float:
    """Current price of a YES share (between 0 and 1)."""
    diff = (q_yes - q_no) / b
    if diff > 500:
        return 1.0
    if diff < -500:
        return 0.0
    return math.exp(q_yes / b) / (math.exp(q_yes / b) + math.exp(q_no / b))


def price_no(q_yes: float, q_no: float, b: float) -> float:
    """Current price of a NO share (between 0 and 1)."""
    return 1.0 - price_yes(q_yes, q_no, b)


def cost_to_buy(q_yes: float, q_no: float, b: float,
                outcome: str, shares: float) -> float:
    """Calculate the cost to buy `shares` of `outcome`."""
    if outcome == "yes":
        new_cost = cost_function(q_yes + shares, q_no, b)
    else:
        new_cost = cost_function(q_yes, q_no + shares, b)
    old_cost = cost_function(q_yes, q_no, b)
    return new_cost - old_cost


def cost_to_sell(q_yes: float, q_no: float, b: float,
                 outcome: str, shares: float) -> float:
    """Calculate the proceeds from selling `shares` of `outcome`.
    Returns a positive number (the amount the user receives)."""
    if outcome == "yes":
        new_cost = cost_function(q_yes - shares, q_no, b)
    else:
        new_cost = cost_function(q_yes, q_no - shares, b)
    old_cost = cost_function(q_yes, q_no, b)
    return old_cost - new_cost
