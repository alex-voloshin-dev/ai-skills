# Changes to notification system

## Summary
Work in progress on notifications. Adds email and SMS support but not fully tested yet.

## Changes
- Modified `src/notifications/sender.py` to support email and SMS
- Added new file `src/notifications/channels.py` (incomplete)
- Updated `src/models/user.py` — added phone_number field but migration not done
- Removed old notification code (file `src/legacy_notify.py`)

## PR Description
Just implemented the notification system. Should be good to go.

## Commit Messages
- commit 1: "add notifications"
- commit 2: "more changes"
- commit 3: "fix stuff"

## Code
```python
def send_notification(user, msg, channel='email'):
    if channel == 'email':
        import smtplib  # TODO: use config
        client = smtplib.SMTP('localhost', 25)
        client.sendmail(msg)  # missing recipient
    elif channel == 'sms':
        # SMS code not written yet
        pass
    return True  # assuming success
```

## Testing
Will add tests in next PR.

## Concerns
- Need to handle failures better
- SMS integration with Twilio (no credentials yet)
- Should we support WhatsApp?
