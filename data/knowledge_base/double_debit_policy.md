# Double Debit Resolution Policy

## Purpose

This policy governs how the AI Customer Operations Agent handles reports of duplicate debits and multiple charges for a single transaction.

---

## Definition

A double debit occurs when:

- A customer is charged more than once.
- Multiple debits exist for a single transaction.
- The customer paid once but funds were deducted multiple times.

---

## Customer Symptoms

Customers may report:

- "I was debited twice."
- "Money was deducted two times."
- "I paid once but got charged twice."
- "I received multiple debit alerts."

---

## Required Verification

Before investigating:

1. Verify customer identity.
2. Confirm customer account ownership.
3. Confirm transaction belongs to customer.

---

## Investigation Process

### Step 1: Retrieve Transaction History

Call:

- get_recent_transactions()

Retrieve:

- Transaction references
- Amounts
- Timestamps
- Merchant information

---

### Step 2: Check for Duplicate Transactions

Call:

- check_duplicate_debit()

Compare:

- Amount
- Merchant
- Timestamp
- Transaction reference

---

## Possible Outcomes

### Duplicate Confirmed

If duplicate debit exists:

Determine whether:

- Automatic reversal already occurred.
- Reversal is pending.
- No reversal exists.

---

### Duplicate Not Found

If no duplicate debit exists:

Explain findings.

Offer transaction details.

Create investigation ticket if customer disagrees.

---

## Reversal Handling

Call:

- check_reversal_status()

Possible statuses:

- COMPLETED
- PENDING
- NOT_FOUND

---

### Completed

Inform customer:

> A duplicate debit was identified and has already been reversed.

---

### Pending

Inform customer:

> A duplicate debit was identified and reversal is currently being processed.

Provide expected timeline.

---

### Not Found

Create dispute ticket.

Escalate to Finance Operations.

---

## Escalation Conditions

Escalate when:

- Duplicate debit exists without reversal.
- Reversal exceeds SLA.
- Customer disputes findings.
- API investigation fails.

Escalation Department:

Finance Operations

---

## SLA Guidelines

| Issue | SLA |
|--------|------|
| Duplicate Debit Investigation | 24 Hours |
| Reversal Processing | 48 Hours |
| Escalated Review | 72 Hours |

---

## Allowed Actions

The AI agent may:

- Investigate duplicate debit.
- Check reversal status.
- Create dispute case.
- Escalate case.

The AI agent may NOT:

- Credit customer directly.
- Force reversal.
- Override banking records.

---

## Customer Communication Example

If duplicate debit is confirmed:

> We have identified a duplicate debit on your account. We are currently checking the reversal status. If a reversal has not yet been processed, a dispute case will be created for further investigation.

---

## AI Agent Instruction Summary

1. Verify customer.
2. Retrieve transaction history.
3. Detect duplicate debit.
4. Check reversal status.
5. Inform customer.
6. Create dispute if needed.
7. Escalate when required.