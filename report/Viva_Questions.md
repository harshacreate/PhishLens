# PhishLens — viva and interview questions

**1. Why logistic regression when random forests are usually stronger?** On this data all four models tie within one point (F1 0.962–0.970). Logistic regression gives exact per-feature attributions (β·z), which is the product's purpose. With a tie, explainability decides.

**2. Why is ~97% the ceiling?** The generator flips 3% of labels on purpose. No model can predict a random flip, so ~97% is the best achievable accuracy.

**3. What is shortcut learning, and where did you see it?** A model learns features that correlate with the label in the dataset but are not causal. The generator always paired punycode, '@' and brand tricks with suspicious TLDs and plain HTTP, so the model relied on those correlates. On hold-out probes with the same tricks on .com domains over HTTPS, it caught 1 of 10.

**4. Isn't the hybrid just overfitting to your probes?** That's why there are two probe sets. The development set guided the design, so its 10/10 is optimistic. The hold-out set was written and fixed before the hybrid existed and never used for tuning: 9/10 recall, 0/12 false positives. It's still small, so the confidence interval is wide.

**5. Define typosquatting and combosquatting.** Typosquatting registers a misspelling (paypa1.com, linkedln.com). Combosquatting joins a brand with other words (hdfc-netbanking-kyc-update.in). Kintis et al. (CCS 2017) found combosquatting more common and longer-lived.

**6. How do you avoid flagging the real brand's domain?** If the registered label is exactly the brand, the squatting rules never fire. A brand appearing only in the path (e.g. Wikipedia's PayPal article) is medium severity, so it doesn't trigger the floor.

**7. Explain the SSRF you fixed.** The domain check validated the *name* but not its DNS answer. A public name pointing to 127.0.0.1, 10.x or 169.254.169.254 made OpenSSL connect inside the container or network. The fix resolves once, rejects any non-global address, and connects to that vetted IP with SNI, so rebinding between lookups can't change the target.

**8. Why not fetch the page for better accuracy?** Fetching hostile pages is risky (exploits, tracking, alerting the attacker) and would make the tool unsafe to run locally. URL-only analysis is a deliberate scope choice.

**9. What's wrong with your registered-domain logic?** It takes the last two labels, which fails for suffixes like .co.uk or .gov.in. The Public Suffix List is the correct fix.

**10. How would you evaluate on real data?** A licensed corpus (e.g. a public phishing feed plus top-site lists) with a *time-based* split, so the test contains campaigns that appear after training. Report calibration and confidence intervals.
