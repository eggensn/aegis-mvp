# AGENTS.md — Aegis AML MVP

## Project purpose

This repository contains a minimal Streamlit MVP for Aegis, a privacy-preserving AML consortium platform.

The goal is to demonstrate the core business logic of Aegis: a graduated disclosure protocol for anti-money laundering collaboration between banks. Each stage only reveals more information when the previous stage has justified escalation.

This MVP is for an educational product demo. It should be simple, readable, and investor-demo friendly.

## Core concept

Aegis chains privacy-preserving technologies into a three-stage workflow:

1. Stage 1 — Private Set Intersection (PSI) simulation
2. Stage 2 — Zero-Knowledge Proof (ZKP) / anonymous risk attestation simulation
3. Stage 3 — Conditional transaction graph disclosure

The legal logic and the technical logic should stay aligned:
- Stage 1 answers whether the entity appears elsewhere.
- Stage 2 answers whether anonymous risk confirmations exist.
- Stage 3 only unlocks wider transaction graph information after Stages 1 and 2 justify escalation.

The main architectural idea is graduated disclosure: the system assesses whether sharing is necessary before sharing sensitive information.

## Important limitation

This MVP does not implement production-grade cryptography.

Do not claim that the software performs real PSI, real ZKP, ring signatures, threshold cryptography, or live AML detection.

Instead, the MVP simulates the outputs of these cryptographic stages using synthetic data so that the workflow, user experience, and business logic can be demonstrated.

Use wording such as:
- "PSI simulation"
- "ZKP attestation simulation"
- "anonymous risk attestation simulation"
- "synthetic transaction graph"
- "production version would require audited cryptographic libraries"

## Minimal file structure

Keep the project as simple as possible.

Preferred files:
- `app.py` — main Streamlit app
- `README.md` — human-readable project explanation and run instructions
- `AGENTS.md` — AI-agent instructions
- `session-log.md` — short record of AI-agent use
- `requirements.txt` — Python dependencies
- `.gitignore` — ignored local files

Do not create extra folders or extra files unless they are clearly necessary.

Keep most or all code in `app.py` for the first MVP.

## MVP features to implement

The Streamlit app should show a simple investigator dashboard for a consortium bank.

### Stage 1 — PSI simulation

The user should be able to:
- Select or enter a flagged customer/entity ID.
- Run a Stage 1 check.
- See whether the entity is present at other consortium banks.
- See a count of matching banks.
- Not see which specific banks matched.

Required privacy rule:
- Do not reveal individual bank names in Stage 1 output.

Example output:
- Entity found elsewhere: Yes
- Number of other banks: 3
- Bank identities: Hidden

### Stage 2 — Anonymous risk attestation simulation

If Stage 1 shows cross-institutional presence, the user can escalate to Stage 2.

The app should show:
- Whether anonymous risk confirmations exist.
- A simple aggregate risk category, such as Low, Medium, or High.
- A verification status, such as "Attestation verified."
- No individual bank identities.
- No dates, rationales, or bank-specific risk details.

Required privacy rule:
- Do not reveal which banks flagged, investigated, or denied service to the entity.

Example output:
- Anonymous risk confirmations: 2
- Aggregate risk category: High
- Source banks: Hidden
- Attestation status: Verified

### Stage 3 — Conditional transaction graph disclosure

Stage 3 should stay locked unless Stage 1 and Stage 2 pass the required thresholds.

If Stage 3 unlocks, the app can show a simple synthetic transaction graph or transaction table.

The purpose of Stage 3 is to demonstrate that deeper knowledge sharing only happens after privacy-preserving checks justify escalation.

Example output:
- Stage 3 unlocked
- Synthetic related accounts
- Synthetic transaction amounts
- Simplified suspicious network view

Required rule:
- Use synthetic data only.
- Make clear that this is a demo graph, not real transaction data.

## Suggested thresholds

Use simple demo thresholds:

- Stage 1 passes if the entity appears at 2 or more other banks.
- Stage 2 passes if anonymous risk confirmations are 1 or more.
- Stage 3 unlocks only if both Stage 1 and Stage 2 pass.

These thresholds are for the MVP only and should be described as configurable in a real product.

## UX rules

The app should be easy to understand for a non-technical viewer.

Use clear headings:
- Aegis AML MVP
- Stage 1 — PSI Simulation
- Stage 2 — Anonymous Risk Attestation
- Stage 3 — Conditional Transaction Graph

Use short explanatory text under each stage.

The user should always understand:
- What information is being checked.
- What is revealed.
- What remains hidden.
- Why the next stage is or is not unlocked.

The product demo should feel investor-oriented:
- Emphasize reduced duplicated AML investigations.
- Emphasize privacy-preserving collaboration.
- Emphasize proportional disclosure.
- Emphasize detection of cross-bank suspicious networks.

## Coding rules

- Keep the code simple and readable.
- Prefer plain Python and Streamlit.
- Use synthetic in-code data if that avoids extra files.
- Add short comments for important business logic.
- Avoid overengineering.
- Avoid unnecessary classes.
- Avoid unnecessary folders.
- Avoid external APIs.
- Avoid real customer data.
- Avoid complex cryptographic libraries in the MVP.
- Do not expose individual bank identities in Stage 1 or Stage 2.

## Recommended dependencies

Use only minimal dependencies.

Preferred `requirements.txt`:
- streamlit
- pandas

Only add another package if absolutely necessary.

## Testing instructions

Before committing, run:

```bash
streamlit run app.py