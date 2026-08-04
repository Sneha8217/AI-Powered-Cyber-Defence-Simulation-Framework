import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_curve, auc

def calculate_evaluation_metrics(y_true, y_pred, y_prob, save_plot_path="logs/roc_curve.png"):
    """
    Computes cyber classification metrics and saves a ROC curve chart.
    """
    # Create logs directory
    os.makedirs(os.path.dirname(save_plot_path), exist_ok=True)
    
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    
    # ROC Curve calculation
    fpr, tpr, thresholds = roc_curve(y_true, y_prob)
    roc_auc = auc(fpr, tpr)
    
    print("\n--- Model Evaluation Summary ---")
    print(f"Accuracy         : {accuracy:.4f}")
    print(f"Precision        : {precision:.4f}")
    print(f"Recall (DR)      : {recall:.4f}")
    print(f"F1 Score         : {f1:.4f}")
    print(f"ROC AUC          : {roc_auc:.4f}")
    
    # Plotting
    plt.figure(figsize=(6, 5))
    plt.plot(fpr, tpr, color="darkorange", lw=2, label=f"ROC Curve (AUC = {roc_auc:.2f})")
    plt.plot([0, 1], [0, 1], color="navy", lw=2, linestyle="--")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("False Positive Rate (FPR)")
    plt.ylabel("True Positive Rate (TPR)")
    plt.title("Intrusion Detection Receiver Operating Characteristic (ROC)")
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(save_plot_path, dpi=100)
    plt.close()
    print(f"ROC chart saved successfully to {save_plot_path}")
    
    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "auc": roc_auc
    }

if __name__ == "__main__":
    # Generate mock validation data
    np.random.seed(42)
    y_true_mock = np.random.randint(0, 2, size=200)
    y_prob_mock = np.random.rand(200)
    # Add dependency to ground truth for realistic correlation
    y_prob_mock = np.clip(y_prob_mock * 0.5 + y_true_mock * 0.5, 0.0, 1.0)
    y_pred_mock = (y_prob_mock > 0.5).astype(int)
    
    calculate_evaluation_metrics(y_true_mock, y_pred_mock, y_prob_mock)
