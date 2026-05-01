# Code Sample — Tangled interdependencies

```python
# Compute something
def compute(d, m, x):
    try:
        r = d['val'] * m if d else x
    except:
        r = x
    return r

# Process a batch
def process_batch(items, config, state):
    out = []
    for i, item in enumerate(items):
        try:
            v = item.get('value')
            if v is None:
                v = config.get('default', 0)
            
            # Mutate state
            state['count'] = state.get('count', 0) + 1
            state['last_value'] = v
            
            # Weird coupling: depends on side effects from earlier iterations
            adjusted = v * (state.get('multiplier', 1) if state['count'] > 5 else 1)
            
            # Bare except
            try:
                out.append({'result': adjusted, 'count': state['count']})
            except:
                pass  # Silent fail
        except Exception as e:
            # No logging, no re-raise
            pass
    
    return out, state
```

Problems:
- Bare exception handlers (catches all errors, including KeyboardInterrupt)
- No logging or error visibility
- Mutation of shared state (tightly couples iterations)
- Side effects make testing hard
- No type hints or docstrings
- Silent failures mask bugs
