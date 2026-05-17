# Characterization Tests (Reference)

Approval / golden-master testing for **legacy code without coverage**. Based on Michael Feathers, *Working Effectively with Legacy Code* (2004), and Llewellyn Falco's approval-testing tradition (approvaltests.com).

## When to Apply

Run a coverage scan on the target files **before** any refactor. If line coverage on the touched files is **<80%**, write characterization tests as a **separate, prior phase** — do NOT mix them into the refactor commit.

Without characterization, "tests still pass" is meaningless: you might be preserving behavior that wasn't tested, or breaking behavior that was never asserted. Characterization tests turn the current behavior into the spec.

## Core Idea

> Capture current behavior as a test **without judging whether it's correct**, then refactor knowing any behavior change shows up as a failing test.

The test is a witness, not a judge. You're not asking "is this right?" — you're asking "what does it do today?" and freezing that answer.

## Workflow

1. **Identify the seam.** A seam is a place where behavior can be intercepted without changing the code under test (Feathers). Common seams: function boundary, class constructor, network/IO boundary, observable property.
2. **Write a test** that calls the function with realistic inputs. Use real production data when possible — anonymized fixtures, recorded request/response pairs, sample files from production.
3. **Run the test** and let it fail. The failure shows the **actual** output of today's code.
4. **Copy actual output as expected output** — the "approval." The captured output is now the gold-standard reference.
5. **Re-run the test** — it passes.
6. **Refactor.** Any behavior change during the refactor produces a diff against the approval and fails the test.
7. **Review approval diffs deliberately.** When the test fails after a refactor, the diff between actual and approved is the whole signal — eyeball it before re-approving.

## Tooling

| Tool | Language | Notes |
|---|---|---|
| ApprovalTests | .NET, Java, Python, JS, C++, Ruby | Original approval-testing library family (approvaltests.com) |
| pytest-approvaltests | Python | pytest-native integration |
| Jest snapshots | JS / TS | Same idea, framework-integrated; `toMatchSnapshot()` |
| Vitest snapshots | JS / TS | Drop-in for Jest snapshots |
| insta | Rust | Inline + file snapshots |
| Cupaloy / goldie | Go | Golden-file helpers |
| Diff-on-stdout golden files | any | Language-agnostic: dump output to a file, `diff` against committed expected output |

**Default rule:** prefer a framework-integrated snapshot tool (Jest, Vitest, pytest-approvaltests, insta). Fall back to plain golden files when the output isn't easily serialized or you need cross-language tests.

## Patterns from *Working Effectively with Legacy Code*

### Sensing Variable Extraction
Capture intermediate state to test, then remove the sensing once the test pins behavior down.
```python
# Before refactor — function only returns a side effect
def process(order):
    apply_discount(order)
    record_audit(order)

# Add a sensing variable for the test
def process(order):
    discounted = apply_discount(order)
    audit_id = record_audit(order)
    return {"discounted": discounted, "audit_id": audit_id}  # sensing
```
Once the characterization test asserts on the sensing dict, you can refactor `apply_discount` and `record_audit` freely. After the refactor settles, restore the original return type.

### Subclass and Override
Split the concrete class so a test subclass can override the awkward parts (network call, clock, random) **without changing production behavior**.
```python
class PaymentCalculator:
    def now(self):  # seam
        return datetime.utcnow()
    def compute(self, order):
        return order.total * self.rate(self.now())

class FrozenClockPaymentCalculator(PaymentCalculator):
    def now(self):
        return datetime(2026, 1, 1)
```

### Wrap Method
Preserve the existing call site while adding a hook for tests.
```python
def charge(order):  # public — unchanged signature
    _charge_impl(order, clock=datetime.utcnow)

def _charge_impl(order, clock):  # testable — clock is injectable
    ...
```

## Mutation Testing as a Quality Probe

A characterization test **passes** doesn't prove it's sensitive enough. Run mutation testing after writing the suite:

| Tool | Language |
|---|---|
| `mutmut` | Python |
| `pitest` | Java / Kotlin |
| `stryker` | JS / TS |
| `cargo-mutants` | Rust |
| `mull` | C / C++ |

Mutation testing perturbs the code (flips operators, removes statements) and checks whether your tests catch it. **If mutation score is low (<70%), characterization isn't sensitive enough — add more inputs or coarser assertions before refactoring.**

## Concrete Example — `PaymentCalculator.compute()`

Legacy code with no tests. We want to refactor it. First, characterize.

```python
# tests/test_payment_calculator_characterization.py
import json
from pathlib import Path
import pytest
from legacy.payment import PaymentCalculator

FIXTURES = Path(__file__).parent / "fixtures" / "orders"

@pytest.mark.parametrize("fixture", sorted(FIXTURES.glob("*.json")))
def test_compute_matches_approved_output(fixture, snapshot):
    order = json.loads(fixture.read_text())
    calc = PaymentCalculator(rate_table=load_rate_table())
    result = calc.compute(order)
    snapshot.assert_match(json.dumps(result, indent=2, sort_keys=True), fixture.stem + ".approved.json")
```

Or with ApprovalTests:

```python
from approvaltests import verify

def test_compute_for_sample_order():
    order = json.loads(FIXTURES.joinpath("order_typical.json").read_text())
    calc = PaymentCalculator(rate_table=load_rate_table())
    verify(json.dumps(calc.compute(order), indent=2, sort_keys=True))
```

Run once, inspect the `*.received.txt`, copy to `*.approved.txt`, commit. Now `compute()` is pinned. Refactor freely; any behavior drift produces a diff.

After the suite is green, run `mutmut run --paths-to-mutate legacy/payment.py`. If the score is below 70%, the characterization is too coarse — add fixtures covering edge cases (negative totals, zero quantity, missing fields) before touching the refactor itself.

## Output Artifact

When `/refactor` triggers a characterization phase, the developer writes:
- Tests under `tests/characterization/<module>/`.
- A short note in `<repo>/.ai-skills-memory/refactor/<run-id>/CHARACTERIZATION.md` listing files covered, fixture sources, and the mutation score baseline. The team-lead reads this before approving the refactor plan.
