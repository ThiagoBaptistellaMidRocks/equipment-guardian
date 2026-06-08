from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score


class EvaluationService:
    def evaluate(self, y_true, y_prob, threshold: float = 0.5) -> dict[str, float]:
        y_pred = [1 if value >= threshold else 0 for value in y_prob]
        metrics = {
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "precision": float(precision_score(y_true, y_pred, zero_division=0)),
            "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        }

        try:
            metrics["roc_auc"] = float(roc_auc_score(y_true, y_prob))
        except ValueError:
            metrics["roc_auc"] = 0.0

        return metrics
