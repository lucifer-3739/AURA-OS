from agent.security import PermissionManager, RiskLevel, PermissionStatus

def test_permission_risk_levels():
    pm = PermissionManager(mode="interactive")
    
    # SAFE & MODERATE auto-approved
    assert pm.evaluate(RiskLevel.SAFE) == PermissionStatus.AUTO_APPROVED
    assert pm.evaluate(RiskLevel.MODERATE) == PermissionStatus.AUTO_APPROVED

    # DANGEROUS & CRITICAL require approval
    assert pm.evaluate(RiskLevel.DANGEROUS) == PermissionStatus.PENDING
    assert pm.evaluate(RiskLevel.CRITICAL) == PermissionStatus.PENDING

    # With user approval
    assert pm.evaluate(RiskLevel.DANGEROUS, user_confirmed=True) == PermissionStatus.USER_APPROVED
    assert pm.evaluate(RiskLevel.DANGEROUS, user_confirmed=False) == PermissionStatus.USER_REJECTED
