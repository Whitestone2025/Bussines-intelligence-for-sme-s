# See Your Frontend

Your frontend is the local review surface where you inspect your case.

## How It Should Work

Once Codex has loaded your business, it should run:

```bash
python3 scripts/serve_ui.py
```

Then it should give you the local URL.

On a clean installation, Codex should also explain that the repo setup is already done and that the frontend now corresponds to your own business case.

## What You Should Expect To See

- your business as the active case,
- thesis and recommendation,
- customer and market summary,
- viability and pricing view,
- decision and plan,
- in-app document reader,
- and audit mode if you want to inspect traceability.

## If The Frontend Is Empty

That means your business has not been loaded yet.
Tell Codex to continue the onboarding instead of trying to fix the repo yourself.

Example:

```text
Sigue con Ws B-I y no te detengas hasta que mi negocio aparezca en el frontend.
```
