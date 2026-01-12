class ScoringService:
    @staticmethod
    def determine_priority(score: float) -> str:
        """Determines lead priority based on prediction score."""
        if score > 0.3:
            return "High"
        elif score > 0.1:
            return "Medium"
        else:
            return "Low"

    @staticmethod
    def evaluate_accuracy(priority: str, actual_converted: bool) -> str:
        """Evaluates prediction accuracy against actual outcome."""
        if priority == "High" and actual_converted:
            return "correct"
        elif priority == "Low" and not actual_converted:
            return "correct"
        elif priority == "High" and not actual_converted:
            return "false_positive"
        elif priority == "Low" and actual_converted:
            return "missed"
        else:
            return "medium"
