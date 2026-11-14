# Security policy

Agent Boundary Map is a static page that runs in your browser. It promises two things, and we treat a break of either as a security issue:

1. **It makes no network requests.** Answers stay in the browser; the page's Content-Security-Policy blocks outgoing requests.
2. **It doesn't run content as code.** What you type (such as the agent's name or evidence notes) is shown as text, never as HTML or script.

## Supported versions

Only the current version is supported: the `main` branch, published at https://emanherawy.github.io/agent-boundary-map/. Copies saved earlier, or the older claude.ai version ("Agent Trust Map"), don't get fixes.

## Reporting a vulnerability

Please report privately, not in a public issue: use **[Report a vulnerability](https://github.com/EmanHerawy/agent-boundary-map/security/advisories/new)** on the repository's Security tab.

Include what you found, the steps to reproduce it, the browser and version, and what an attacker could do with it. You'll get an acknowledgement within 7 days. Once it's fixed, we'll credit you in the advisory unless you'd rather not be named.

## In scope

- A way for the page to send data out, or to load anything from the network.
- Script injection through anything the app reads: the agent's name, evidence notes, or answers saved in the browser's storage.
- A way for an exported PDF or Markdown file to carry something other than the report.
- Tampering risks in the bundled components (fonts, jsPDF).

## Not a vulnerability, but please tell us

- **Wrong or misleading security guidance**: a question, status or recommended action that's inaccurate, or that could lead someone to a weaker setup. Open a normal [issue](https://github.com/EmanHerawy/agent-boundary-map/issues), unless the details themselves would help an attacker; then report privately as above.
- A source in the [evidence docs](docs/evidence.md) that's wrong, broken or overstated.

## Out of scope

- Your agent's own security. The app assesses answers you give; it doesn't connect to or test your agent.
- Issues that need someone who already controls your browser or machine.
- What you choose to do with a downloaded report, such as sharing it.
