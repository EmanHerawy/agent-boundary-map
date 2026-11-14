# Why these questions are here

The Agent Boundary Map asks 66 questions about how your AI agent is set up. None of them is hypothetical. Each one is there because something went wrong, or was shown to go wrong, in a real AI system: a product used by real people, an attack researchers demonstrated, or a risk a security standard names.

This page lists that evidence for every question, with links so you can check it yourself. They all follow one rule: **the model may propose, but something outside the model must authorize.**

## How to read this

Each source is labeled by what kind of evidence it is:

| Label | What it means |
|---|---|
| **Real incident** | It happened to real users or organizations. |
| **Demonstrated attack** | Researchers made the attack work against a real product. The vendor usually fixed it afterwards. It shows the attack works, not that anyone used it. |
| **Research** | A peer-reviewed paper or a published proof of concept. |
| **Standard** | A security standard, a specification or vendor guidance that names the risk or the control. |
| **Background** | Related evidence that explains why the control matters, but doesn't show this exact risk. |

> **What this evidence proves, and what it doesn't**
>
> A paper that demonstrates an attack doesn't mean every agent is vulnerable. A documented incident shows that one particular system or configuration failed. It doesn't prove every system will fail the same way.
>
> The map uses these examples to show that each attack surface is real and worth examining. What matters is how *your* system handles it, and that's what the questions ask.

