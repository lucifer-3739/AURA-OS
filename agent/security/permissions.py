from enum import Enum
from typing import Dict, Any, Optional

class RiskLevel(str, Enum):
    SAFE = "SAFE"
    MODERATE = "MODERATE"
    DANGEROUS = "DANGEROUS"
    CRITICAL = "CRITICAL"

class PermissionStatus(str, Enum):
    AUTO_APPROVED = "AUTO_APPROVED"
    USER_APPROVED = "USER_APPROVED"
    USER_REJECTED = "USER_REJECTED"
    PENDING = "PENDING"

class PermissionManager:
    def __init__(self, mode: str = "interactive"):
        self.mode = mode  # "interactive", "strict", "permissive"

    def requires_approval(self, risk_level: RiskLevel) -> bool:
        if self.mode == "permissive":
            return risk_level == RiskLevel.CRITICAL
        elif self.mode == "strict":
            return risk_level in (RiskLevel.MODERATE, RiskLevel.DANGEROUS, RiskLevel.CRITICAL)
        else:  # interactive
            return risk_level in (RiskLevel.DANGEROUS, RiskLevel.CRITICAL)

    def evaluate(self, risk_level: RiskLevel, user_confirmed: Optional[bool] = None) -> PermissionStatus:
        if not self.requires_approval(risk_level):
            return PermissionStatus.AUTO_APPROVED

        if user_confirmed is True:
            return PermissionStatus.USER_APPROVED
        elif user_confirmed is False:
            return PermissionStatus.USER_REJECTED
        else:
            return PermissionStatus.PENDING

permission_manager = PermissionManager()
