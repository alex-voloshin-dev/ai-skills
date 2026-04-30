# Updates

Bunch of stuff.

## Changes

- fixed login
- refactored db layer
- added new feature for users
- updated dependencies
- removed old code
- TODO: write tests later

## Code

```python
def login(u, p):
    try:
        return User.objects.get(email=u, password=p)
    except:
        return None  # silently fail
```

```python
SECRET_KEY = "abc123-real-key"  # replace before merge
```
