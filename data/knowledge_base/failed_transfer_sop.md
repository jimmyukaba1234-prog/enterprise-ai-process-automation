# Failed Transfer Standard Operating Procedure (SOP)

## Purpose

This document defines the process for handling customer complaints relating to failed transfers, delayed transfers, pending transfers, and beneficiary non-receipt of funds.

The AI Customer Operations Agent must follow this procedure before creating disputes or escalating cases.

---

## Definition

A failed transfer occurs when:

- A customer initiates a transfer.
- Funds may or may not be debited.
- The beneficiary does not receive value.
- The transaction remains pending, failed, or unknown.

---

## Customer Symptoms

Customers may report:

- "My transfer did not go through."
- "I sent money but the recipient has not received it."
- "My account was debited but the transfer failed."
- "Transfer is showing pending."
- "Money left my account but the beneficiary didn't get it."

---

## Required Verification

Before investigating a transfer:

1. Verify customer identity.
2. Confirm customer profile is active.
3. Confirm transaction belongs to the customer.

---

## Information Required

The AI agent should obtain or retrieve:

- Customer ID
- Transaction reference
- Transaction amount
- Transaction date
- Beneficiary bank
- Beneficiary account number (masked where possible)

---

## Investigation Process

### Step 1: Retrieve Transaction

Call Transaction API:

- get_transaction_details()

Retrieve:

- Transaction reference
- Status
- Amount
- Timestamp
- Beneficiary information

---

### Step 2: Check Transaction Status

Possible statuses:

- SUCCESS
- FAILED
- PENDING
- REVERSED

---

### Step 3: Status Handling

#### SUCCESS

If status is SUCCESS:

- Inform customer transfer completed successfully.
- Confirm beneficiary details.
- Advise beneficiary to check account balance and statement.

If customer still disputes receipt:

- Create investigation ticket.
- Escalate to Finance Operations.

---

#### FAILED

If status is FAILED:

Check reversal status.

Possible outcomes:

- Reversal completed
- Reversal pending
- Reversal not initiated

---

#### PENDING

If status is PENDING:

Inform customer:

> Your transfer is currently being processed. Some transfers may experience temporary delays due to network or interbank processing issues.

Provide estimated timeline.

Monitor until SLA expires.

---

#### REVERSED

If transaction is already reversed:

Inform customer:

> The transaction has been reversed and the funds have been returned to your account.

Provide reversal date and time if available.

---

## Reversal Investigation

Call:

- check_reversal_status()

Possible statuses:

- COMPLETED
- PENDING
- NOT_FOUND

---

## Escalation Conditions

Escalate when:

- Reversal exceeds SLA
- Transaction status cannot be determined
- API failure occurs
- Customer disputes system records
- Multiple failures occur on same account

Escalation Department:

Finance Operations

---

## SLA Guidelines

| Issue Type | SLA |
|------------|------|
| Pending Transfer | 24 Hours |
| Failed Transfer | 24 Hours |
| Reversal Pending | 48 Hours |
| Escalated Investigation | 72 Hours |

---

## Allowed Actions

The AI agent may:

- Check transaction status
- Check reversal status
- Provide timeline updates
- Create dispute ticket
- Escalate case

The AI agent may NOT:

- Force a transaction reversal
- Credit customer manually
- Modify transaction records

---

## AI Agent Instruction Summary

1. Verify customer.
2. Retrieve transaction.
3. Check status.
4. Check reversal if required.
5. Inform customer.
6. Create dispute if needed.
7. Escalate when SLA or policy requires.