import logging
from asset_mapper import AssetMapper
from threat_sync import ThreatIntelligenceSynchronizer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] (SituationalAwareness) %(message)s")
logger = logging.getLogger("ACDSF-SituationalAwareness")

class SituationalAwarenessCenter:
    """
    Enterprise Security Situational Awareness engine.
    Correlates asset profiles, vulnerability states, and active threat indicators.
    """
    def __init__(self):
        self.asset_mapper = AssetMapper()
        self.intel_sync = ThreatIntelligenceSynchronizer()
        
        # Load asset mappings and threat intel indexes
        self.intel_sync.sync_feeds()
        
        self.SECTOR_WEIGHTS = {
            "Energy": 0.25,
            "Finance": 0.20,
            "Government": 0.20,
            "Telecom": 0.15,
            "Water": 0.10,
            "Transport": 0.10
        }

    def evaluate_sector_risk(self, sector: str, active_compromises_count: int) -> float:
        """
        Calculates sector risk index [0-100].
        Calculated as a function of active node compromises, asset criticalities, and weights.
        """
        weight = self.SECTOR_WEIGHTS.get(sector, 0.1)
        base_threat = active_compromises_count * 25.0  # +25 risk points per active compromise
        
        # Bound risk
        risk = min(100.0, base_threat * (1.0 + weight))
        logger.info(f"Sector {sector:11s} evaluated risk score: {risk:5.1f}% | Active Compromises: {active_compromises_count}")
        return risk

    def calculate_enterprise_risk(self, active_compromise_map: dict) -> float:
        """
        Computes weighted global enterprise risk index [0-100].
        """
        global_risk = 0.0
        for sector, weight in self.SECTOR_WEIGHTS.items():
            compromises = active_compromise_map.get(sector, 0)
            sector_risk = self.evaluate_sector_risk(sector, compromises)
            global_risk += sector_risk * weight
            
        logger.info(f"[Enterprise Dashboard] Weighted Global Risk Score: {global_risk:.2f}/100")
        return round(global_risk, 2)

if __name__ == "__main__":
    sac = SituationalAwarenessCenter()
    # Assume 1 active compromise in Energy and 2 in Government
    compromises = {"Energy": 1, "Government": 2}
    sac.calculate_enterprise_risk(compromises)
