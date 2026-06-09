# Chargeback and Card Dispute Policy

## Purpose

This policy defines how card transaction disputes and chargeback requests should be handled.

Chargebacks allow customers to dispute eligible card transactions when goods, services, or transactions are questionable or unauthorized.

---

## Definition

A chargeback is a formal dispute raised against a card transaction.

Common reasons include:

- Unauthorized card transaction
- Goods not received
- Services not delivered
- Duplicate card charges
- Merchant dispute
- Incorrect transaction amount

---

## Customer Symptoms

Customers may report:

- "I want to dispute a card payment."
- "The merchant charged me incorrectly."
- "I never received the product."
- "I paid but the service was not provided."
- "This transaction was not authorized."

---

## Required Verification

Before discussing transaction details:

1. Verify customer identity.
2. Verify card ownership.
3. Verify transaction ownership.

---

## Required Information

Retrieve:

- Transaction reference
- Transaction amount
- Merchant name
- Transaction date
- Card type

API:

- get_transaction_details()

---

## Eligibility Review

Before creating a chargeback request:

API:

- check_chargeback_eligibility()

Verify:

- Transaction falls within dispute period
- Transaction is card-based
- Transaction has not already been resolved
- Transaction qualifies under chargeback rules

---

## Common Eligible Scenarios

### Unauthorized Card Use

Examples:

- Card stolen
- Card compromised
- Fraudulent online purchase

---

### Goods Not Received

Examples:

- Customer paid merchant
- Merchant failed to deliver

---

### Service Not Provided

Examples:

- Booking cancelled
- Merchant failed to perform service

---

### Duplicate Merchant Charge

Examples:

- Merchant charged customer multiple times

---

## Ineligible Scenarios

Examples:

- Customer changes mind after valid purchase
- Merchant fulfilled service correctly
- Transaction falls outside dispute window

---

## Chargeback Creation

API:

- create_chargeback_request()

Store:

- Customer ID
- Transaction reference
- Merchant details
- Dispute reason
- Supporting information

---

## Escalation Rules

Escalate when:

- High-value disputes exist
- Merchant challenge is expected
- Multiple disputes are detected
- Fraud investigation is required

Department:

Finance Operations

Fraud Team if fraud suspected.

---

## SLA Guidelines

| Issue | SLA |
|---------|------|
| Eligibility Review | Same Day |
| Chargeback Creation | Same Day |
| Investigation | 7–30 Business Days |
| Final Resolution | Card Scheme Timeline |

---

## Allowed Actions

The AI agent may:

- Check transaction details
- Verify eligibility
- Create chargeback request
- Escalate case

The AI agent may NOT:

- Approve chargeback
- Refund customer automatically
- Override card scheme decisions

---

## Customer Communication Example

> Your dispute request has been submitted for review. The transaction will be assessed according to applicable chargeback rules and card scheme procedures.

---

## AI Agent Instruction Summary

1. Verify customer.
2. Retrieve transaction.
3. Check chargeback eligibility.
4. Create chargeback request.
5. Escalate if necessary.
6. Inform customer of review timeline.
7. Track case until resolution.