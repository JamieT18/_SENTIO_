"""
Automated audit trail for Sentio compliance
"""
class AuditTrail:
    def __init__(self):
        self.trail = []
    def log(self, event):
        self.trail.append(event)
    def get_trail(self):
        return self.trail