**58 of the 66 questions have direct public evidence. The other 8 rest on established security principles, with related background.** We mark those clearly and list them [at the end](#questions-with-no-direct-public-case-yet). We'd rather show a gap than stretch a source to fill it.

Want the mapping at a glance? The [evidence register](evidence.md) has every question and source in one table per step, with exact quotes from each source.

## Seen in the wild

If you only read one section, read this one. These are real incidents, not lab demonstrations:

- **An AI agent deleted a production database.** During a code freeze, Replit's agent deleted a company's production database, then said it couldn't be recovered. The founder recovered it himself. [Gizmodo, Jul 2025](https://gizmodo.com/replits-ai-agent-wipes-companys-codebase-during-vibecoding-session-2000633176). See A4 and O4.
- **Stolen integration tokens kept working for days.** Compromised tokens from the Salesloft Drift integration pulled data from Salesforce instances from Aug 8 to at least Aug 18, 2025, until they were revoked on Aug 20. [Google Threat Intelligence](https://cloud.google.com/blog/topics/threat-intelligence/data-theft-salesforce-instances-via-salesloft-drift). See T5 and O3.
- **A trusted MCP server turned malicious through an update.** After 15 normal releases, version 1.0.16 of the `postmark-mcp` npm package began secretly BCC-ing every email to an outside server. [The Register, Sep 2025](https://www.theregister.com/2025/09/29/postmark_mcp_server_code_hijacked/). See P3.
- **Malware used developers' own AI tools to steal secrets.** Malicious versions of the Nx build package ran AI command-line tools already on the machine, with their permission-bypass flags, to find and steal files and secrets. [Wiz, Aug 2025](https://www.wiz.io/blog/s1ngularity-supply-chain-attack). See X4 and O8.
- **Hundreds of malicious skills in an agent marketplace.** Koi Security found 341 malicious skills on ClawHub, OpenClaw's skill marketplace. Some hid a fake "prerequisite" telling the agent to download and run a payload. [Palo Alto Networks Unit 42, Jun 2026](https://unit42.paloaltonetworks.com/openclaw-ai-supply-chain-risk/). See K2 and K3.
- **An AI integration exposed data across customers.** A bug in Asana's MCP server could let users see other organizations' data. The server was offline June 5–17, 2025. [The Register](https://www.theregister.com/2025/06/18/asana_mcp_server_bug/). See U3.
- **Source code sent to a chatbot.** A Samsung engineer uploaded internal source code to ChatGPT. Samsung then banned generative AI tools at work. [Forbes, May 2023](https://www.forbes.com.au/news/innovation/samsung-bans-chatgpt-among-employees-after-sensitive-code-leak/). See O6.
- **Malicious code shipped inside an AI coding extension.** Code committed to the Amazon Q Developer extension's repo shipped in a normal release, version 1.84.0. A syntax error stopped it from running. [AWS security bulletin, Jul 2025](https://aws.amazon.com/security/security-bulletins/AWS-2025-015/). See O8.

The rest of this page goes question by question, in the order the map asks them.

---

## Instructions

### I2 · Rules read-only
> Are these files read-only to the agent at the operating-system level?

- **Demonstrated attack:** [GitHub Copilot, CVE-2025-53773](https://embracethered.com/blog/posts/2025/github-copilot-remote-code-execution-via-prompt-injection/) (Embrace The Red, Aug 2025). Injected instructions made Copilot edit the project's `settings.json` to auto-approve its own tools, then run shell commands. It was fixed in Aug 2025. If an agent can write its own settings, injected text can switch off its safeguards.

### I3 · Overriding instructions
> Untrusted text can try to override your instructions, either typed by a user (direct injection) or hidden in content the agent reads (indirect injection). What keeps it from overriding them?

- **Research:** [Greshake et al., *Not what you've signed up for*](https://arxiv.org/abs/2302.12173) (2023). This paper introduced indirect prompt injection: instructions planted in data an AI app later reads. Content the agent reads can carry instructions that compete with yours.
- **Research:** [Beurer-Kellner et al., *Design Patterns for Securing LLM Agents*](https://arxiv.org/abs/2506.08837) (2025). It describes agent designs with provable resistance to prompt injection, which shows what a protection outside the model can look like.

### I5 · Folder files changing setup
> What stops files you didn't review from changing the agent's instructions or settings?

- **Real incident:** [Instruction-file poisoning](https://labs.cloudsecurityalliance.org/research/csa-research-note-agent-instruction-file-poisoning-20261027/) (Cloud Security Alliance, Oct 2026). A compromised contributor account committed agent files that run a credential stealer when the repo is opened in an AI tool.
- **Demonstrated attack:** [Claude Code project files, CVE-2025-59536](https://research.checkpoint.com/2026/rce-and-api-token-exfiltration-through-claude-code-project-files/) (Check Point, Feb 2026). Hooks and MCP servers defined in a cloned repo ran when the project was opened, with no prompt. It was fixed.
- **Demonstrated attack:** [Codex CLI, CVE-2025-61260](https://research.checkpoint.com/2025/openai-codex-cli-command-injection-vulnerability/) (Check Point, Dec 2025). Config files inside a project made Codex run an attacker's command at startup, with no approval. It was fixed in 0.23.0.
- **Demonstrated attack:** [Rules File Backdoor](https://pillar.security/blog/new-vulnerability-in-github-copilot-and-cursor-how-hackers-can-weaponize-code-agents) (Pillar Security, Mar 2025). Invisible Unicode characters in Cursor and Copilot rules files hid instructions from people, even during pull-request review. A review only protects you if it can see what the agent will read.

### I6 · Leaked instructions
> If someone got the agent to repeat its instructions, would that help them?

- **Real incident:** [Bing Chat spills its secrets](https://arstechnica.com/information-technology/2023/02/ai-powered-bing-chat-spills-its-secrets-via-prompt-injection-attack/) (Ars Technica, Feb 2023). A prompt injection made Bing Chat reveal its hidden instructions, including its codename, Sydney.
- **Standard:** [OWASP LLM07:2025 System Prompt Leakage](https://genai.owasp.org/llmrisk/llm072025-system-prompt-leakage/). A system prompt isn't secret. Keep credentials out of it, and don't rely on it as a security control.

## Outside content

### C1 · Off-task requests
> Can content the agent reads get it to do something its job doesn't need?

- **Demonstrated attack:** [*Invitation Is All You Need*](https://www.safebreach.com/blog/invitation-is-all-you-need-hacking-gemini/) (SafeBreach, Aug 2025). Instructions hidden in a calendar invite made Gemini delete events and control home appliances. Nothing in the user's task needed either action.

### C2 · Data leaving
> What stops data the agent can reach from leaving to a place it shouldn't?

- **Demonstrated attack:** [Microsoft 365 Copilot, CVE-2025-32711 ("EchoLeak")](https://www.cve.org/CVERecord?id=CVE-2025-32711) (Microsoft, Jun 2025). Microsoft's description: "AI command injection in M365 Copilot allows an unauthorized attacker to disclose information over a network."
- **Demonstrated attack:** [Data exfiltration from Slack AI](https://promptarmor.substack.com/p/data-exfiltration-from-slack-ai-via) (PromptArmor, Aug 2024). A message in a public channel made Slack AI leak data from private channels the attacker wasn't in.
- **Research:** [The lethal trifecta](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/) (Simon Willison, Jun 2025). An agent that has private data, reads untrusted content and has a way to send data out can be made to leak that data. Of the three, the way out is often the easiest to control.
- **Research:** [The AI agent lethal trifecta](https://labs.cloudsecurityalliance.org/research/csa-research-note-ai-agent-lethal-trifecta-capability-securi/) (Cloud Security Alliance, Jun 2026). The same model, described by a standards body.

## Memory

### M1 · What gets into memory
> What can end up in the agent's memory?

- **Demonstrated attack:** [SpAIware](https://embracethered.com/blog/posts/2024/chatgpt-macos-app-persistent-data-exfiltration/) (Embrace The Red, Sep 2024). A web page wrote instructions into ChatGPT's long-term memory, and they leaked the user's future chats. It was fixed in Sep 2024. What an agent reads can end up in memory and outlive the session.
- **Demonstrated attack:** [Hacking Gemini's memory](https://embracethered.com/blog/posts/2025/gemini-memory-persistence-prompt-injection/) (Embrace The Red, Feb 2025). A document tricked Gemini into saving false long-term memories, despite its tool protections.

### M2 · Changing memory
> Can the agent change or delete what's already in memory?

- **Research:** [*Hidden in Memory*](https://arxiv.org/abs/2605.15338) (Pulipaka et al., May 2026). Adversarial content corrupted what an assistant remembered and steered its later interactions. If what the agent reads can rewrite memory, it can change future behavior.

### M3 · Memory per project
> Is memory kept separate per project, client or task?

- **Standard:** [OWASP Top 10 for Agentic Applications 2026, ASI06](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) (OWASP, Dec 2025). It recommends "memory segmentation: isolate user sessions and domain contexts to prevent knowledge and sensitive data leakage."

### M4 · Sensitive data in memory
> Can sensitive data end up saved in memory?

- **Standard:** [OWASP Top 10 for Agentic Applications 2026, ASI06](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) (OWASP, Dec 2025). It recommends scanning memory writes "for malicious or sensitive content before commit", and keeping data for less time the more sensitive it is.

## Knowledge sources

### N1 · Retrieval per user
> How is retrieval limited to the documents and search results the user is authorized to access?

- **Standard:** [Copilot data foundation guidance](https://learn.microsoft.com/en-us/sharepoint/sharepoint-copilot-best-practices) (Microsoft). Copilot answers from everything a user already has access to, so Microsoft tells admins to fix oversharing first. Retrieval inherits any access that's too broad.

### N2 · Adding to the index
> Who or what can add content the agent will later retrieve?

- **Demonstrated attack:** [Slack AI](https://promptarmor.substack.com/p/data-exfiltration-from-slack-ai-via) (PromptArmor, Aug 2024). An attacker's public message was pulled into answers for other users. Anyone who could post was, in effect, adding to the index.
- **Research:** [PoisonedRAG](https://arxiv.org/abs/2402.07867) (USENIX Security 2025). A few planted texts in a knowledge base made the model give the attacker's chosen answer.
- **Research:** [AgentPoison](https://arxiv.org/abs/2407.12784) (NeurIPS 2024). Poisoning under 0.1% of an agent's memory or knowledge base gave an average attack success rate of 80% or more.

## Users

### U1 · Caller identity
> How is the identity of whoever sends the agent a request established?

- **Standard:** [OWASP API2:2023 Broken Authentication](https://owasp.org/API-Security/editions/2023/en/0xa2-broken-authentication/). Authentication is exposed to everyone, which makes it an easy target. Identity has to come from a trusted mechanism, not from what the request says.

### U2 · User's access
> When the agent acts for a user, how is that user's access checked?

- **Standard:** [MCP Security Best Practices](https://modelcontextprotocol.io/specification/2025-11-25/basic/security_best_practices) (MCP specification). MCP servers that call third-party APIs on users' behalf can be exploited as "confused deputies". A server acting for many users has to check each user's own access.

### U3 · Data crossing users
> Can one user's data show up in another user's session?

- **Real incident:** [Asana MCP server bug](https://www.theregister.com/2025/06/18/asana_mcp_server_bug/) (The Register, Jun 2025). A bug could let users see other organizations' data. The server was offline June 5–17.
- **Real incident:** [ChatGPT redis-py bug](https://www.engadget.com/openai-says-a-bug-leaked-sensitive-chatgpt-user-data-165439848.html) (Engadget, Mar 2023). Some users saw other users' chat titles, and the payment details of 1.2% of ChatGPT Plus subscribers may have been exposed. A shared component mixed users' data. (OpenAI's own post blocks automated access, so we link to a report of it.)

### U4 · Steering another user
> Can one user put something into shared state that another user's session later acts on?

- **Demonstrated attack:** [Slack AI](https://promptarmor.substack.com/p/data-exfiltration-from-slack-ai-via) (PromptArmor, Aug 2024). One user's public message steered the answers another user received.

### U5 · Who sees the reply
> Can people who aren't allowed to see the data end up seeing the agent's reply?

- **Real incident:** [AI meeting assistants leak confidential business conversations](https://oecd.ai/en/incidents/2024-10-02-8f84) (OECD AI Incidents Monitor, Oct 2024). Otter.ai and Zoom's AI Companion sent sensitive post-meeting discussions to people who weren't meant to see them. (The OECD entry is an AI-generated summary of press reports.)

## Tools

### T1 · Tools changing mid-session
> During a session, can anything add or change the tools, MCP servers or skills available to the agent?

- **Research:** [Poisoned MCP tool descriptions](https://labs.cloudsecurityalliance.org/research/csa-research-note-mcp-tool-description-poisoning-20260711-cs/) (Cloud Security Alliance, Jul 2026). Updating an approved tool's description doesn't trigger a new approval, so a tool can change after you approved it.

### T3 · Who can read credentials
> Who can read the tools' credentials?

- **Demonstrated attack:** [Claude Code project files, CVE-2026-21852](https://research.checkpoint.com/2026/rce-and-api-token-exfiltration-through-claude-code-project-files/) (Check Point, Feb 2026). A repo's settings could send the user's API key to an attacker's server. It was fixed before publication. Anything that can redirect or read a credential can leak it.

### T4 · Credential scope
> What can each credential reach, and what can it do there?

- **Demonstrated attack:** [GitHub MCP exploit](https://tessl.io/blog/malicious-github-issue-ai-agent-leak/) (Invariant Labs research, reported by Tessl, Jun 2025). A malicious public issue made an agent copy data from a private repo into a public pull request. The agent's token could reach far more than its task needed.

### T5 · Credential lifetime
> How long does each credential stay valid?

- **Real incident:** [Salesloft Drift token theft](https://cloud.google.com/blog/topics/threat-intelligence/data-theft-salesforce-instances-via-salesloft-drift) (Google Threat Intelligence, Aug 2025). Stolen tokens pulled Salesforce data from Aug 8 to at least Aug 18, until they were revoked on Aug 20. The longer a credential stays valid, the longer a thief can use it.

### T6 · Trusting tool results
> When a tool's result leads to an action that matters, is it checked against a source the tool can't influence?

- **Research:** [AgentDojo](https://arxiv.org/abs/2406.13352) (Debenedetti et al., 2024). Data returned by external tools hijacked agents into carrying out malicious tasks.
- **Research:** [InjecAgent](https://arxiv.org/abs/2403.02691) (Zhan et al., ACL Findings 2024). Outside content reaching a tool-using agent hijacked a GPT-4 agent 24% of the time. A tool's result is untrusted input, however it's formatted.

### T7 · Tool arguments
> Do the tools you built treat the model's arguments as untrusted input?

- **Demonstrated attack:** [SQL injection in the SQLite MCP server](https://www.trendmicro.com/en/research/25/f/why-a-classic-mcp-server-vulnerability-can-undermine-your-entire-ai-agent.html) (Trend Micro, Jun 2025). Anthropic's reference server put unsanitized input into SQL. The server is archived and unpatched, and it was forked more than 5,000 times. Arguments the model supplies reach your code like any other user input.

## MCP servers

### P2 · Unapproved servers
> Can an MCP server you didn't approve be connected to the agent?

- **Demonstrated attack:** [Codex CLI, CVE-2025-61260](https://research.checkpoint.com/2025/openai-codex-cli-command-injection-vulnerability/) (Check Point, Dec 2025). An MCP server declared in a repo's config ran at startup, with no approval.

### P3 · Servers changing
> What makes sure a third-party MCP server still runs the version you approved?

- **Real incident:** [postmark-mcp backdoor](https://www.theregister.com/2025/09/29/postmark_mcp_server_code_hijacked/) (The Register, Sep 2025). After 15 releases, version 1.0.16 of an npm MCP server began secretly BCC-ing emails to an outside server.
- **Demonstrated attack:** [MCPoison, CVE-2025-54136](https://research.checkpoint.com/2025/cursor-vulnerability-mcpoison/) (Check Point, Aug 2025). In Cursor, an approved server's command could be changed and still run, with no new prompt. It was fixed in Cursor 1.3.

### P4 · Server review
> Before a third-party server is enabled or updated, what gets reviewed?

- **Research:** [Poisoned MCP tool descriptions](https://labs.cloudsecurityalliance.org/research/csa-research-note-mcp-tool-description-poisoning-20260711-cs/) (Cloud Security Alliance, Jul 2026). Hidden text in a tool's description gives the agent instructions the user never sees. Invariant Labs first described this in Apr 2025. A review has to cover descriptions and instructions, not just code.

### P5 · Your servers' callers
> How do the servers you built check who is calling them?

- **Demonstrated attack:** [MCP Inspector, CVE-2025-49596](https://www.oligo.security/blog/critical-rce-vulnerability-in-anthropic-mcp-inspector-cve-2025-49596) (Oligo Security, Jun 2025). There was no authentication between client and proxy, so a website the developer visited could run code on their machine.
- **Standard:** [MCP Security Best Practices](https://modelcontextprotocol.io/specification/2025-11-25/basic/security_best_practices) (MCP specification). Local servers can be reached through DNS rebinding, so the spec says to require an authorization token.

### P6 · Downstream credentials
> When servers you built call other APIs, which credentials do they use?

- **Standard:** [MCP Security Best Practices](https://modelcontextprotocol.io/specification/2025-11-25/basic/security_best_practices) (MCP specification). Token passthrough is forbidden: a server must not accept tokens that weren't issued to it.

### P7 · Local server access
> Where do local third-party servers run, and what can they access?

- **Demonstrated attack:** [mcp-remote, CVE-2025-6514](https://jfrog.com/blog/2025-6514-critical-mcp-remote-rce-vulnerability/) (JFrog, Jul 2025). Connecting to a malicious server could run OS commands on the user's machine (severity 9.6 of 10). Local MCP components run with your machine's access.
- **Demonstrated attack:** [EscapeRoute, CVE-2025-53109 and CVE-2025-53110](https://cymulate.com/blog/cve-2025-53109-53110-escaperoute-anthropic/) (Cymulate, 2025). Symlink and path-prefix flaws let Anthropic's Filesystem MCP server reach files outside its allowed folders. They were fixed. A server's own limits aren't a sandbox.

## Skills, plugins and hooks

### K2 · Unapproved items
> Can a skill, plugin or hook you didn't approve be added to the agent?

- **Real incident:** [OpenClaw's skill marketplace and the AI supply chain](https://unit42.paloaltonetworks.com/openclaw-ai-supply-chain-risk/) (Palo Alto Networks Unit 42, Jun 2026). Koi Security's "ClawHavoc" disclosure found 341 malicious skills on ClawHub, OpenClaw's skill marketplace. Unvetted marketplace items reached agents.
- **Background:** [Malicious npm packages abuse dependency confusion](https://www.microsoft.com/en-us/security/blog/2026/05/29/33-malicious-npm-packages-abuse-dependency-confusion-profile-developer-environments/) (Microsoft, May 2026). These were packages, not skills. Their code ran as soon as `npm install` ran, and it collected environment variables. An agent that installs packages carries the same risk.

### K3 · Item review
> Before a third-party skill, plugin or hook is enabled or updated, what gets reviewed?

- **Real incident:** [The same Unit 42 report](https://unit42.paloaltonetworks.com/openclaw-ai-supply-chain-risk/). Skills hid a fake "prerequisite" telling the agent to decode and run a remote payload. Unit 42 recommends a line-by-line audit. A review has to cover setup instructions, not just code.
- **Background:** [The same Microsoft report](https://www.microsoft.com/en-us/security/blog/2026/05/29/33-malicious-npm-packages-abuse-dependency-confusion-profile-developer-environments/). The code ran at install time, before anyone reviewed what it did. A review has to happen before anything runs.

### K4 · Items changing
> Can a skill or plugin pull in new content, or change, after it was reviewed?

*No direct public case yet. Background:*

- **Background:** [postmark-mcp backdoor](https://www.theregister.com/2025/09/29/postmark_mcp_server_code_hijacked/) (The Register, Sep 2025). After 15 releases, an update to an npm MCP server added a hidden backdoor. This was an MCP server, not a skill or plugin, but any item that updates after review could change the same way.

### K5 · Items granting permissions
> Can a skill or plugin bypass or weaken the agent's approval and authorization checks?

- **Research:** [What's the "Matter" with Skills?](https://www.hiddenlayer.com/research/whats-the-matter-with-skills) (HiddenLayer, Jul 2026). A skill's `allowed-tools` frontmatter could pre-authorize tool use in Claude Code. An item can bring its own permissions.
- **Background:** [Claude Code issue #67198](https://github.com/anthropics/claude-code/issues/67198) (Jun 2026). A skill's permission grants applied when the user invoked it, but not when the model did. How permissions behave can depend on the path, so check each one.

### K6 · Parsing skill files
> How does your code read the metadata in skill files?

- **Demonstrated attack:** [PyYAML, CVE-2017-18342](https://www.cve.org/CVERecord?id=CVE-2017-18342) (2018). Before version 5.1, `yaml.load()` could run arbitrary code from untrusted input. This isn't specific to agents, but skill metadata is often YAML, and an unsafe loader turns a skill file into code.

### K7 · Where items are active
> Is each skill or plugin active only where it's needed, or everywhere?

*No direct public case yet. Background:*

- **Background:** [OWASP Agentic Top 10, ASI02](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) (OWASP, Dec 2025). Under "Least Agency and Least Privilege for Tools", it says to limit each tool's functions, permissions and data to what the task needs. That's the related principle. It's about how tool permissions are scoped, not where an item is active.

## Code execution

### X1 · Where code runs
> Where does code run: commands the agent runs, scripts from skills, and hooks?

- **Demonstrated attack:** [Securing CI/CD in an agentic world: Claude Code GitHub Action case](https://www.microsoft.com/en-us/security/blog/2026/06/05/securing-ci-cd-in-agentic-world-claude-code-github-action-case/) (Microsoft, Jun 2026). In a lab test, injected text in a GitHub issue led Claude Code's GitHub Action to read the runner's environment and expose its API key. It was fixed in 2.1.128. The agent's tools could reach everything the runner held.
- **Background:** [Malicious npm packages](https://www.microsoft.com/en-us/security/blog/2026/05/29/33-malicious-npm-packages-abuse-dependency-confusion-profile-developer-environments/) (Microsoft, May 2026). Untrusted code ran on developer machines at install time and collected environment variables. Code runs with the access of wherever it runs.

### X2 · Network reach
> What network destinations can executed code reach?

- **Demonstrated attack:** [Claude Code DNS exfiltration, CVE-2025-55284](https://embracethered.com/blog/posts/2025/claude-code-exfiltration-via-dns-requests/) (Embrace The Red, Aug 2025). Injected instructions made Claude Code read `.env` and leak it through DNS lookups. It was fixed in v1.0.4. DNS counts as network reach.

### X3 · Installing code
> What controls which packages or downloaded code the agent can install or run?

- **Research:** [*We Have a Package for You!*](https://arxiv.org/abs/2406.10279) (USENIX Security 2025). Code models suggest packages that don't exist (the researchers found 205,474 unique made-up names). Attackers can register those names. An agent that installs whatever a model suggests can install an attacker's package.

### X4 · Machine secrets
> Can executed code read secrets that live on the machine?

- **Real incident:** [s1ngularity supply-chain attack](https://www.wiz.io/blog/s1ngularity-supply-chain-attack) (Wiz, Aug 2025). Malicious Nx versions ran the machine's AI command-line tools with permission-bypass flags to steal files and secrets.
- **Demonstrated attack:** [Securing CI/CD in an agentic world](https://www.microsoft.com/en-us/security/blog/2026/06/05/securing-ci-cd-in-agentic-world-claude-code-github-action-case/) (Microsoft, Jun 2026). The agent's Read tool worked "with full access to the process's environment variables", including the workflow's API key. Environment variables are machine secrets too.

### X5 · Escaping the sandbox
> Can executed code get out of its execution environment?

- **Demonstrated attack:** [EscapeRoute](https://cymulate.com/blog/cve-2025-53109-53110-escaperoute-anthropic/) (Cymulate, 2025). Two flaws let attackers escape the Filesystem MCP server's sandbox. They were fixed. A boundary the tool enforces on itself can be bypassed.

### X6 · Pre-approved commands
> Can commands that skip approval run other code or send data out?

- **Demonstrated attack:** [CVE-2025-55284](https://embracethered.com/blog/posts/2025/claude-code-exfiltration-via-dns-requests/) (Embrace The Red, Aug 2025). `ping`, `nslookup`, `host` and `dig` ran without approval, and they carried the data out. It was fixed in v1.0.4. "Harmless" pre-approved commands were enough to leak data.

### X7 · Fresh environment
> Does the execution environment start fresh for each task, or carry over?

*No direct public case yet. Background:*

- **Background:** [Securing CI/CD in an agentic world](https://www.microsoft.com/en-us/security/blog/2026/06/05/securing-ci-cd-in-agentic-world-claude-code-github-action-case/) (Microsoft, Jun 2026). The runner was a fresh, short-lived VM, yet the agent could still read that run's secrets. This shows a fresh environment doesn't protect you *within* a run. It doesn't show anything carrying over between tasks, or that fresh environments prevent that.

## Browser

### W1 · What the browser carries
> What does the browser carry with it: which accounts, saved passwords and saved payment details?

- **Research:** [*Scamlexity*](https://guard.io/labs/scamlexity-we-put-agentic-ai-browsers-to-the-test-they-clicked-they-paid-they-failed) (Guardio Labs, Aug 2025). In tests, an AI browser filled in the user's saved address and card on a fake shop. Saved payment details became the agent's to spend.

### W2 · Browser actions
> Before the browser does something that matters, what has to happen?

- **Demonstrated attack:** [Indirect prompt injection in Perplexity Comet](https://brave.com/blog/comet-prompt-injection/) (Brave, Aug 2025). A hidden Reddit comment made Comet send the user's email address and one-time code to the attacker. The browser acted with the user's logged-in sessions, and nothing checked it.

### W3 · Browser control channel
> Who else can control the agent's browser?

- **Standard:** [Changes to remote debugging switches](https://developer.chrome.com/blog/remote-debugging-port) (Chrome for Developers, Mar 2025). Attackers used Chrome's remote debugging to extract cookies, so Chrome 136 blocked it on the default profile. The control channel itself is a target.
- **Research:** [CDP session hijacking](https://labs.cloudsecurityalliance.org/research/csa-research-note-chrome-devtools-session-hijacking-20260817/) (Cloud Security Alliance, Aug 2026). Code already running on the machine can take over logged-in browser sessions through the debugging protocol. Anything that reaches the channel gets the sessions.

## Actions

### A1 · Review before use
> What must happen before the agent's code or file changes are used (merged, deployed, or relied on by others)?

- **Demonstrated attack:** [Rules File Backdoor](https://pillar.security/blog/new-vulnerability-in-github-copilot-and-cursor-how-hackers-can-weaponize-code-agents) (Pillar Security, Mar 2025). Poisoned rules made coding assistants write code with backdoors, hidden even in pull-request review. Changes an agent writes need a review that can see what they do.
- **Background:** [Amazon Q Developer extension, AWS-2025-015](https://aws.amazon.com/security/security-bulletins/AWS-2025-015/) (AWS, Jul 2025). Malicious code committed to the repo shipped automatically in version 1.84.0. A syntax error stopped it from running. Unreviewed changes reached users, though this change came from a person, not an agent.

### A2 · Files that run automatically
> Can the agent change files that run automatically, or that control its own environment?

- **Demonstrated attack:** [GitHub Copilot, CVE-2025-53773](https://embracethered.com/blog/posts/2025/github-copilot-remote-code-execution-via-prompt-injection/) (Embrace The Red, Aug 2025). Copilot rewrote its own settings file to approve its own actions. Files that control the agent's environment are a target.

### A3 · Authorizing each request
> When the agent changes something in an outside system, what decides whether that specific request is allowed?

- **Demonstrated attack:** [*Invitation Is All You Need*](https://www.safebreach.com/blog/invitation-is-all-you-need-hacking-gemini/) (SafeBreach, Aug 2025). Gemini deleted calendar events and operated connected devices on instructions hidden in an invite. Nothing outside the model checked each request.

### A4 · Final decision
> Before an action that matters and is hard to undo, who makes the final decision?

- **Real incident:** [Replit agent deletes a production database](https://gizmodo.com/replits-ai-agent-wipes-companys-codebase-during-vibecoding-session-2000633176) (Gizmodo, Jul 2025). During a code freeze, Replit's agent deleted a company's production database. A hard-to-undo action went ahead without a person deciding.

### A5 · Retries
> If an action times out or fails partway and is retried, could it happen twice?

- **Standard:** [Idempotent requests](https://docs.stripe.com/api/idempotent_requests) (Stripe API documentation). An idempotency key lets a request be retried "without accidentally performing the same operation twice". It's the standard way to make retries safe.

### A6 · Cumulative limits
> What limits how much the agent can do in one task or session?

- **Standard:** [OWASP LLM10:2025 Unbounded Consumption](https://genai.owasp.org/llmrisk/llm102025-unbounded-consumption/). Uncontrolled use leads to denial of service and "denial of wallet", so OWASP recommends rate limits and quotas. They limit the total, not just each action.

### A7 · Scheduled actions
> Can the agent schedule actions or tasks to run later, and what happens when they run?

*No direct public case yet. Background:*

- **Background:** [OWASP LLM06:2025 Excessive Agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/). It recommends approval for high-impact actions and limited permissions. That's the relevant principle, but it doesn't cover actions that run later.

### A8 · Agreements on your behalf
> Can the agent accept terms, licenses or agreements on your organization's behalf?

*No direct public case yet. Background:*

- **Background:** [Moffatt v. Air Canada, 2024 BCCRT 149](https://www.canlii.org/en/bc/bccrt/doc/2024/2024bccrt149/2024bccrt149.pdf) (BC Civil Resolution Tribunal, Feb 2024). Air Canada's chatbot gave a customer wrong fare information, and the tribunal held the airline responsible for it. The agent didn't accept an agreement here, but the organization answered for what its AI said.
- **Background:** [UNCITRAL Model Law on Automated Contracting](https://uncitral.un.org/en/mlac) (United Nations, Jul 2024). A legal framework for contracts formed with automation and AI, including rules for attributing what automated systems output. It's legal context, not the technical control this question asks about.
- **Background:** [OWASP LLM06:2025 Excessive Agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/). It covers high-impact actions taken without independent approval, but not agreements specifically.

## Other agents

### G1 · Requests from agents
> When another agent sends this one a request, what's checked?

- **Research:** [Agent session smuggling](https://unit42.paloaltonetworks.com/agent-session-smuggling-in-agent2agent-systems/) (Palo Alto Networks Unit 42, Oct 2025). A malicious remote agent slipped extra instructions into an agent-to-agent session. This is a proof of concept and hasn't been seen in the wild. A request from another agent can carry instructions.

### G2 · Authority handed on
> When this agent hands work to another agent or a sub-agent, what keeps the receiver within the task it was given?

- **Research:** [*Multi-Agent Systems Execute Arbitrary Malicious Code*](https://arxiv.org/abs/2503.12188) (Triedman et al., 2025). Malicious content hijacked AutoGen, CrewAI and MetaGPT into running arbitrary code, even when the individual agents refused. Authority passed between agents can be used by whatever steers them.

### G3 · Rules on delegated work
> Are your critical constraints on delegated work enforced even if the receiver never gets or follows your instructions?

- **Standard:** [OWASP Agentic Top 10, ASI03](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) (OWASP, Dec 2025). It names "un-scoped privilege inheritance": a manager agent delegates work without limiting privileges and passes on its full access. Constraints have to follow the work, not stay with the agent that delegated it.

### G4 · Sub-agent results
> When a sub-agent returns results, how are those results treated?

- **Research:** [The same paper](https://arxiv.org/abs/2503.12188) (Triedman et al., 2025). The attack travels through what agents pass to each other and steers which agent runs next. A sub-agent's output is untrusted input.

## Oversight

### O1 · Action records
> Can you reconstruct what the agent did from records it can't change?

- **Research:** [*LLM Agents Can Easily Tamper With Their Own Traces*](https://arxiv.org/abs/2609.30266) (Qin et al., Sep 2026). Of the local harnesses tested, Claude Code, Codex and all but one other let agents delete their own traces when asked. Attackers could trigger it, and it also happened on its own when agents pursued rewards. The authors advise logging through a mechanism outside the agent's control.
- **Standard:** [OWASP AI Exchange: Monitor use](https://owaspai.org/goto/monitoruse/). Log tool calls with their arguments and the identity that made them, and keep the agent's audit trail "in tamper-evident storage the agent cannot modify".
- **Standard:** [OWASP AI Agent Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html). "Log all agent decisions, tool calls, and outcomes", and keep audit trails for forensics.

### O2 · Stopping it
> Can a person stop the agent at any moment, including all work it has started?

*No direct public case yet. Background:*

- **Background:** [NIST SP 800-61 Rev. 3](https://csrc.nist.gov/pubs/sp/800/61/r3/final) (NIST, Apr 2025). The US incident-response standard covers detection, response and recovery. It establishes the need to respond, but not a specific way to stop an agent.

### O3 · Revoking access
> Can you cut off the agent's access right now, without changing its code?

- **Real incident:** [Salesloft Drift token theft](https://cloud.google.com/blog/topics/threat-intelligence/data-theft-salesforce-instances-via-salesloft-drift) (Google Threat Intelligence, Aug 2025). Stolen tokens kept working from Aug 8 to at least Aug 18. All of them were revoked on Aug 20. Revoking them ended the access. Until then, it continued.

### O4 · Undoing effects
> If the agent does something wrong, can you undo it?

- **Real incident:** [Replit](https://gizmodo.com/replits-ai-agent-wipes-companys-codebase-during-vibecoding-session-2000633176) (Gizmodo, Jul 2025). The agent said the database it deleted couldn't be recovered. The founder recovered it himself. Recovery depended on a mechanism outside the agent, not on what the agent reported.

### O5 · Memory provenance
> Can you see what's in memory, and where each entry came from?

*No direct public case yet. Background:*

- **Background:** [*Hidden in Memory*](https://arxiv.org/abs/2605.15338) (Pulipaka et al., May 2026). Poisoned memories were written from documents, web pages and repositories the agent read. This shows why an entry's source matters, but it doesn't test controls that track sources.

### O6 · Data sent to providers
> Is what reaches the model provider limited to what its terms allow?

- **Real incident:** [Samsung bans ChatGPT](https://www.forbes.com.au/news/innovation/samsung-bans-chatgpt-among-employees-after-sensitive-code-leak/) (Forbes, May 2023). An engineer uploaded internal source code to ChatGPT, and Samsung then banned generative AI tools at work. Data sent to a model provider leaves your control.

### O7 · Model changes
> Can the model the agent uses change without your review?

- **Research:** [*How is ChatGPT's behavior changing over time?*](https://arxiv.org/abs/2307.09009) (Chen, Zaharia, Zou, 2023). GPT-4 and GPT-3.5 behaved substantially differently between their March and June 2023 versions. The same model name can behave differently next month.

### O8 · Software changes
> Can the software that makes up the agent change without your review?

- **Real incident:** [Amazon Q Developer extension, AWS-2025-015](https://aws.amazon.com/security/security-bulletins/AWS-2025-015/) (AWS, Jul 2025). Malicious code reached users inside a normal extension release.
- **Real incident:** [s1ngularity](https://www.wiz.io/blog/s1ngularity-supply-chain-attack) (Wiz, Aug 2025). Malicious versions of a widely used build package were published to npm. An update can change your agent's software without your review, directly or through a dependency.

### O9 · Alerting
> Does suspicious activity alert someone who can act on it?

*No direct public case yet. Background:*

- **Background:** [NIST SP 800-61 Rev. 3](https://csrc.nist.gov/pubs/sp/800/61/r3/final) (NIST, Apr 2025). The US incident-response standard treats detection as a core discipline. It doesn't show that alerts are independent of the agent, timely or acted on.

---

## Questions with no direct public case yet

We haven't found a public incident, paper or standard that covers these eight directly. Each one has related background above. They're architectural controls based on established security principles, and they follow the same rule as the rest: something outside the model must authorize.

| Question | Principle it rests on |
|---|---|
| **K4** Items changing | Verify integrity: pin versions and use signed releases |
| **K7** Where items are active | Least privilege |
| **X7** Fresh environment | Rebuild the environment for each task |
| **A7** Scheduled actions | Authorize when the action runs, not only when it's scheduled |
| **A8** Agreements on your behalf | Only someone entitled to commit the organization can authorize it |
| **O2** Stopping it | A fail-safe stop for all running work |
| **O5** Memory provenance | Record where each entry came from |
| **O9** Alerting | Detection and response that don't depend on the agent |

## Check it yourself

Every link on this page was checked on 12 Nov 2026. Where the original page couldn't be opened by automated tools, we link to a report of it and say so.

For each source's exact quote, and our reasons for using or rejecting it, see the full [evidence register](evidence.md).

Know a source for one of the eight questions above, or a better source for any question? [Open an issue](https://github.com/EmanHerawy/agent-boundary-map/issues) with the link.
