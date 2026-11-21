PhishLens interview questions

1. Why use logistic regression instead of a random forest?

All four models scored about the same on this test. Their F1 scores were from 0.962 to 0.970. F1 is one score that combines how many phishing links were found and how often a phishing result was right. Logistic regression also shows which link details changed the score. That helps explain each result.

2. Why is the best score close to 97%?

The sample maker changed 3% of the answers at random. A model cannot know which answers were changed. So this test data can support about 97% accuracy at most.

3. What is shortcut learning, and where did it happen here?

Shortcut learning is when a model relies on a pattern that often appears with an answer, even though that pattern does not prove the answer is right. The sample maker always put punycode, `@` signs, and brand-name tricks with odd domain endings and plain HTTP. The model learned those patterns. In a test with the same tricks on HTTPS `.com` sites, it found 1 of 10 phishing links.

4. Did the combined model just learn the test links?

There were two test sets. I used the first while making the model, so its result of 10 out of 10 may be too high. I made and saved the second set before I made the combined model. I did not use it to tune the model. The combined model found 9 of 10 phishing links and gave no wrong alerts on 12 safe links. This test is small, so the result may change with more links.

5. What do typosquatting and combosquatting mean?

Typosquatting uses a misspelled brand name, such as `paypa1.com` or `linkedln.com`. Combosquatting adds other words to a brand name, such as `hdfc-netbanking-kyc-update.in`. Kintis et al. (CCS 2017) found that combosquatting was more common and lasted longer.

6. How does the app avoid flagging a real brand site?

A registered domain is the main name a person or group has registered, such as `paypal.com`. The brand rules do not flag a site when its registered domain is exactly the brand name. If a brand name appears only in the page path, such as a Wikipedia article about PayPal, the result is medium risk. It does not reach the alert level.

7. What was the SSRF problem you fixed?

The app checked a domain name but did not check the IP address it led to. A public-looking name could point to a private address such as `127.0.0.1`, `10.x`, or `169.254.169.254`. OpenSSL could then connect to the app's own container or network. Now the app looks up the name once, stops if any address is not public, and connects to the checked address. It still uses the domain name for SNI. This stops DNS rebinding from changing the address after the check.

8. Why not open each page to get a better result?

Opening an unknown page can expose the app to attacks or tracking. It can also alert the site owner. PhishLens checks the link text only. This is a planned limit.

9. Why is the last part of the domain not enough?

Checking only the last two parts fails for endings such as `.co.uk` and `.gov.in`. The Public Suffix List keeps track of these endings and helps find the right registered domain.

10. How would you test the app with public data?

Use data that allows this kind of test, such as a public phishing list and a list of popular sites. Split data by date, so the test includes attacks that appeared after training. Report how often a score matches the real risk, and show a range to explain how much the result may change.
