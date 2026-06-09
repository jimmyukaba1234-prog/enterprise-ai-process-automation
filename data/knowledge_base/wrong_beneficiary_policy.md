# Wrong Beneficiary Transfer Recovery Policy

## Purpose

This policy defines the process for handling situations where a customer mistakenly transfers funds to the wrong account or beneficiary.

The objective is to provide guidance on recovery procedures while ensuring compliance with banking regulations and customer privacy requirements.

---

## Definition

A wrong beneficiary transfer occurs when a customer successfully transfers funds to an unintended recipient.

Examples include:

- Incorrect account number entered
- Incorrect beneficiary selected
- Transfer sent to wrong saved beneficiary
- Transfer sent to wrong bank account

---

## Important Notice

A successful transfer cannot automatically be reversed solely because the customer made an error.

Recovery depends on:

- Transaction status
- Recipient bank cooperation
- Recipient account status
- Applicable banking regulations

Recovery is not guaranteed.

---

## Customer Symptoms

Customers may report:

- "I transferred money to the wrong account."
- "I entered the wrong account number."
- "I sent money to the wrong person."
- "I selected the wrong beneficiary."

---

## Required Verification

Before discussing transaction details:

1. Verify customer identity.
2. Verify account ownership.
3. Confirm transaction belongs to customer.

---

## Required Information

The AI agent should retrieve:

- Transaction reference
- Transaction amount
- Transaction date
- Beneficiary account
- Beneficiary bank
- Transaction status

API:

- get_transaction_details()

---

## Investigation Process

### Step 1

Retrieve transaction details.

Confirm:

- Transaction reference
- Amount
- Beneficiary details
- Transaction status

---

### Step 2

Determine Transaction Status

Possible statuses:

- SUCCESS
- PENDING
- FAILED
- REVERSED

---

### SUCCESS

If transaction status is SUCCESS:

Inform customer:

> The transfer was successfully completed. Recovery of funds requires a formal investigation and cooperation from the receiving institution.

Create recovery case.

Escalate to Finance Operations.

---

### PENDING

If transaction is pending:

Inform customer:

> The transaction is still being processed. Recovery options will depend on the final transaction outcome.

Monitor transaction.

---

### FAILED

If transaction failed:

Check reversal status.

API:

- check_reversal_status()

If reversal completed, inform customer.

---

### REVERSED

If already reversed:

Inform customer that funds have been returned.

---

## Recovery Case Creation

API:

- create_recovery_case()

Case should contain:

- Customer ID
- Transaction reference
- Beneficiary details
- Recovery reason
- Investigation notes

---

## Escalation Rules

Escalate when:

- Transaction completed successfully
- Customer requests recovery
- Recovery investigation required
- Beneficiary bank involvement required

Department:

Finance Operations

---

## SLA Guidelines

| Issue | SLA |
|---------|------|
| Recovery Case Creation | Same Day |
| Initial Review | 24 Hours |
| Recovery Investigation | 3–10 Business Days |

---

## Allowed Actions

The AI agent may:

- Retrieve transaction details
- Create recovery case
- Escalate investigation
- Inform customer of recovery process

The AI agent may NOT:

- Reverse successful transfers
- Debit beneficiary accounts
- Guarantee fund recovery

---

## Customer Communication Example

> We have created a recovery request for the transaction. Recovery efforts will be initiated in line with banking procedures, although successful recovery cannot be guaranteed.

---

## AI Agent Instruction Summary

1. Verify customer.
2. Retrieve transaction.
3. Determine status.
4. Create recovery case.
5. Escalate to Finance Operations.
6. Explain recovery limitations.
7. Provide updates where available.