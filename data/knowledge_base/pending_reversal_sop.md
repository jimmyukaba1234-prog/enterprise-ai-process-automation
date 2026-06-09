# Pending Reversal Standard Operating Procedure (SOP)

## Purpose

This document defines the process for handling customer inquiries relating to pending reversals following failed transactions, unsuccessful card payments, ATM dispense errors, and other debit-related incidents.

The objective is to provide customers with accurate status updates while ensuring timely escalation when reversal timelines are exceeded.

---

## Definition

A pending reversal occurs when:

- Customer was debited.
- Original transaction did not complete successfully.
- Funds have not yet been returned.
- Reversal process is still ongoing.

---

## Common Customer Complaints

Customers may report:

- "My money has not been reversed."
- "I was debited but did not receive value."
- "The reversal is taking too long."
- "My funds are still pending."

---

## Required Verification

Before investigating:

1. Verify customer identity.
2. Verify account ownership.
3. Confirm transaction ownership.

---

## Investigation Process

### Step 1

Retrieve transaction information.

API:

- get_transaction_details()

Retrieve:

- Transaction reference
- Amount
- Date
- Transaction type
- Current transaction status

---

### Step 2

Check reversal status.

API:

- check_reversal_status()

Possible statuses:

- COMPLETED
- PENDING
- FAILED
- NOT_FOUND

---

## Status Handling

### COMPLETED

Inform customer:

> The reversal has been successfully processed and the funds have been returned to your account.

Provide reversal date and time if available.

---

### PENDING

Inform customer:

> The reversal request is currently being processed. Some reversals may take additional time depending on the transaction channel and participating institutions.

Provide estimated timeline.

---

### FAILED

Create investigation ticket.

Escalate immediately.

---

### NOT_FOUND

Create dispute case.

Escalate to Finance Operations.

---

## Reversal Timelines

Typical reversal timelines:

| Channel | Expected Timeline |
|----------|-------------------|
| Internal Transfer | Up to 24 Hours |
| Interbank Transfer | Up to 48 Hours |
| ATM Dispense Error | 3–5 Business Days |
| POS Transaction | 3–7 Business Days |
| Card Transaction | 7–14 Business Days |

---

## Escalation Conditions

Escalate when:

- Reversal exceeds SLA
- Reversal status unavailable
- Reversal fails
- Customer disputes information
- Multiple complaints exist

Department:

Finance Operations

---

## Allowed Actions

The AI agent may:

- Check reversal status
- Inform customer of timeline
- Create dispute ticket
- Escalate case

The AI agent may NOT:

- Force reversal processing
- Credit customer account manually
- Alter transaction records

---

## Customer Communication Example

> Your reversal request is currently under processing. Based on the transaction type, reversals may take up to the applicable timeline before completion. We will escalate the case if the expected timeline is exceeded.

---

## AI Agent Instruction Summary

1. Verify customer.
2. Retrieve transaction.
3. Check reversal status.
4. Compare against SLA.
5. Inform customer.
6. Escalate when necessary.
7. Log all actions.