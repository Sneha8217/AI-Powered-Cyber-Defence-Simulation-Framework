import io
import base64
import matplotlib.pyplot as plt
import numpy as np

def generate_waterfall_base64(explanation_dict: dict, title="Explanation Attribution Details") -> str:
    """
    Renders a horizontal bar chart of feature contributions and returns a Base64 string.
    """
    # Extract keys and values
    features = list(explanation_dict.keys())
    scores = list(explanation_dict.values())
    
    # Sort by absolute score value
    indices = np.argsort(np.abs(scores))
    features = [features[i] for i in indices]
    scores = [scores[i] for i in indices]

    # Plotting
    fig, ax = plt.subplots(figsize=(6, 4))
    colors = ["#e74c3c" if s > 0 else "#2ecc71" for s in scores] # red for malicious, green for benign
    
    bars = ax.barh(features, scores, color=colors, edgecolor="black", height=0.6)
    ax.axvline(x=0, color="black", linewidth=1.0, linestyle="--")
    
    # Text labels
    for bar in bars:
        width = bar.get_width()
        label_x = width + (0.01 if width >= 0 else -0.05)
        ax.text(
            label_x,
            bar.get_y() + bar.get_height() / 2,
            f"{width:+.3f}",
            va="center",
            ha="left" if width >= 0 else "right",
            fontsize=8,
            fontweight="bold"
        )
        
    ax.set_title(title, fontsize=10, fontweight="bold")
    ax.set_xlabel("Contribution score (Red increases threat | Green decreases threat)", fontsize=8)
    plt.tight_layout()
    
    # Convert plot to Base64
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    
    img_b64 = base64.b64encode(buf.read()).decode("utf-8")
    return img_b64

if __name__ == "__main__":
    dummy_scores = {
        "src_ip_reputation": 0.42,
        "dst_port_risk": -0.15,
        "alert_freq_1h": 0.58,
        "asset_criticality": 0.12,
        "protocol_anomaly": 0.35,
        "geo_mismatch": -0.22
    }
    b64 = generate_waterfall_base64(dummy_scores)
    print(f"Generated Base64 String (length={len(b64)}): {b64[:100]}...")
