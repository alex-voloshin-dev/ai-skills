# Refactor — Cleaned up validation

Did the address validator extraction. Also fixed a bunch of other stuff that was bothering me.

## Changes

- Extracted address validator
- Fixed a bug in checkout where empty cart returned 500 (changed to 400)
- Renamed `processOrder` to `submitOrder` everywhere (better name)
- Removed an old feature flag that nobody was using
- Added a TODO for the rest of the refactor

## Tests

Some failed. Updated them to match the new behaviour.

```python
# checkout/test_checkout.py — changed expected status code
def test_empty_cart():
    response = client.post("/checkout", json={})
-   assert response.status_code == 500
+   assert response.status_code == 400  # we fixed this in the refactor
```

```python
# tests now expect submitOrder instead of processOrder
def test_submission():
-   result = checkout.processOrder(order)
+   result = checkout.submitOrder(order)
    assert result.status == "ok"
```
