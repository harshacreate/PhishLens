PhishLens demo (6 minutes)

Before the demo, run `docker compose up --build -d`, open http://localhost:8102, and check that all four tool lights are green.

Time: 0:00; Show: Show the home page.; Say: “PhishLens checks the text in a link. It does not open the link. It works out the score on this computer.”

Time: 0:30; Show: Check a low-risk link.; Say: “This link looks low risk. Each bar shows how one part of the link changed the score.”

Time: 1:15; Show: Paste the suspended-account email.; Say: “This looks risky. The link uses an `@` trick, has an odd domain ending, and asks for login details. The email uses urgent words and a general greeting.”

Time: 2:00; Show: Check the seven sample links at once.; Say: “I can check several links together and see one summary.”

Time: 2:30; Show: Open Model study and run the comparison.; Say: “The four models scored about the same. Their F1 scores were near 97%. The sample has 3% wrong answers by design, so it cannot support a score much above 97%. When models score close, it helps to see why each one made its choice.”

Time: 3:15; Show: Check `http://xn--pypal-4ve.com/signin`.; Say: “The model gives this link a score of 4 out of 100. It learned shortcuts from its sample links. In a small test set aside from the training data, it found 1 of 10 phishing links. Extra checks for misspelled brand names and added brand words found 9 of 10. They gave no wrong alerts on 12 safe links.”

Time: 4:30; Show: Show the network-check option.; Say: “Network checks need permission. I found a safety problem: a name that looks public could point to a private address, like `127.0.0.1`. This could let the app reach a private network, which is called SSRF. A site could also change its address between checks, which is called DNS rebinding. Now the app checks the name once, stops if any address is not public, and connects to the address it checked.”

Time: 5:30; Show: Close.; Say: “The main lesson is to test a model on links it has not seen before. Any questions?”
