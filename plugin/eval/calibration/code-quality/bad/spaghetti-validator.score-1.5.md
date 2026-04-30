# Code Sample — Email validator

```python
import re

def v(e):
    # validate
    if e == None or e == "":
        return False
    try:
        if len(e) > 500:
            return False
        # check format
        x = re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", e)
        if x:
            return True
        else:
            return False
    except:
        # something went wrong
        pass

# TODO: add tests later
# TODO: handle internationalized domains
# TODO: add MX check
# old version below in case we need it:
# def validate_email(email):
#     return "@" in email
```
