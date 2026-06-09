# Card Blocking and Card Security Policy

## Purpose

This policy defines how debit card and ATM card security incidents should be handled.

The objective is to prevent unauthorized usage and minimize financial loss.

---

## Definition

Card blocking is a security action that prevents further card transactions.

Blocking may be temporary or permanent depending on the situation.

---

## Situations Requiring Card Blocking

A card may need to be blocked when:

- Card is lost
- Card is stolen
- Unauthorized transactions occur
- Card compromise is suspected
- Customer requests card suspension
- Fraud team recommends card restriction

---

## Customer Symptoms

Customers may report:

- "My card is missing."
- "My ATM card was stolen."
- "Someone is using my card."
- "I lost my debit card."
- "Please block my card."
- "My card details may have been exposed."

---

## Required Verification

Before card status is discussed:

1. Verify customer identity.
2. Verify card ownership.
3. Verify customer account relationship.

---

## Card Status Investigation

API:

- get_card_status()

Retrieve:

- Card status
- Card type
- Last transaction
- Card ownership information

---

## Possible Card Statuses

- ACTIVE
- BLOCKED
- EXPIRED
- RESTRICTED
- REPLACEMENT_PENDING

---

## Customer Requests Card Block

If customer requests card block:

### Step 1

Verify customer.

### Step 2

Confirm reason for block.

Possible reasons:

- Lost card
- Stolen card
- Suspected fraud
- Temporary security concern

### Step 3

Initiate block request.

API:

- block_card()

---

## Stolen Card Procedure

If card is reported stolen:

1. Verify customer.
2. Block card immediately.
3. Create fraud case.
4. Escalate to Fraud Team.
5. Recommend card replacement.

---

## Lost Card Procedure

If card is reported lost:

1. Verify customer.
2. Block card.
3. Offer replacement process.
4. Inform customer of replacement timelines.

---

## Replacement Card Requests

If replacement is requested:

API:

- request_card_replacement()

Provide:

- Replacement timeline
- Collection instructions
- Applicable fees

---

## Escalation Rules

Escalate when:

- Card fraud is suspected
- Multiple unauthorized transactions exist
- Card block request fails
- Customer disputes card activity

Department:

Fraud and Risk Management

---

## SLA Guidelines

| Issue | SLA |
|---------|------|
| Card Block Request | Immediate |
| Fraud Escalation | Immediate |
| Replacement Request | Same Day |
| Card Delivery | Bank Defined Timeline |

---

## Allowed Actions

The AI agent may:

- Check card status
- Block card
- Request replacement
- Create fraud case
- Escalate to Fraud Team

The AI agent may NOT:

- Reactivate blocked cards without approval
- Modify card ownership details
- Override fraud restrictions

---

## Customer Communication Example

> Your card protection request has been processed. The card has been restricted from further use and a replacement request can be initiated if required.

---

## AI Agent Instruction Summary

1. Verify customer.
2. Confirm card ownership.
3. Check card status.
4. Block card if required.
5. Create fraud case if needed.
6. Escalate when necessary.
7. Provide replacement guidance.