# Customer Verification Policy

## Document Purpose

This policy defines how customer identity must be verified before the AI Customer Operations Agent can provide account-specific information, investigate transactions, create disputes, escalate complaints, or trigger sensitive actions.

The AI agent must never disclose account, card, transaction, or personal information unless the customer has been reasonably verified.

---

## When Verification Is Required

Customer verification is required before handling any of the following requests:

- Checking account balance or account status
- Investigating failed transfers
- Investigating double debit complaints
- Checking reversal status
- Reviewing transaction history
- Reporting unauthorized transactions
- Blocking a card
- Blocking or restricting an account
- Creating a dispute case
- Creating a fraud case
- Updating customer information
- Checking KYC status
- Checking complaint status

---

## Low-Risk Requests

Verification may not be required for general information requests, such as:

- Branch opening hours
- General product information
- How to reset password
- General transaction processing timelines
- General card delivery timelines
- General complaint escalation timelines

For low-risk requests, the AI agent may provide general guidance without accessing customer records.

---

## Minimum Verification Requirement

Before accessing customer-specific records, the AI agent must confirm that a valid customer ID exists in the session.

The customer ID may come from:

- Mobile banking app session
- Internet banking session
- WhatsApp banking session
- Contact center CRM
- Verified USSD session

If no customer ID is available, the agent must ask the customer to continue through a verified banking channel.

---

## Verification Checks

The agent should perform the following checks using the customer API:

1. Confirm that the customer ID exists.
2. Confirm that the customer profile is active.
3. Confirm that the customer is not restricted from digital support.
4. Confirm that the request matches the customer’s account/card/transaction records.
5. Confirm whether stronger verification is required for sensitive actions.

---

## Strong Verification Required

Strong verification is required before any high-risk action, including:

- Blocking a card
- Blocking an account
- Restricting an account
- Reporting fraud
- Creating a fraud case
- Viewing sensitive transaction history
- Changing customer details
- Initiating recovery for wrong beneficiary transfer

Strong verification may include:

- OTP confirmation
- Security question
- In-app authentication
- Call center confirmation
- Biometric confirmation
- PIN validation through secure banking channel

The AI agent must not ask the customer to reveal their full PIN, full password, full card PAN, CVV, or OTP in plain text chat unless handled through a secure verified channel.

---

## Information the Agent Must Never Request

The AI agent must never ask for:

- Full card number
- CVV
- Full PIN
- Full password
- Full OTP in an unsecured chat
- Internet banking password
- Mobile app password
- Full BVN/NIN in plain text

If the customer shares sensitive information, the agent should warn the customer not to share such details and avoid storing it in logs.

---

## Verification Failure Handling

If verification fails, the agent must:

1. Politely inform the customer that identity could not be confirmed.
2. Avoid disclosing account-specific information.
3. Provide general guidance only.
4. Recommend secure support channels where necessary.
5. Escalate only if there is a fraud or safety risk.

Example response:

> I’m unable to confirm your identity from this session, so I can’t access account-specific details here. Please continue through the verified banking app, internet banking, or contact the support center for secure assistance.

---

## Action Rules After Verification

If verification succeeds, the AI agent may:

- Retrieve relevant account or transaction details
- Check transaction status
- Check reversal status
- Check card status
- Create a dispute case
- Create a complaint ticket
- Escalate to the correct department
- Provide personalized resolution guidance

For high-risk actions, the agent must still check whether strong verification is required.

---

## Escalation Rules

The agent must escalate to a human support team when:

- Customer verification fails but fraud risk is suspected
- The customer reports unauthorized transactions
- The customer requests account restriction
- Transaction details are unclear
- API response is unavailable
- The customer is angry or distressed
- The issue exceeds SLA
- The policy does not clearly allow the requested action

---

## Compliance Notes

All customer support actions must be logged for audit purposes.

Logs should include:

- Customer ID
- Issue type
- Verification status
- API calls made
- Action taken
- Escalation status
- Timestamp
- Agent response summary

Sensitive information such as PINs, passwords, CVV, OTP, and full card numbers must not be stored in logs.

---

## AI Agent Instruction Summary

The AI agent must always follow this order:

1. Understand the customer request.
2. Determine whether verification is required.
3. Confirm customer ID from the session.
4. Call the customer API to validate the customer profile.
5. Decide whether normal or strong verification is required.
6. Retrieve only the information needed to resolve the issue.
7. Avoid requesting or exposing sensitive information.
8. Respond clearly and safely.
9. Escalate when policy, risk, or system limits require it.