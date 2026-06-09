# Unauthorized Transaction Investigation Policy

## Purpose

This policy defines the process for handling customer reports of transactions that were not authorized by the customer.

Unauthorized transaction reports are treated as potential fraud incidents and must be handled with high priority.

---

## Definition

An unauthorized transaction is any transaction that the customer claims they did not initiate, approve, or benefit from.

Examples include:

- Card fraud
- Mobile banking compromise
- Internet banking compromise
- Account takeover
- Social engineering scams
- Unknown POS transactions
- Unknown ATM withdrawals
- Unknown transfers

---

## Risk Classification

All unauthorized transaction reports must be classified as:

Priority: Critical

Department: Fraud and Risk Management

Potential Financial Risk: High

---

## Customer Symptoms

Customers may report:

- "I did not make this transaction."
- "Someone withdrew money from my account."
- "I did not authorize this transfer."
- "My account has been hacked."
- "I received a debit alert for a transaction I didn't perform."
- "I noticed suspicious activity on my account."

---

## Required Verification

Before discussing transaction details:

1. Verify customer identity.
2. Confirm account ownership.
3. Confirm customer profile status.
4. Confirm customer relationship to affected account.

---

## Initial Investigation

### Step 1

Retrieve recent transaction history.

API:

- get_recent_transactions()

Retrieve:

- Amount
- Date
- Time
- Channel
- Merchant
- Reference Number

---

### Step 2

Identify disputed transaction.

Collect:

- Transaction reference
- Amount
- Date
- Transaction type

---

### Step 3

Flag transaction as suspicious.

API:

- flag_suspicious_transaction()

---

## Immediate Protection Actions

The AI agent should evaluate whether account protection is required.

Potential actions:

- Recommend card block
- Recommend account restriction
- Create fraud case
- Escalate to Fraud Team

---

## Fraud Indicators

High-risk indicators include:

- Multiple unknown debits
- Transactions from unusual locations
- Multiple failed login attempts
- New device activity
- High-value transfers
- ATM withdrawals customer denies

---

## Escalation Rules

Escalate immediately when:

- Customer confirms fraud
- Multiple suspicious transactions exist
- Account compromise is suspected
- Customer requests investigation
- Card theft is reported

Department:

Fraud and Risk Management

---

## SLA Guidelines

| Issue | SLA |
|---------|------|
| Fraud Report Creation | Immediate |
| Fraud Team Assignment | 1 Hour |
| Initial Investigation | 24 Hours |
| Full Investigation | 3–7 Business Days |

---

## Allowed Actions

The AI agent may:

- Retrieve transaction history
- Flag suspicious activity
- Create fraud case
- Escalate case
- Recommend card block
- Recommend account restriction

The AI agent may NOT:

- Refund customer automatically
- Close investigation
- Remove fraud flags
- Reverse transactions

---

## Customer Communication Example

> We have flagged the reported transaction for investigation and created a fraud case for review. To protect your account, additional security measures may be recommended while the investigation is ongoing.

---

## AI Agent Instruction Summary

1. Verify customer.
2. Retrieve transactions.
3. Identify suspicious activity.
4. Create fraud case.
5. Recommend protection actions.
6. Escalate immediately.
7. Keep customer informed.