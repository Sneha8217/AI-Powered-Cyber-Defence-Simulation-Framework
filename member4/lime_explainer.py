import numpy as np
from sklearn.linear_model import Ridge

class AlertLimeExplainer:
    """
    Fits local linear surrogate models around target instance to explain decisions (LIME).
    """
    def __init__(self, num_features=8):
        self.num_features = num_features
        self.feature_names = [
            "src_ip_reputation", "dst_port_risk", "alert_freq_1h", "asset_criticality",
            "time_of_day", "protocol_anomaly", "geo_mismatch", "connection_duration"
        ]

    def explain_instance(self, instance: list, predict_fn) -> dict:
        """
        Creates perturbations, queries target model's predictions, and fits local Ridge regression.
        """
        x_target = np.array(instance)
        num_perturbations = 100
        
        # 1. Generate perturbations around the target instance
        perturbations = x_target + np.random.normal(0, 0.1, size=(num_perturbations, self.num_features))
        perturbations = np.clip(perturbations, 0.0, 100.0) # bound check
        
        # 2. Get predictions from target model
        y_perturbed = []
        for p in perturbations:
            y_perturbed.append(predict_fn(p.tolist()))
        y_perturbed = np.array(y_perturbed)

        # 3. Calculate distance weights
        distances = np.linalg.norm(perturbations - x_target, axis=1)
        # kernel width
        kernel_width = 0.75
        weights = np.exp(- (distances ** 2) / (kernel_width ** 2))

        # 4. Fit local Ridge regressor
        local_model = Ridge(alpha=1.0)
        local_model.fit(perturbations, y_perturbed, sample_weight=weights)
        
        # Extract weights
        weights_dict = {}
        for name, coef in zip(self.feature_names, local_model.coef_):
            weights_dict[name] = float(coef)

        return {
            "intercept": float(local_model.intercept_),
            "local_weights": weights_dict
        }

if __name__ == "__main__":
    explainer = AlertLimeExplainer()
    # Dummy prediction function: returns threat score based on reputation and port risk
    def dummy_predict(feats):
        return feats[0] * 0.7 + feats[2] * 0.05
        
    res = explainer.explain_instance([0.9, 0.2, 12.0, 8.0, 0.1, 0.8, 1.0, 0.05], dummy_predict)
    print("LIME Local Weights:")
    import json
    print(json.dumps(res, indent=2))
