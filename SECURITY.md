# Security

PhishLens is an educational project for Design Project II, Semester IV of B.Tech Cyber Security. It is made to run on your own computer with local data. It is not made for use on a public network.

## Supported versions

| Version | Supported |
|---|---|
| 1.1.x (main) | Yes |
| Earlier versions | No |

## Report a security issue

Do not post a security issue in a public issue. Use GitHub’s private report form: open the **Security** tab and choose **Report a vulnerability**. Include the version or commit, steps to repeat the problem, and what happened.

Expected response: a reply within 7 days. For a confirmed issue, a fix or plan is expected within 30 days. Credit can be added to the changelog if you ask.

You may test your own local copy. Do not test a system or account unless you own it or have permission.

## What this app handles

PhishLens checks pasted links and email text. It can also look up public domain details when you turn on that option. The browser and Flask app run on the same computer. There are no user accounts. The app is not meant to be open to a network.

| Risk | What the app does |
|---|---|
| The app opens a harmful link | It checks the text and link details. It does not open or fetch the link. |
| Lookups used against others | WHOIS, DNS, and TLS lookups need an ownership or permission flag. They accept public domain names only. IPs, private addresses, and local names are refused. Each client can make up to 10 lookups per minute. |
| A domain points to an internal address | Before a TLS check, the app looks up the domain once. If any address is not public, including loopback, private, link-local, or metadata addresses, it stops. OpenSSL then connects to the checked IP with SNI. This helps stop DNS rebinding from changing the target. |
| Too much trust in a score | Each score shows the signs behind it. The page says the model was trained on made-up data. |
| Too much work at once | Limits are 128 KB per request, 20,000 characters per input, and 25 links per batch. Lookups and model comparison have rate limits. |
| Script attacks from a link | The page escapes link text before showing it and uses a same-origin Content Security Policy. |

## How the code is kept safer

- Each API route checks input type, size, and range. Errors use JSON.
- Each reply has security headers. API replies are marked `Cache-Control: no-store`.
- Logs include a request ID, but never the request data.
- Users see a general error for a server fault. The full error stays in the server log.
- Program calls use fixed argument lists, no shell, and time limits.
- The Docker app runs as a non-root user. CI runs the tests on every push.

## Limits

This project has not had an outside security review. It has no sign-in because it is for one user on one computer. See the README for other limits.
