from typing import Tuple

def evaluate_operational_priority(
    risk_index: float,
    abnormality: str,
    source_hypothesis: str,
    verification_status: str,
    confidence: float
) -> Tuple[str, str]:
    """
    Evaluates Operational Investigation Priority:
    Answers: 'Which event should an analyst investigate first?'
    Returns (priority_level, justification).
    """
    if risk_index >= 75.0 or (abnormality == "Highly Abnormal" and source_hypothesis == "Industrial Fire"):
        priority = "Critical"
        justification = "Immediate analyst attention required: high risk score combined with abnormal industrial thermal signature."
    elif risk_index >= 55.0 or abnormality in ["Unusual", "Highly Abnormal"]:
        priority = "High"
        justification = "Elevated investigation priority: significant deviation from historical baseline or sensitive asset proximity."
    elif risk_index >= 30.0 or source_hypothesis == "Wildfire":
        priority = "Medium"
        justification = "Moderate priority: active thermal event being tracked; no immediate industrial infrastructure breach."
    elif source_hypothesis == "Routine Flare" and abnormality == "Normal":
        priority = "Low"
        justification = "Routine operational monitoring: signature conforms to registered facility flare baseline."
    else:
        priority = "Monitor"
        justification = "Ongoing sensor tracking; low risk and stable spatial footprint."

    return priority, justification
