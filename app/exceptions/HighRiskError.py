class HighRiskError(Exception):
    """Exception raised for high risk individual."""
    def __init__(self, risk, message="Individual is high risk"):
        self.risk = risk
        self.message = message
        super().__init__(self.message) # Call the base class constructor
    
    def __str__(self):
        return f'{self.risk} -> {self.message}'