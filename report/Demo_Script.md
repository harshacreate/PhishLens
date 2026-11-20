# PhishLens demo (6 minutes)

**Before the demo:** Run `docker compose up --build -d`, open http://localhost:8102, and check that all four tool lights are green.

| Time | Do | Say |
|---|---|---|
| 0:00 | Show the home page | “PhishLens checks links as text. It never opens them. The score is made on this computer.” |
| 0:30 | Check a low-risk link | “This link has low risk. Each bar shows how one part of the link changed the score. It uses the coefficient times the standardised value.” |
| 1:15 | Paste the suspended-account email | “This looks risky. The link has an `@` trick, a suspicious domain ending, and login words. The email sounds urgent and starts with a general greeting.” |
| 2:00 | Check the seven sample links at once | “I can check several links at once and see a summary.” |
| 2:30 | Open **Model study** and run the comparison | “The four models have about the same F1 score: 97%. The sample data has 3% wrong labels by design, so about 97% is the best score this data allows. When the scores are close, it helps to see why each model made its choice.” |
| 3:15 | Check `http://xn--pypal-4ve.com/signin` | “The model gives this link 4 out of 100. It learned shortcuts from its sample data. On 10 links I set aside, it caught 1. The extra checks for misspelled brand names and brand names joined to other words caught 9 of 10. They also had no false alerts.” |
| 4:30 | Show the network-check option | “Network checks need permission. I found a risk: a public-looking name could point to 127.0.0.1, a private address. Now the app looks up the name once, stops if any address is not public, and connects to the checked IP. This helps stop an SSRF attack and DNS rebinding.” |
| 5:30 | Close | “The main lesson is to test on links the model has not seen. Any questions?” |
