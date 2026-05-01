# Code Sample — Magic numbers and copy-paste

```javascript
function calculatePrice(qty, tax_rate) {
    // Hardcoded multipliers (what do these mean?)
    if (qty > 100) {
        return qty * 9.95 * (1 + 0.08);  // 8% tax hardcoded
    } else if (qty > 50) {
        return qty * 10.50 * (1 + 0.08);
    } else {
        return qty * 12.99 * (1 + 0.08);
    }
}

// Copy-pasted logic in another function
function calculateDiscount(qty, tax_rate) {
    if (qty > 100) {
        return qty * 9.95 * (1 + 0.08) * 0.85;  // 15% discount, hardcoded
    } else if (qty > 50) {
        return qty * 10.50 * (1 + 0.08) * 0.85;
    } else {
        return qty * 12.99 * (1 + 0.08) * 0.85;
    }
}

// Tax param passed but ignored
function submitOrder(items, shipping_cost, tax_rate) {
    let total = 0;
    for (let item of items) {
        total += item.qty * item.price;
    }
    total = total * 1.08;  // 8% tax hardcoded again
    total += shipping_cost;
    return total;
}
```

Problems:
- Magic numbers (9.95, 10.50, 12.99, 0.08, 0.85) with no explanation
- Same logic repeated 3 places (maintenance nightmare)
- Function parameters (tax_rate) ignored; values hardcoded
- No DRY principle; copy-paste increases bug surface
