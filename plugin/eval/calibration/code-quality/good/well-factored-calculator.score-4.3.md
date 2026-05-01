# Code Sample — Calculator with clear factoring

```python
"""Financial calculator for interest and penalties."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass
class LoanPayment:
    principal: Decimal
    annual_rate: Decimal
    months: int
    
    def monthly_rate(self) -> Decimal:
        """Convert annual percentage rate to monthly decimal."""
        return self.annual_rate / 100 / 12
    
    def monthly_payment(self) -> Decimal:
        """Calculate fixed monthly payment using standard amortization formula.
        
        Assumes monthly compounding over the loan term.
        Returns amount in dollars (rounded to nearest cent).
        """
        r = self.monthly_rate()
        if r == 0:
            return (self.principal / self.months).quantize(Decimal('0.01'))
        
        numerator = r * (1 + r) ** self.months
        denominator = (1 + r) ** self.months - 1
        return (self.principal * numerator / denominator).quantize(Decimal('0.01'))
    
    def total_interest(self) -> Decimal:
        """Total interest paid over loan lifetime."""
        return (self.monthly_payment() * self.months) - self.principal


# Tests
def test_monthly_payment_no_interest():
    loan = LoanPayment(principal=Decimal('1000'), annual_rate=Decimal('0'), months=12)
    assert loan.monthly_payment() == Decimal('83.33')

def test_monthly_payment_with_interest():
    loan = LoanPayment(principal=Decimal('200000'), annual_rate=Decimal('4.5'), months=360)
    # Expected: approximately $1013.37/month for 30-year mortgage
    assert Decimal('1000') < loan.monthly_payment() < Decimal('1100')

def test_total_interest_calculation():
    loan = LoanPayment(principal=Decimal('100000'), annual_rate=Decimal('5'), months=60)
    total = loan.total_interest()
    assert Decimal('12000') < total < Decimal('14000')  # 5-year term
```
