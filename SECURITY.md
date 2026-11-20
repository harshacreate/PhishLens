# Security

PhishLens is a learning project for Design Project II, Semester IV of B.Tech Cyber Security. It runs on your computer and uses local data. Do not use it on a public network.

## Supported versions

| Version | Supported |
|---|---|
| 1.1.x (main) | Yes |
| Earlier versions | No |

## Report a security issue

Do not report a security issue in a public issue. Open GitHub's Security tab and choose Report a vulnerability. Include the version or commit, steps to repeat the problem, and what happened.

I aim to reply within 7 days. If I confirm the issue, I aim to share a fix or plan within 30 days. I can add your name to the change log if you ask.

You may test your own copy on your computer. Do not test a system or account unless you own it or have permission.

## What this app checks

PhishLens checks links and email text that you paste. If you choose, it can also look up details about public domains. Your browser and the Flask app run on the same computer. There are no user accounts. Do not open the app to a network.

| Risk | What the app does |
|---|---|
| The app opens a harmful link | It checks the text and link details. It does not open the link or fetch the page. |
| Lookups used without permission | WHOIS, DNS, and TLS lookups need an ownership or permission flag. They accept public domain names only. IP addresses, private addresses, and local names are refused. Each client can make up to 10 lookups per minute. |
| A domain points to a private address | Before a TLS check, the app looks up the domain once. If any result is not a public address, including loopback, private, link-local, or metadata addresses, it stops. OpenSSL then connects to the checked IP address and sends SNI, the site name used during TLS. This helps stop DNS rebinding, where a domain changes its address after the check. |
| A score is trusted too much | Each score shows the signs behind it. The page says the model was trained on made-up data. |
| Too many requests at once | Limits are 128 KB per request, 20,000 characters per input, and 25 links per batch. Lookups and model comparisons also have limits. |
| Link text runs a script | The page escapes link text before showing it and uses a same-origin Content Security Policy. |

## How the app stays safer

- Each API route checks the input type, size, and allowed range. Errors use JSON.
- Each reply has security headers. API replies use Cache-Control: no-store so the browser does not save them.
- Logs include a request ID, but not the request contents.
- A server error shows a general message. The full error stays in the server log.
- Program calls use fixed arguments, do not use a shell, and have time limits.
- The Docker app does not run as the root user. CI runs the tests after each push.

## Limits

This project has not had an outside security review. It has no sign in because it is for one person on one computer. See the README for other limits.
