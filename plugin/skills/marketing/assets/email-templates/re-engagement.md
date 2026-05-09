# Re-engagement / Win-back Email Template

Send to subscribers who have not opened or clicked in 60-90 days. Goal is binary: re-engage them, or let them go cleanly. A clean unsubscribe is better than a dead address dragging your sender reputation down.

## Subject line (3 variants)

1. **Direct**: `Should we keep sending?`
2. **Honest**: `It has been a while`
3. **Specific**: `Last email from us unless you click below`

Avoid manipulative subjects (`Your account will be deleted`) — they trigger spam filters and burn trust.

## Preview text

80-110 characters. Reinforce the choice, not the loss.

> A quick check-in. Two seconds, one click — keep getting our updates or step off the list.

## Acknowledgment

Two or three sentences. Honest, not sycophantic. Skip phrases like `we miss you so much` or `you are special to us`.

> Looking at our records, you have not opened anything from us since February. That is fine — inboxes get crowded and priorities shift.

## Reminder of value

What did they originally sign up for, and is that promise still being delivered? One short paragraph.

> When you joined the {company} list, we promised one email every two weeks with hands-on engineering write-ups and zero recruitment spam. We have kept to that. The full archive lives at {url} if you want to skim recent issues before deciding.

## What has changed since last visit

3-5 bullets. Focus on improvements that respond to common complaints (cadence, content quality, new formats).

- Cut send frequency from weekly to bi-weekly
- Added a `read time` indicator at the top of every issue
- Shipped a {key product feature} you may have been waiting for
- Removed the digest format readers said felt cluttered
- Started a podcast version for commute listeners

## Single low-friction CTA

One click. No form, no logged-in confirmation flow.

> [Yes, keep me on the list →]

Place the explicit unsubscribe link directly under the CTA — same visual weight, not buried in the footer.

> Or: [unsubscribe with one click]

This pairing satisfies GDPR Article 7(3) (withdrawal of consent must be as easy as giving it) and CAN-SPAM one-click requirements.

## Polite goodbye option

Below the CTAs, one short paragraph for readers who choose to leave.

> If this is not a fit anymore, no hard feelings. Unsubscribing helps us send to people who actually want to hear from us. Thanks for the time you gave us.

## Sign-off

```
— {first_name}
{role}, {company}
```

## GDPR-compliant unsubscribe handling

- Process the unsubscribe within 10 business days (GDPR / CAN-SPAM)
- Do not require a login or password to unsubscribe
- Do not ask for a reason — that is a separate optional survey
- Honor the unsubscribe across all marketing lists, not just this campaign
- Keep a suppression record (hashed email + timestamp) so the address is not re-imported later
- For EU subscribers, run a sunset policy: 90 days no engagement → re-engagement → 30 days no response → auto-suppress

## Followup logic

If no click within 14 days, send one final `last call` email, then auto-suppress. Do not chain four or five win-back emails — it damages deliverability for the rest of the list.
