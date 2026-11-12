# Evidence behind the questions

This is the full citation register: every source, with an exact quote and why it was or wasn't used. For a readable walkthrough of the same evidence, grouped with the actual question text, see [Why these questions are here](user-guide-evidence.md).

This page links the Agent Boundary Map's questions to public evidence: real incidents, demonstrated attacks, research and security standards. Most questions have direct evidence. The others rely on established security principles, and the page says which ones and why. Every source is linked, so you can check it yourself.

**How to read it.** A source shows that a risk is real. It doesn't show that your system has the same weakness. Each row says what happened in the cited case, then how it relates to the question.

| Type | Meaning |
|---|---|
| **Incident** | It happened to real users or organizations |
| **Vulnerability** | Researchers demonstrated it in a real product, which was usually then fixed. It shows the attack works, not that anyone used it. |
| **Research** | A paper or a published proof of concept |
| **Guidance** | A standard, a specification or vendor documentation |
| **Background** | Related evidence that explains why the control matters, without showing this exact risk |

Every link was checked on 12 Nov 2026. Where the original page couldn't be opened, the link goes to a report of it, and the row says so. Question IDs match the app.

**58 of 66 questions have direct evidence. The other eight have related background only.** They're listed [at the end](#questions-without-direct-evidence-yet).

## Instructions

