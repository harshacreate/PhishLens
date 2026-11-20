# PhishLens interview questions

1. Why use logistic regression instead of a random forest?

All four models scored close to each other on this test: F1 from 0.962 to 0.970. Logistic regression can show how each feature affected its result. That fits the goal of PhishLens, which explains its results.

2. Why is the score near 97% at best?

The data maker changes 3% of the labels at random. No model can know which labels were changed, so about 97% is the best accuracy this data can support.

3. What is shortcut learning? Where did it happen here?

Shortcut learning is when a model uses clues that often appear with a label in its training data, even when those clues do not prove the label. The data maker always put punycode, @ signs and brand tricks with odd domain endings and plain HTTP. The model learned these clues. In a test with the same tricks on .com sites using HTTPS, it caught 1 of 10 cases.

4. Did the hybrid model just learn your test cases?

There were two test sets. The first one helped shape the model, so its 10 out of 10 result may be too high. The second set was made and fixed before the hybrid model existed, and it was not used to tune the model. The hybrid caught 9 out of 10 phishing cases and gave no false alerts on 12 safe cases. This test is small, so there is a lot of uncertainty.

5. What do typosquatting and combosquatting mean?

Typosquatting uses a misspelled brand name, like paypa1.com or linkedln.com. Combosquatting adds other words to a brand name, like hdfc-netbanking-kyc-update.in. Kintis et al. (CCS 2017) found that combosquatting was more common and lasted longer.

6. How does the app avoid flagging the real brand site?

The brand rules do not fire when the registered domain name is exactly the brand. If the brand name appears only in the page path, such as in a Wikipedia article about PayPal, the result is medium risk. It does not raise the score to the alert level.

7. What was the SSRF problem you fixed?

The app checked the domain name, but not the IP address it led to. A public domain could point to an internal address such as 127.0.0.1, 10.x or 169.254.169.254. OpenSSL could then connect to the app's own container or network. The fix checks the address once, rejects any address that is not public, and connects to that checked address while keeping the domain name for SNI. This stops DNS rebinding from changing the address between checks.

8. Why not open each page to get a better result?

Opening unknown pages can expose the app to attacks, tracking, or alerting the attacker. PhishLens checks the URL text only. That is a planned limit of the app.

9. What is wrong with checking only the last two parts of a domain?

That rule fails on endings such as .co.uk and .gov.in. The Public Suffix List gives the right registered domain for these cases.

10. How would you test the app with real data?

Use a data set that allows this kind of test, such as a public phishing list and a list of popular sites. Split the data by date so the test includes attacks that appeared after training. Also report how well the scores match the real risk and include confidence intervals.
