# PhishLens — demonstration script (6 minutes)

**Setup:** `docker compose up --build -d`, open http://localhost:8102, confirm the four tool pills are green.

| Time | Do | Say |
|---|---|---|
| 0:00 | Landing page | "PhishLens never opens the links it analyses. Everything here is offline scoring." |
| 0:30 | Click a low-risk example | "Low risk. Note the feature drivers: each bar is coefficient × standardised value — the exact reason, not an approximation." |
| 1:15 | Paste the suspended-account e-mail | "High risk. Signals: '@' trick, suspicious TLD, credential keywords; e-mail cues: urgency, generic greeting." |
| 2:00 | Batch mode with the seven sample URLs | "Batch scoring with a summary." |
| 2:30 | Model study → Run comparison | "Four models tie at ~97% F1. That's the ceiling from 3% label noise. When accuracy ties, explanation decides." |
| 3:15 | Analyse `http://xn--pypal-4ve.com/signin` | "The model alone says 4/100. It learned shortcuts from its generator. On a hold-out set I fixed in advance it caught 1 of 10. Typosquat/combosquat signals plus a risk floor catch 9 of 10, with no false positives." |
| 4:30 | Explain enrichment checkbox | "Network checks need explicit authorization. In review I found an SSRF: a name resolving to 127.0.0.1 would have been contacted. Now I resolve once, refuse non-public IPs and connect to the vetted IP." |
| 5:30 | Close | "Lesson: measure generalisation, not just accuracy. Questions?" |
