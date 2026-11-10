# Security policy

PhishLens is an educational security tool (Design Project II, Semester IV, B.Tech with specialisation in Cyber Security). It is
designed to run on your own machine, on loopback, with bundled or user-supplied local data.

## Supported versions

| Version | Supported |
|---|---|
| 1.1.x (main) | Yes |
| < 1.1 | No |

## Reporting a vulnerability

Please **do not open a public issue** for a security problem. Use GitHub's private
vulnerability reporting instead: open the repository's **Security** tab and choose
**Report a vulnerability**. Include the version or commit, steps to reproduce, and the
impact you observed.

What to expect:

- Acknowledgement within 7 days.
- A fix or mitigation plan within 30 days for confirmed issues.
- Credit in the changelog if you would like it.

Good-faith research on your own local install is welcome. Do not test against systems or
accounts you do not own or are not authorized to assess.

## Threat model

**Assets:** pasted URLs and email bodies, domains submitted for enrichment.

**Trust boundary:** the browser and the Flask process on the same machine. The app is not
designed to be exposed to a network and has no user accounts; binding it to a public
interface is out of scope.

| Threat | Mitigation in this codebase |
|---|---|
| Analyzer used to visit malicious links | Analysis is offline string/feature work; the supplied URL is never fetched or opened. |
| Enrichment abused to probe third parties | WHOIS/DNS/TLS lookups need an explicit ownership/authorization flag, accept only public DNS names (IPs, private and local hosts rejected), and are rate-limited (10/min per client). |
| SSRF via enrichment | IP literals and local names are refused outright. Before the TLS check the name is resolved once; if any answer is not a globally routable address (loopback, private, link-local/metadata) the check is refused, and OpenSSL then connects to the vetted IP so DNS rebinding cannot swap the target. |
| Over-trust in model output | Every score ships with the signals and per-feature contributions behind it, and the UI labels the model as trained on synthetic data. |
| Resource exhaustion | 128 KB request cap, 20,000-char input cap, 25-URL batch cap, rate limits on enrichment and the model comparison. |
| XSS from hostile URLs | All URL text is HTML-escaped before rendering; strict same-origin CSP. |

## Secure-development practices

- Input validation on every API route (type, length and range checks) with JSON error bodies.
- Security headers on every response (see `phishlens/web_security.py`) and `Cache-Control: no-store` on API responses.
- Structured access logs with a request ID; request bodies are never logged.
- Generic 500 responses: stack traces go to the server log, not the client.
- Subprocess calls use argument lists (no shell) and timeouts.
- Container runs as a non-root user; tests run in CI on every push.

## Known limitations

This project has not had an independent security audit. It has no authentication because it
is single-user and loopback-only. See the README's *Limitations* section for functional limits.