| Question | Type | Source | What happened | How it relates |
|---|---|---|---|---|
| **I2** Rules read-only | Vulnerability | [GitHub Copilot, CVE-2025-53773](https://embracethered.com/blog/posts/2025/github-copilot-remote-code-execution-via-prompt-injection/) · Embrace The Red, Aug 2025 | Injected instructions made Copilot edit the project's `settings.json` to auto-approve tools, then run shell commands. Fixed Aug 2025. | If the agent can write its own settings, injected text can turn off its safeguards. |
| **I3** Overriding instructions | Research | [Greshake et al., *Not what you've signed up for*](https://arxiv.org/abs/2302.12173) · 2023 | Introduced indirect prompt injection: instructions planted in data an AI app later reads. | Content the agent reads can carry instructions that compete with yours. |
| | Research | [Beurer-Kellner et al., *Design Patterns for Securing LLM Agents*](https://arxiv.org/abs/2506.08837) · 2025 | Agent designs with provable resistance to prompt injection. | Shows what a protection outside the model can look like. |
| **I5** Folder files changing setup | Vulnerability | [Claude Code project files, CVE-2025-59536](https://research.checkpoint.com/2026/rce-and-api-token-exfiltration-through-claude-code-project-files/) · Check Point, Feb 2026 | Hooks and MCP servers defined in a cloned repo ran when the project was opened, with no prompt. Fixed. | Files that arrive with a project can change what the agent runs. |
| | Vulnerability | [Codex CLI, CVE-2025-61260](https://research.checkpoint.com/2025/openai-codex-cli-command-injection-vulnerability/) · Check Point, Dec 2025 | Project-local config made Codex run an attacker's command at startup, with no approval. Fixed in 0.23.0. | The same route in a different harness. |
| | Vulnerability | [Rules File Backdoor](https://pillar.security/blog/new-vulnerability-in-github-copilot-and-cursor-how-hackers-can-weaponize-code-agents) · Pillar Security, Mar 2025 | Invisible Unicode in Cursor and Copilot rules files hid instructions from people, including in pull-request review. | A review only protects you if it can see what the agent will read. |
| | Incident | [Instruction-file poisoning](https://labs.cloudsecurityalliance.org/research/csa-research-note-agent-instruction-file-poisoning-20261027/) · Cloud Security Alliance, Oct 2026 | A compromised contributor account committed agent files that run a credential stealer when the repo is opened in an AI tool. | The same route, used in a real attack. |
| **I6** Leaked instructions | Guidance | [OWASP LLM07:2025 System Prompt Leakage](https://genai.owasp.org/llmrisk/llm072025-system-prompt-leakage/) | A system prompt isn't secret: keep credentials out of it, and don't use it as a security control. | Assume your instructions can be read. |
| | Incident | [Bing Chat spills its secrets](https://arstechnica.com/information-technology/2023/02/ai-powered-bing-chat-spills-its-secrets-via-prompt-injection-attack/) · Ars Technica, Feb 2023 | A prompt injection made Bing Chat reveal its hidden instructions, including its codename, Sydney. | Hidden instructions in a live product were extracted. |

## Outside content

| Question | Type | Source | What happened | How it relates |
|---|---|---|---|---|
| **C1** Off-task requests | Vulnerability | [*Invitation Is All You Need*](https://www.safebreach.com/blog/invitation-is-all-you-need-hacking-gemini/) · SafeBreach, Aug 2025 | Instructions hidden in a calendar invite made Gemini delete events and control home appliances. | Content the agent read triggered actions its task didn't need. |
| **C2** Data leaving | Vulnerability | [Microsoft 365 Copilot, CVE-2025-32711 ("EchoLeak")](https://www.cve.org/CVERecord?id=CVE-2025-32711) · Microsoft, Jun 2025 | "AI command injection in M365 Copilot allows an unauthorized attacker to disclose information over a network." | Injected content can make an agent send data out. |
| | Vulnerability | [Data exfiltration from Slack AI](https://promptarmor.substack.com/p/data-exfiltration-from-slack-ai-via) · PromptArmor, Aug 2024 | A post in a public channel made Slack AI leak data from private channels the attacker wasn't in. | Data left through what the agent produced. |
| | Research | [The lethal trifecta](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/) · Simon Willison, Jun 2025 | Private data, untrusted content and a way to send data out: an agent with all three can be made to leak the data. | Closing the way out is often the easiest of the three to control. |
| | Research | [The AI agent lethal trifecta](https://labs.cloudsecurityalliance.org/research/csa-research-note-ai-agent-lethal-trifecta-capability-securi/) · Cloud Security Alliance, Jun 2026 | With sensitive data, untrusted content and outbound actions together, injected content can make the agent misuse its access. | The same model, from a standards body. |

## Memory

| Question | Type | Source | What happened | How it relates |
|---|---|---|---|---|
| **M1** What gets into memory | Vulnerability | [SpAIware](https://embracethered.com/blog/posts/2024/chatgpt-macos-app-persistent-data-exfiltration/) · Embrace The Red, Sep 2024 | A web page wrote instructions into ChatGPT's long-term memory that leaked the user's future chats. Fixed Sep 2024. | What the agent reads can end up in memory and outlive the session. |
| | Vulnerability | [Hacking Gemini's memory](https://embracethered.com/blog/posts/2025/gemini-memory-persistence-prompt-injection/) · Embrace The Red, Feb 2025 | A document tricked Gemini into saving false long-term memories, despite its tool protections. | The same, in a second product. |
| **M2** Changing memory | Research | [*Hidden in Memory*](https://arxiv.org/abs/2605.15338) · Pulipaka et al., May 2026 | Adversarial content corrupted what an assistant remembers and steered its later interactions. | If what the agent reads can rewrite memory, it can change future behavior. |
| **M3** Memory per project | Guidance | [OWASP Top 10 for Agentic Applications 2026, ASI06](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) · OWASP, Dec 2025 | "Memory segmentation: isolate user sessions and domain contexts to prevent knowledge and sensitive data leakage." | Recommends this separation directly. |
| **M4** Sensitive data in memory | Guidance | [Same, ASI06](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) | Scan memory writes "for malicious or sensitive content before commit", and minimize retention by data sensitivity. | Recommends this check directly. |

## Knowledge sources

| Question | Type | Source | What happened | How it relates |
|---|---|---|---|---|
| **N1** Retrieval per user | Guidance | [Copilot data foundation guidance](https://learn.microsoft.com/en-us/sharepoint/sharepoint-copilot-best-practices) · Microsoft | Copilot answers from everything a user already has access to, so Microsoft's guidance has admins fix oversharing. | Retrieval inherits any access that's too broad. |
| **N2** Adding to the index | Research | [PoisonedRAG](https://arxiv.org/abs/2402.07867) · USENIX Security 2025 | A few planted texts in a knowledge base made the model give the attacker's chosen answer. | Whoever can add content can steer answers. |
| | Research | [AgentPoison](https://arxiv.org/abs/2407.12784) · NeurIPS 2024 | Poisoning under 0.1% of an agent's memory or knowledge base gave an average attack success of 80% or more. | Very little planted content is enough. |
| | Vulnerability | [Slack AI](https://promptarmor.substack.com/p/data-exfiltration-from-slack-ai-via) · PromptArmor, Aug 2024 | An attacker's public post was pulled into answers for other users. | Anyone who could post was, in effect, adding to the index. |

## Users

| Question | Type | Source | What happened | How it relates |
|---|---|---|---|---|
| **U1** Caller identity | Guidance | [OWASP API2:2023 Broken Authentication](https://owasp.org/API-Security/editions/2023/en/0xa2-broken-authentication/) | Authentication is exposed to everyone and is an easy target. | Identity has to come from a trusted mechanism, not from the request. |
| **U2** User's access | Guidance | [MCP Security Best Practices](https://modelcontextprotocol.io/specification/2025-11-25/basic/security_best_practices) · MCP specification | MCP servers that call third-party APIs on users' behalf can be exploited as "confused deputies". | A server acting for many users must check each user's own access. |
| **U3** Data crossing users | Incident | [Asana MCP server bug](https://www.theregister.com/2025/06/18/asana_mcp_server_bug/) · The Register, Jun 2025 | A bug could let users see other organizations' data. The server was offline June 5–17. | Separation between users failed in a shipped AI feature. |
| | Incident | [ChatGPT redis-py bug](https://www.engadget.com/openai-says-a-bug-leaked-sensitive-chatgpt-user-data-165439848.html) · Engadget, Mar 2023 (OpenAI's post blocks automated access) | Some users saw other users' chat titles. Payment details of 1.2% of Plus subscribers may have been exposed. | A shared component mixed users' data. |
| **U4** Steering another user | Vulnerability | [Slack AI](https://promptarmor.substack.com/p/data-exfiltration-from-slack-ai-via) · PromptArmor, Aug 2024 | One user's public post steered the answers another user received. | Shared content became a way to act on someone else's session. |
| **U5** Who sees the reply | Incident | [AI meeting assistants leak confidential business conversations](https://oecd.ai/en/incidents/2024-10-02-8f84) · OECD AI Incidents Monitor, Oct 2024 (AI-generated summary of press reports) | Otter.ai and Zoom's AI Companion sent sensitive post-meeting discussions to unintended recipients. | The AI's output reached people who weren't meant to see it. |

## Tools

| Question | Type | Source | What happened | How it relates |
|---|---|---|---|---|
| **T1** Tools changing mid-session | Research | [Poisoned MCP tool descriptions](https://labs.cloudsecurityalliance.org/research/csa-research-note-mcp-tool-description-poisoning-20260711-cs/) · Cloud Security Alliance, Jul 2026 | Updating an approved tool's description doesn't trigger a new approval. | A tool can change after you approved it. |
| **T3** Who can read credentials | Vulnerability | [Claude Code project files, CVE-2026-21852](https://research.checkpoint.com/2026/rce-and-api-token-exfiltration-through-claude-code-project-files/) · Check Point, Feb 2026 | A repo's settings could send the user's API key to an attacker's server. Fixed before publication. | Anything that can redirect or read a credential can leak it. |
| **T4** Credential scope | Vulnerability | [GitHub MCP exploit](https://tessl.io/blog/malicious-github-issue-ai-agent-leak/) · Invariant Labs research, reported by Tessl, Jun 2025 | A malicious public issue made an agent copy private-repo data into a public pull request. | The agent's access reached further than its task needed. |
| **T5** Credential lifetime | Incident | [Salesloft Drift token theft](https://cloud.google.com/blog/topics/threat-intelligence/data-theft-salesforce-instances-via-salesloft-drift) · Google Threat Intelligence, Aug 2025 | Compromised tokens from the Drift integration pulled Salesforce data from Aug 8 to at least Aug 18, until revoked Aug 20. | The longer a credential stays valid, the longer a thief can use it. |
| **T6** Trusting tool results | Research | [AgentDojo](https://arxiv.org/abs/2406.13352) · Debenedetti et al., 2024 | Data returned by external tools hijacked agents into carrying out malicious tasks. | A tool's result is untrusted input, however it's formatted. |
| | Research | [InjecAgent](https://arxiv.org/abs/2403.02691) · Zhan et al., ACL Findings 2024 | Outside content reaching a tool-using agent hijacked a ReAct-prompted GPT-4 agent 24% of the time. | The same, measured across many agents. |
| **T7** Tool arguments | Vulnerability | [SQL injection in the SQLite MCP server](https://www.trendmicro.com/en/research/25/f/why-a-classic-mcp-server-vulnerability-can-undermine-your-entire-ai-agent.html) · Trend Micro, Jun 2025 | Anthropic's reference server put unsanitized input into SQL. It's archived, unpatched, and was forked 5,000+ times. | Model-supplied arguments reach your code like any user input. |

## MCP servers

| Question | Type | Source | What happened | How it relates |
|---|---|---|---|---|
| **P2** Unapproved servers | Vulnerability | [Codex CLI, CVE-2025-61260](https://research.checkpoint.com/2025/openai-codex-cli-command-injection-vulnerability/) · Check Point, Dec 2025 | An MCP server declared in a repo's config ran at startup, with no approval. | A server nobody approved was connected. |
| **P3** Servers changing | Vulnerability | [MCPoison, CVE-2025-54136](https://research.checkpoint.com/2025/cursor-vulnerability-mcpoison/) · Check Point, Aug 2025 | Once approved in Cursor, a server's command could be changed and still run, with no new prompt. Fixed in Cursor 1.3. | Approval didn't cover later changes. |
| | Incident | [postmark-mcp backdoor](https://www.theregister.com/2025/09/29/postmark_mcp_server_code_hijacked/) · The Register, Sep 2025 | After 15 releases, version 1.0.16 of an npm MCP server began secretly BCC-ing emails to an outside server. | A trusted server turned malicious through an update. |
| **P4** Server review | Research | [Poisoned MCP tool descriptions](https://labs.cloudsecurityalliance.org/research/csa-research-note-mcp-tool-description-poisoning-20260711-cs/) · Cloud Security Alliance, Jul 2026 | Hidden text in a tool's description instructs the agent, and the user never sees it. First described by Invariant Labs, Apr 2025. | Review has to cover descriptions and instructions, not just code. |
| **P5** Your servers' callers | Vulnerability | [MCP Inspector, CVE-2025-49596](https://www.oligo.security/blog/critical-rce-vulnerability-in-anthropic-mcp-inspector-cve-2025-49596) · Oligo Security, Jun 2025 | With no authentication between client and proxy, a website the developer visited could run code on their machine. | A local server without caller checks is open to the browser. |
| | Guidance | [MCP Security Best Practices](https://modelcontextprotocol.io/specification/2025-11-25/basic/security_best_practices) · MCP specification | Local servers can be reached through DNS rebinding; the spec says to require an authorization token. | The spec asks for this check. |
| **P6** Downstream credentials | Guidance | [MCP Security Best Practices](https://modelcontextprotocol.io/specification/2025-11-25/basic/security_best_practices) · MCP specification | Token passthrough is forbidden: a server must not accept tokens that weren't issued to it. | The spec rules out passing caller tokens through. |
| **P7** Local server access | Vulnerability | [mcp-remote, CVE-2025-6514](https://jfrog.com/blog/2025-6514-critical-mcp-remote-rce-vulnerability/) · JFrog, Jul 2025 | Connecting to a malicious server could run OS commands on the user's machine (CVSS 9.6). | Local MCP components run with your machine's access. |
| | Vulnerability | [EscapeRoute, CVE-2025-53109 and CVE-2025-53110](https://cymulate.com/blog/cve-2025-53109-53110-escaperoute-anthropic/) · Cymulate, 2025 | Symlink and path-prefix flaws let Anthropic's Filesystem MCP server reach files outside its allowed folders. Fixed. | A server's own limits aren't a sandbox. |

## Skills, plugins and hooks

| Question | Type | Source | What happened | How it relates |
|---|---|---|---|---|
| **K2** Unapproved items | Incident | [OpenClaw's skill marketplace and the AI supply chain](https://unit42.paloaltonetworks.com/openclaw-ai-supply-chain-risk/) · Palo Alto Networks Unit 42, Jun 2026 | Koi Security's "ClawHavoc" disclosure found 341 malicious skills on ClawHub, OpenClaw's skill marketplace. | Unvetted marketplace items reached agents. |
| | Background | [Malicious npm packages abuse dependency confusion](https://www.microsoft.com/en-us/security/blog/2026/05/29/33-malicious-npm-packages-abuse-dependency-confusion-profile-developer-environments/) · Microsoft, May 2026 | Packages, not skills: their code ran the moment `npm install` did and collected environment variables. | An agent that installs packages carries the same risk. |
| **K3** Item review | Incident | [Same Unit 42 report](https://unit42.paloaltonetworks.com/openclaw-ai-supply-chain-risk/) | Skills hid a fake "prerequisite" telling the agent to decode and run a remote payload. Unit 42 calls for a line-by-line audit. | Review has to cover setup instructions, not just code. |
| | Background | [Same Microsoft report](https://www.microsoft.com/en-us/security/blog/2026/05/29/33-malicious-npm-packages-abuse-dependency-confusion-profile-developer-environments/) | The code ran at install time, before anyone reviewed what it did. | Review has to happen before anything runs. |
| **K4** Items changing | Background | [postmark-mcp backdoor](https://www.theregister.com/2025/09/29/postmark_mcp_server_code_hijacked/) · The Register, Sep 2025 | After 15 releases, an update to an npm MCP server added a hidden backdoor. | An MCP server, not a skill or plugin. Any item that updates after review could change the same way. |
| **K5** Items granting permissions | Research | [What's the "Matter" with Skills?](https://www.hiddenlayer.com/research/whats-the-matter-with-skills) · HiddenLayer, Jul 2026 | A skill's `allowed-tools` frontmatter could pre-authorize tool use in Claude Code. | An item can bring its own permissions. |
| | Background | [Claude Code issue #67198](https://github.com/anthropics/claude-code/issues/67198) · Jun 2026 | A skill's grants applied when the user invoked it, but not when the model did. | Permission behavior can depend on the path; check each one. |
| **K6** Parsing skill files | Vulnerability | [PyYAML, CVE-2017-18342](https://www.cve.org/CVERecord?id=CVE-2017-18342) · 2018 | Before 5.1, `yaml.load()` could run arbitrary code on untrusted input. Not agent-specific. | Skill metadata is often YAML. An unsafe loader turns a skill file into code. |
| **K7** Where items are active | Background | [OWASP Agentic Top 10, ASI02](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) · OWASP, Dec 2025 | "Least Agency and Least Privilege for Tools": limit each tool's functions, permissions and data scope to what the task needs. | Related principle. It's about how tool permissions are scoped, not where an item is active. |

## Code execution

| Question | Type | Source | What happened | How it relates |
|---|---|---|---|---|
| **X1** Where code runs | Vulnerability | [Securing CI/CD in an agentic world: Claude Code GitHub Action case](https://www.microsoft.com/en-us/security/blog/2026/06/05/securing-ci-cd-in-agentic-world-claude-code-github-action-case/) · Microsoft, Jun 2026 | In a lab, injected text in GitHub issue content led Claude Code's GitHub Action to read `/proc/self/environ` on the runner, exposing its API key. Fixed in 2.1.128. | The agent's tools could reach everything the runner held. |
| | Background | [Malicious npm packages](https://www.microsoft.com/en-us/security/blog/2026/05/29/33-malicious-npm-packages-abuse-dependency-confusion-profile-developer-environments/) · Microsoft, May 2026 | Untrusted code ran on developer machines at install time and collected environment variables. | Code runs with the access of wherever it runs. |
| **X2** Network reach | Vulnerability | [Claude Code DNS exfiltration, CVE-2025-55284](https://embracethered.com/blog/posts/2025/claude-code-exfiltration-via-dns-requests/) · Embrace The Red, Aug 2025 | Injected instructions made Claude Code read `.env` and leak it through DNS lookups. Fixed in v1.0.4. | DNS counts as network reach. |
| **X3** Installing code | Research | [*We Have a Package for You!*](https://arxiv.org/abs/2406.10279) · USENIX Security 2025 | Code models suggest packages that don't exist (205,474 unique names found), opening "package confusion" attacks. | An agent that installs what a model suggests can install an attacker's package. |
| **X4** Machine secrets | Incident | [s1ngularity supply-chain attack](https://www.wiz.io/blog/s1ngularity-supply-chain-attack) · Wiz, Aug 2025 | Malicious Nx versions ran the machine's AI command-line tools with permission-bypass flags to steal files and secrets. | Secrets on the machine were within reach of agent tools. |
| | Vulnerability | [Securing CI/CD in an agentic world](https://www.microsoft.com/en-us/security/blog/2026/06/05/securing-ci-cd-in-agentic-world-claude-code-github-action-case/) · Microsoft, Jun 2026 | The agent's Read tool worked "with full access to the process's environment variables", including the workflow's API key. | Environment variables are machine secrets too. |
| **X5** Escaping the sandbox | Vulnerability | [EscapeRoute](https://cymulate.com/blog/cve-2025-53109-53110-escaperoute-anthropic/) · Cymulate, 2025 | Two flaws let attackers escape the Filesystem MCP server's sandbox. Fixed. | Boundaries enforced by the tool itself can be bypassed. |
| **X6** Pre-approved commands | Vulnerability | [CVE-2025-55284](https://embracethered.com/blog/posts/2025/claude-code-exfiltration-via-dns-requests/) · Embrace The Red, Aug 2025 | `ping`, `nslookup`, `host` and `dig` ran without approval and carried the data out. Fixed in v1.0.4. | "Harmless" pre-approved commands were enough to leak data. |
| **X7** Fresh environment | Background | [Securing CI/CD in an agentic world](https://www.microsoft.com/en-us/security/blog/2026/06/05/securing-ci-cd-in-agentic-world-claude-code-github-action-case/) · Microsoft, Jun 2026 | The runner was an ephemeral VM, yet the agent could still read that run's secrets. | Shows a fresh environment doesn't protect within a run. It doesn't show carry-over between tasks, or that fresh environments prevent it. |

## Browser

| Question | Type | Source | What happened | How it relates |
|---|---|---|---|---|
| **W1** What the browser carries | Research | [*Scamlexity*](https://guard.io/labs/scamlexity-we-put-agentic-ai-browsers-to-the-test-they-clicked-they-paid-they-failed) · Guardio Labs, Aug 2025 | In tests, an AI browser autofilled the user's saved address and card on a fake shop. | Saved payment details became the agent's to spend. |
| **W2** Browser actions | Vulnerability | [Indirect prompt injection in Perplexity Comet](https://brave.com/blog/comet-prompt-injection/) · Brave, Aug 2025 | A hidden Reddit comment made Comet send the user's email and one-time code to the attacker. | The browser acted with the user's logged-in sessions, without a check. |
| **W3** Browser control channel | Guidance | [Changes to remote debugging switches](https://developer.chrome.com/blog/remote-debugging-port) · Chrome for Developers, Mar 2025 | Attackers used remote debugging to extract cookies, so Chrome 136 blocked it on the default profile. | The control channel itself is a target. |
| | Research | [CDP session hijacking](https://labs.cloudsecurityalliance.org/research/csa-research-note-chrome-devtools-session-hijacking-20260817/) · Cloud Security Alliance, Aug 2026 | Code already running on the machine can take over logged-in browser sessions through the debugging protocol. | Anything that reaches the channel gets the sessions. |

## Actions

| Question | Type | Source | What happened | How it relates |
|---|---|---|---|---|
| **A1** Review before use | Vulnerability | [Rules File Backdoor](https://pillar.security/blog/new-vulnerability-in-github-copilot-and-cursor-how-hackers-can-weaponize-code-agents) · Pillar Security, Mar 2025 | Poisoned rules made coding assistants produce code with backdoors, hidden even in pull-request review. | Agent-written changes need a review that can see what they do. |
| | Background | [Amazon Q Developer extension, AWS-2025-015](https://aws.amazon.com/security/security-bulletins/AWS-2025-015/) · AWS, Jul 2025 | Malicious code committed to the repo shipped automatically in version 1.84.0. A syntax error stopped it from running. | Unreviewed changes reached users. The change came from a person, not an agent. |
| **A2** Files that run automatically | Vulnerability | [GitHub Copilot, CVE-2025-53773](https://embracethered.com/blog/posts/2025/github-copilot-remote-code-execution-via-prompt-injection/) · Embrace The Red, Aug 2025 | Copilot rewrote its own settings file to approve its own actions. | Files that control the agent's environment are a target. |
| **A3** Authorizing each request | Vulnerability | [*Invitation Is All You Need*](https://www.safebreach.com/blog/invitation-is-all-you-need-hacking-gemini/) · SafeBreach, Aug 2025 | Gemini deleted calendar events and operated connected devices on instructions from an invite. | Nothing outside the model checked each request. |
| **A4** Final decision | Incident | [Replit agent deletes a production database](https://gizmodo.com/replits-ai-agent-wipes-companys-codebase-during-vibecoding-session-2000633176) · Gizmodo, Jul 2025 | During a code freeze, Replit's agent deleted a company's production database. | A hard-to-undo action went ahead without a person's decision. |
| **A5** Retries | Guidance | [Idempotent requests](https://docs.stripe.com/api/idempotent_requests) · Stripe API documentation | An idempotency key lets a request be retried "without accidentally performing the same operation twice". | The standard way to make retries safe. |
| **A6** Cumulative limits | Guidance | [OWASP LLM10:2025 Unbounded Consumption](https://genai.owasp.org/llmrisk/llm102025-unbounded-consumption/) | Uncontrolled use leads to denial of service and "denial of wallet". OWASP recommends rate limits and quotas. | Limits on the total, not just each action. |
| **A7** Scheduled actions | Background | [OWASP LLM06:2025 Excessive Agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/) | Recommends approval for high-impact actions and limited permissions. | Relevant principle. It doesn't address actions that run later. |
| **A8** Agreements on your behalf | Background | [Moffatt v. Air Canada, 2024 BCCRT 149](https://www.canlii.org/en/bc/bccrt/doc/2024/2024bccrt149/2024bccrt149.pdf) · BC Civil Resolution Tribunal, Feb 2024 | Air Canada's chatbot gave wrong fare information, and the tribunal held the airline responsible for it. | Not an agreement the agent accepted, but the organization answered for what its AI said. |
| | Background | [UNCITRAL Model Law on Automated Contracting](https://uncitral.un.org/en/mlac) · United Nations, Jul 2024 | A legal framework for contracts formed with automation and AI, including rules for attributing what automated systems output. | Legal context. It doesn't set the technical control this question asks about. |
| | Background | [OWASP LLM06:2025 Excessive Agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/) | High-impact actions taken without independent approval. | Relevant principle. It doesn't cover agreements specifically. |

## Other agents

| Question | Type | Source | What happened | How it relates |
|---|---|---|---|---|
| **G1** Requests from agents | Research | [Agent session smuggling](https://unit42.paloaltonetworks.com/agent-session-smuggling-in-agent2agent-systems/) · Palo Alto Networks Unit 42, Oct 2025 | A malicious remote agent slipped extra instructions into an agent-to-agent session. Proof of concept; not seen in the wild. | A request from another agent can carry instructions. |
| **G2** Authority handed on | Research | [*Multi-Agent Systems Execute Arbitrary Malicious Code*](https://arxiv.org/abs/2503.12188) · Triedman et al., 2025 | Malicious content hijacked AutoGen, CrewAI and MetaGPT into running arbitrary code, even when individual agents refused. | Authority passed between agents can be used by whatever steers them. |
| **G3** Rules on delegated work | Guidance | [OWASP Agentic Top 10, ASI03](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) · OWASP, Dec 2025 | "Un-scoped privilege inheritance": a manager agent delegates without least-privilege scoping and passes on its full access. | Constraints have to follow the work, not stay with the delegating agent. |
| **G4** Sub-agent results | Research | [Same paper](https://arxiv.org/abs/2503.12188) | The attack travels through what agents pass to each other, steering which agent runs next. | A sub-agent's output is untrusted input. |

## Oversight

| Question | Type | Source | What happened | How it relates |
|---|---|---|---|---|
| **O1** Action records | Research | [*LLM Agents Can Easily Tamper With Their Own Traces*](https://arxiv.org/abs/2609.30266) · Qin et al., Sep 2026 | Claude Code, Codex and other local harnesses, all except one tested, let agents delete their own traces when asked. Attackers could trigger it, and it also emerged when agents pursued rewards. | Records the agent can reach can't be trusted. The authors advise logging through a mechanism outside the agent's control. |
| | Guidance | [OWASP AI Exchange: Monitor use](https://owaspai.org/goto/monitoruse/) | Log tool calls with their arguments and invoking identity, and keep the agent's audit trail "in tamper-evident storage the agent cannot modify". | Recommends exactly this control, so incidents can be reconstructed. |
| | Guidance | [OWASP AI Agent Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html) | "Log all agent decisions, tool calls, and outcomes", and keep audit trails for forensics. | Covers what to record. It doesn't address protecting the records from the agent. |
| **O2** Stopping it | Background | [NIST SP 800-61 Rev. 3](https://csrc.nist.gov/pubs/sp/800/61/r3/final) · NIST, Apr 2025 | The US incident-response standard covers detection, response and recovery. | Sets the need for a response capability, not a specific way to stop an agent. |
| **O3** Revoking access | Incident | [Salesloft Drift token theft](https://cloud.google.com/blog/topics/threat-intelligence/data-theft-salesforce-instances-via-salesloft-drift) · Google Threat Intelligence, Aug 2025 | Compromised tokens kept working from Aug 8 to at least Aug 18. All were revoked on Aug 20. | Revoking ended the access. Until then, it continued. |
| **O4** Undoing effects | Incident | [Replit](https://gizmodo.com/replits-ai-agent-wipes-companys-codebase-during-vibecoding-session-2000633176) · Gizmodo, Jul 2025 | The agent said the database couldn't be recovered. The founder recovered it himself. | Recovery depended on a mechanism outside the agent, not on what it reported. |
| **O5** Memory provenance | Background | [*Hidden in Memory*](https://arxiv.org/abs/2605.15338) · Pulipaka et al., May 2026 | Poisoned memories were written from documents, web pages and repositories the agent read. | Shows why an entry's source matters. It doesn't test provenance controls. |
| **O6** Data sent to providers | Incident | [Samsung bans ChatGPT](https://www.forbes.com.au/news/innovation/samsung-bans-chatgpt-among-employees-after-sensitive-code-leak/) · Forbes, May 2023 | An engineer uploaded internal source code to ChatGPT. Samsung then banned generative AI tools at work. | Data sent to a model provider leaves your control. |
| **O7** Model changes | Research | [*How is ChatGPT's behavior changing over time?*](https://arxiv.org/abs/2307.09009) · Chen, Zaharia, Zou, 2023 | GPT-4 and GPT-3.5 behaved substantially differently between their March and June 2023 versions. | The same model name can behave differently next month. |
| **O8** Software changes | Incident | [Amazon Q Developer extension, AWS-2025-015](https://aws.amazon.com/security/security-bulletins/AWS-2025-015/) · AWS, Jul 2025 | Injected code reached users inside a normal extension release. | An update can change your agent's software without your review. |
| | Incident | [s1ngularity](https://www.wiz.io/blog/s1ngularity-supply-chain-attack) · Wiz, Aug 2025 | Malicious versions of a widely used build package were published to npm. | The same, through a dependency. |
| **O9** Alerting | Background | [NIST SP 800-61 Rev. 3](https://csrc.nist.gov/pubs/sp/800/61/r3/final) · NIST, Apr 2025 | The US incident-response standard covers detection, response and recovery. | Supports detection as a discipline. It doesn't show that alerts are independent, timely or actionable. |

## Questions without direct evidence yet

We haven't found a public incident, paper or standard that directly covers these eight. Each has related background in the tables above. They are architectural controls derived from mature security principles, and each follows the same rule as the rest: something outside the model must authorize.

| Question | What we have | Principle it rests on |
|---|---|---|
| **K4** Items changing | Background (an MCP server, not a skill) | Integrity verification: pinning and signed releases |
| **K7** Where items are active | Background (tool permissions, not where items load) | Least privilege |
| **X7** Fresh environment | Background (within one run, not across tasks) | Ephemeral, rebuilt environments |
| **A7** Scheduled actions | Background | Authorize at the time of action, not only when scheduled |
| **A8** Agreements on your behalf | Background (legal liability and context) | Authorization by someone entitled to commit the organization |
| **O2** Stopping it | Background | Fail-safe stop for all running work |
| **O5** Memory provenance | Background | Provenance: record where each entry came from |
| **O9** Alerting | Background | Independent detection and response |

Know a source for one of these, or a better one for any question? Open an issue with the link.
