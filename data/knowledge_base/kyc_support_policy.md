# KYC and Customer Information Management Policy

## Purpose

This policy defines how the AI Customer Operations Agent should handle customer inquiries relating to Know Your Customer (KYC) requirements, profile updates, account restrictions, and customer information management.

The objective is to provide customers with accurate guidance while ensuring compliance with regulatory requirements.

---

## Definition

Know Your Customer (KYC) refers to the process of verifying and maintaining accurate customer identification and profile information.

KYC requirements are necessary to:

- Prevent fraud
- Prevent money laundering
- Meet regulatory obligations
- Protect customer accounts
- Enable uninterrupted banking services

---

## Common Customer Requests

Customers may ask:

- "How do I update my KYC?"
- "Why is my account restricted?"
- "How do I increase my transaction limit?"
- "How do I update my phone number?"
- "How do I update my email address?"
- "How do I update my address?"
- "Why can I not transfer money?"
- "Why is my account limited?"

---

## Verification Requirements

Before discussing customer-specific KYC information:

1. Verify customer identity.
2. Confirm customer profile ownership.
3. Confirm account status.

---

## Customer Profile Investigation

API:

- get_customer_profile()

Retrieve:

- Customer status
- KYC level
- Verification status
- Account restrictions
- Registered contact information

---

## KYC Levels

Possible KYC classifications:

### Basic KYC

Typical characteristics:

- Limited transaction thresholds
- Limited account functionality

---

### Standard KYC

Typical characteristics:

- Increased transaction limits
- Additional banking services

---

### Enhanced KYC

Typical characteristics:

- Higher transaction limits
- Full account functionality
- Additional verification completed

---

## Common Restriction Reasons

An account may be restricted due to:

- Missing KYC documentation
- Expired identification
- Regulatory review
- Fraud investigation
- Compliance review
- Customer-requested restriction

---

## Phone Number Update Requests

If customer requests phone number update:

Advise customer to:

- Use approved banking channels
- Visit a branch if required
- Complete verification procedures

The AI agent must not directly modify customer records.

---

## Email Update Requests

If customer requests email update:

Provide approved update process.

The AI agent must not directly modify customer records.

---

## Address Update Requests

If customer requests address update:

Provide required documentation guidance.

The AI agent must not directly modify customer records.

---

## Transaction Limit Inquiries

If customer requests higher limits:

Check KYC level.

Explain:

- Current limit category
- Additional requirements
- Upgrade process

---

## Escalation Rules

Escalate when:

- Restriction reason cannot be determined
- Regulatory review exists
- Customer disputes restriction
- Compliance approval is required

Department:

Customer Operations

Compliance Team when applicable.

---

## Allowed Actions

The AI agent may:

- Check KYC status
- Explain KYC requirements
- Explain account restrictions
- Provide update procedures
- Escalate cases

The AI agent may NOT:

- Modify customer records
- Approve KYC upgrades
- Remove restrictions
- Override compliance decisions

---

## Customer Communication Example

> Your account currently requires additional verification to access certain services. Once the required information is submitted through an approved banking channel, your profile will be reviewed accordingly.

---

## AI Agent Instruction Summary

1. Verify customer.
2. Retrieve customer profile.
3. Determine KYC status.
4. Explain requirements.
5. Provide next steps.
6. Escalate when necessary.
7. Log customer interaction.