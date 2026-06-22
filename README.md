# Aegis AML MVP

This repository contains a minimal Streamlit MVP for Aegis, a privacy-preserving Anti-Money Laundering (AML) consortium platform. The goal is to demonstrate the core business logic of Aegis through a graduated disclosure protocol for collaboration between banks.

## Project Purpose

The Aegis AML MVP showcases a three-stage workflow that emphasizes privacy-preserving technologies:

1. **Stage 1 — Private Set Intersection (PSI) Simulation**: Users can check if a flagged customer/entity ID appears at other consortium banks without revealing specific bank identities.
2. **Stage 2 — Anonymous Risk Attestation Simulation**: If Stage 1 indicates cross-institutional presence, users can escalate to this stage to see if anonymous risk confirmations exist, along with an aggregate risk category.
3. **Stage 3 — Conditional Transaction Graph Disclosure**: This stage unlocks only if both Stage 1 and Stage 2 pass the required thresholds, allowing users to view a synthetic transaction graph or table.

## Important Notes

- This MVP does not implement production-grade cryptography. It simulates the outputs of cryptographic stages using synthetic data.
- The app is designed for educational purposes and investor demonstrations, emphasizing reduced duplicated AML investigations, privacy-preserving collaboration, and proportional disclosure.

## Running the App

To run the Streamlit app, ensure you have the required dependencies installed. You can install them using:

```bash
pip install -r requirements.txt
```

Then, run the app with the following command:

```bash
streamlit run app.py
```

## File Structure

- `app.py`: Main Streamlit application code.
- `requirements.txt`: Lists project dependencies.
- `AGENTS.md`: Instructions for the AI agent.
- `session-log.md`: Record of AI-agent use.
- `.gitignore`: Specifies files to ignore in Git.

This project is a demonstration of the Aegis AML platform's capabilities and is not intended for production use.