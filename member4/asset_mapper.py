import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] (AssetMapper) %(message)s")
logger = logging.getLogger("ACDSF-AssetMapper")

class AssetMapper:
    """
    Asset Inventory and Criticality Mapping.
    Profiles asset vulnerabilities and maps host IPs to enterprise CNI sectors.
    """
    def __init__(self):
        # Sample CNI network subnets
        self.sector_subnets = {
            "Government": "10.1.0.0/16",
            "Energy": "10.2.0.0/16",
            "Finance": "10.3.0.0/16",
            "Telecom": "10.4.0.0/16",
            "Water": "10.5.0.0/16",
            "Transport": "10.6.0.0/16"
        }

        # Hardcoded inventory map (IP: {name, criticality, cves})
        self.asset_registry = {
            "10.1.0.10": {"name": "GOVT-SRV1", "criticality": 9, "cves": 2},
            "10.2.0.20": {"name": "ENERGY-PLC-01", "criticality": 10, "cves": 4},
            "10.3.0.15": {"name": "FINANCE-DB-01", "criticality": 10, "cves": 1},
            "10.4.0.50": {"name": "TELECOM-SWITCH-01", "criticality": 7, "cves": 0},
            "10.5.0.30": {"name": "WATER-PUMP-PLC", "criticality": 8, "cves": 3},
            "10.6.0.25": {"name": "TRANSPORT-HMI", "criticality": 8, "cves": 2}
        }

    def resolve_sector(self, ip: str) -> str:
        """Determines sector from IP octets."""
        if ip.startswith("10.1."):
            return "Government"
        elif ip.startswith("10.2."):
            return "Energy"
        elif ip.startswith("10.3."):
            return "Finance"
        elif ip.startswith("10.4."):
            return "Telecom"
        elif ip.startswith("10.5."):
            return "Water"
        elif ip.startswith("10.6."):
            return "Transport"
        return "External"

    def get_asset_info(self, ip: str) -> dict:
        """Retrieves profile info, returns defaults if not found in registry."""
        sector = self.resolve_sector(ip)
        if ip in self.asset_registry:
            info = self.asset_registry[ip].copy()
            info["sector"] = sector
            return info
        else:
            # Default fallback for new discovered hosts
            return {
                "name": f"Discovered-Host-{ip.replace('.', '-')}",
                "criticality": 5,
                "cves": 1,
                "sector": sector
            }
            
if __name__ == "__main__":
    mapper = AssetMapper()
    print("Resolved profile for 10.2.0.20:", mapper.get_asset_info("10.2.0.20"))
