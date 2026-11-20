# PhishLens demo (6 minutes)

Before the demo, run `docker compose up --build -d`, open http://localhost:8102, and check that all four tool lights are green.

| Time | Show | Say |
|---|---|---|
| 0:00 | Show the home page. | “PhishLens checks the text in a link. It does not open the link. It works out the score on this computer.” |
| 0:30 | Check a low-risk link. | “This link looks low risk. Each bar shows how one part of the link changed the score.” |
| 1:15 | Paste the suspended-account email. | “This looks risky. The link uses an `@` trick, has an odd domain ending, and asks for login details. The email uses urgent words and a general greeting.” |
| 2:00 | Check the seven sample links at once. | “I can check several links together and see one summary.” |
| 2:30 | Open Model study and run the comparison. | “The four models scored about the same. Their F1 scores were near 97%. The sample has 3% wrong answers by design, so it cannot support a score much above 97%. When models score close, it helps to see why each one made its choice.” |
| 3:15 | Check `http://xn--pypal-4ve.com/signin`. | “The model gives this link a score of 4 out of 100. It learned shortcuts from its sample links. In a small test set aside from the training data, it found 1 of 10 phishing links. Extra checks for misspelled brand names and added brand words found 9 of 10. They gave no wrong alerts on 12 safe links.” |
| 4:30 | Show the network-check option. | “Network checks need permission. I found a safety problem: a name that looks public could point to a private address, like `127.0.0.1`. This could let the app reach a private network, which is called SSRF. A site could also change its address between checks, which is called DNS rebinding. Now the app checks the name once, stops if any address is not public, and connects to the address it checked.” |
| 5:30 | Close. | “The main lesson is to test a model on links it has not seen before. Any questions?” |
