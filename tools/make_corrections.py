"""Write src/harness-corrections.json: fixes to the app's harness claims, each with the
claim IDs it addresses and the sources that back it, taken from harness-claims-mapping.md
(the verified claim-by-claim results). Run from the repo root."""
import json, re

ALL = ["claude", "codex", "cursor", "openclaw", "hermes", "otherh"]
def without(*h): return [x for x in ALL if x not in h]

rows = open("harness-claims-mapping.md", encoding="utf-8").read().splitlines()
def cells(l): return [x.strip() for x in re.split(r"(?<!\\)\|", l.strip())[1:-1]]
def urls_for(claims):
    out = []
    for cid in claims:
        if cid.startswith("http"):  # an extra source given directly
            out.append(cid); continue
        for l in rows:
            if l.startswith("| " + cid + " "):
                out += re.findall(r"https?://[^\s|)<]+", cells(l)[5])
            elif l.startswith("| **OP-") and re.search(r"\b(OP|HE)-\d+", cid) and cid.split("-")[1] in l.split("[")[0]:
                c = cells(l)
                col = c[1] if cid.startswith("OP") else c[2]
                out += re.findall(r"https?://[^\s|)<]+", col)
    seen = []
    for u in out:
        u = u.rstrip(".,;")
        if u not in seen: seen.append(u)
    return seen

options = [
    ("o7", "{H}'s auto mode picks the model for each request", ["cursor", "otherh"], ["CL-111", "CO-108", "OP-083", "HE-083"],
     "Only Cursor documents an Auto mode that routes each request to a model. In Claude Code, auto mode is a permission mode; Codex, OpenClaw and Hermes have no per-request model picker."),
    ("m4", "{H}'s automatic memory saves what the agent decides, with no check for secrets or personal data", without("codex"), ["CO-024"],
     "Codex redacts secrets from the memories it generates."),
    ("i2", "Only {H}'s permission rules block edits; shell commands can still write these files", without("codex"), ["CO-003"],
     "Codex has no edit-only permission rule: its sandbox applies to spawned commands, not just its file tools."),
    ("o4", "Only {H}'s built-in checkpoints, which rewind its own file edits but not shell commands or effects outside the machine", without("codex", "openclaw"), ["CO-104", "OP-079"],
     "Codex removed its rollback and tells users to make Git checkpoints; OpenClaw's rewind changes the transcript, not files."),
    ("m3", "{H} files memory by project, but the agent's file or shell access can read other projects' memory", without("cursor", "openclaw", "hermes"), ["CU-015", "OP-015", "HE-015"],
     "Cursor has no per-project memory store since 2.1; OpenClaw keeps memory per agent workspace and Hermes per profile."),
    ("a1", "{H} asks before each edit, but nothing reviews what gets merged", without("cursor", "openclaw", "hermes"), ["CU-059", "OP-059", "HE-059"],
     "Cursor, OpenClaw and Hermes write file edits without asking."),
    ("a2", "{H} asks before each file edit, but nothing marks these files as special", without("cursor", "openclaw", "hermes"), ["CU-060", "OP-060", "HE-060"],
     "Cursor, OpenClaw and Hermes write file edits without asking."),
    ("n1", "{H}'s connector signs in as each user, and the source checks that user's current permissions", without("openclaw", "hermes"), ["OP-020", "HE-020"],
     "OpenClaw and Hermes have no connector that signs in per user; credentials belong to the whole gateway or profile."),
    ("x5", "{H}'s sandbox closes these routes, and nothing (an exception setting, a parameter, a restart) lets code run outside it", without("cursor"), ["CU-051", "CL-069", "CO-068", "OP-051", "HE-051"],
     "Cursor runs allowlisted calls outside the sandbox, can rerun failed commands outside it, and can turn it off (Run Everything, insecure_none, --sandbox disabled). For the others it holds only when no exception, approval or component (hooks, local MCP servers, code tools) runs outside the sandbox, so the answer now names those conditions.",
     "{H}'s sandbox closes these routes, and nothing lets code run outside it: no excluded command or approved escalation, no setting that turns it off, and nothing it starts (hooks, local MCP servers, code tools) runs outside it"),
    ("o5", "Memory is {H}'s plain files: a person can read them, but no system records where each entry came from", without("openclaw"), ["OP-080"],
     "OpenClaw's memory records which session each automatically ingested entry came from."),
    ("o8", "{H} updates itself automatically", without("hermes"), ["HE-086"],
     "Hermes doesn't update itself: updates run through `hermes update` or the desktop Update control."),
]
notes = [
    ("p2", "Check what your allowlist matches on: the exact URL, or command and arguments, not just the server's name. Whether an approved server's contents can change is P3.",
     "If {H} has an allowlist for MCP servers, check what it matches on: the exact URL, or command and arguments, not just the server's name. If it has none, check who can edit its MCP server configuration. Whether an approved server's contents can change is P3.",
     ["OP-034", "HE-034"], "OpenClaw and Hermes have no MCP server allowlist."),
    ("w2", "Check whether a site approval lasts for the whole session, and whether another approval path can skip the per-site check.",
     "If {H} approves browser actions per site, check whether an approval lasts for the whole session, and whether another path can skip the per-site check. If it has no per-site approval, check whether the browser tool is allowed at all, and which profile and sites it can reach.",
     ["OP-057", "HE-057"], "OpenClaw and Hermes have no per-site browser approvals."),
]
old_wc = "Not established in the documentation reviewed as of Nov 2026. Check your actual configuration."
_src = open("src/v20-export.html", encoding="utf-8").read()
_i = _src.index("var D = {"); _k = _src.index("{", _i); _d = 0
for _p in range(_k, len(_src)):
    if _src[_p] == "{": _d += 1
    elif _src[_p] == "}":
        _d -= 1
        if _d == 0: _end = _p + 1; break
QS = {q["id"]: q for q in json.loads(_src[_k:_end])["qs"]}
def cur(q, h): return QS[q].get("wc", {}).get(h)
CL_SANDBOX = ("sandbox.enabled covers Bash, PowerShell and Monitor commands and the processes they start; without it, commands run unsandboxed. "
              "Commands matching excludedCommands run outside it; allowUnsandboxedCommands: false turns off the unsandboxed retry; failIfUnavailable makes Claude Code exit at startup rather than run commands unsandboxed. "
              "What you type at the ! prompt, hooks and local MCP servers run outside it.")
CO_SANDBOX = ("sandbox_mode (read-only, workspace-write, danger-full-access); requirements can limit it with allowed_sandbox_modes or permission profiles (allowed_permission_profiles). "
              "Commands an allow rule matches, and escalations you approve, run outside the sandbox, and local stdio MCP servers always run outside it. Where hooks run isn't documented.")
where = [
    ("t1", "codex", old_wc, "Codex detects skill changes automatically, so skills can be added or changed mid-session, and a skill can declare MCP servers that Codex installs. Project MCP servers in .codex/config.toml load only in trusted projects. Whether a connected server's tool-list changes are picked up isn't documented.", ["CO-037"]),
    ("k4", "codex", old_wc, "Workspace plugin marketplaces sync daily and can add and update plugins, unless a Git source is pinned to a commit sha. Local skills are picked up as soon as they change.", ["CO-053"]),
    ("w1", "codex", old_wc, "The Codex CLI and IDE extension have no browser. In the desktop app, the built-in browser uses its own profile, separate from your regular browser; the browser extension uses your regular, signed-in profile.", ["CO-074"]),
    ("w2", "codex", old_wc, "CLI and IDE: no browser. Desktop app: check the site rules, how long an approval lasts (this turn or this thread), and whether full Chrome DevTools Protocol access is allowed; it asks before using full CDP. Computer Use can also operate a browser as a native app, and the browser's site rules don't apply to that path.", ["CO-076"]),
    ("w3", "codex", old_wc, "CLI and IDE: no browser. Desktop app: check which browser profile has the extension, and whether full Chrome DevTools Protocol access is enabled (browser_use_full_cdp_access in managed configuration).", ["CO-078"]),
    ("o8", "codex", old_wc, "check_for_update_on_startup controls update checks (set it to false only when updates are centrally managed). The desktop app installs updates on its own unless in_app_updates = false is set in managed requirements.", ["CO-110"]),
    ("x1", "claude", cur("x1", "claude"), CL_SANDBOX, ["CL-058"]),
    ("x5", "claude", cur("x5", "claude"), CL_SANDBOX, ["CL-068", "CL-069", "https://code.claude.com/docs/en/settings-reference.md"]),
    ("x1", "codex", cur("x1", "codex"), CO_SANDBOX, ["CO-057", "https://learn.chatgpt.com/docs/permissions.md", "https://learn.chatgpt.com/docs/agent-configuration/rules.md"]),
    ("x5", "codex", cur("x5", "codex"), CO_SANDBOX, ["CO-067", "CO-068", "https://learn.chatgpt.com/docs/permissions.md"]),
    ("x5", "openclaw", None, "OpenClaw's sandboxing is off by default. When it's on, elevated execution is an exec-only escape hatch from it; only a sandbox set to \"required\" can't be escaped that way. Check the agent's sandbox mode and who may use elevated execution.", ["OP-051", "https://docs.openclaw.ai/gateway/sandboxing"]),
    ("x5", "hermes", None, "Hermes's terminal sandbox doesn't confine its code-execution tool (a host subprocess), MCP servers, plugins, hooks or skills. Only running the whole agent in a container (the Hermes Docker image or OpenShell) does.", ["HE-051"]),
    ("i5", "claude", cur("i5", "claude"), cur("i5", "claude") + " SDK runs load project .mcp.json servers only when settingSources includes project settings.", ["CL-006"]),
    ("m3", "claude", cur("m3", "claude"), "autoMemoryEnabled, CLAUDE_CODE_DISABLE_AUTO_MEMORY, autoMemoryDirectory. By default memory is in ~/.claude/projects/<project>/memory/: one directory per repository, shared by its worktrees and subdirectories, unless autoMemoryDirectory or CLAUDE_CODE_PROJECT_DIR_NAME points several projects at one directory.", ["CL-020", "https://code.claude.com/docs/en/memory.md"]),
    ("w3", "claude", cur("w3", "claude"), "Claude Code reaches the browser through the extension's native messaging host and the bridge.claudeusercontent.com relay; the docs mention a named pipe for Windows and no debugging port. Whether other local processes can reach that channel isn't documented.", ["CL-081"]),
    ("g2", "claude", cur("g2", "claude"), "Sub-agent tools and disallowedTools; mcpServers can give a sub-agent servers the main conversation doesn't have (plugin sub-agents ignore it). Sub-agents generally inherit the parent's permission mode, and the parent's mode can override the one a sub-agent sets. omitClaudeMd skips user, project and local CLAUDE.md files, but managed policy files still load; CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH limits nesting.", ["CL-093"]),
    ("g3", "claude", cur("g3", "claude"), "Sub-agent tools and disallowedTools; mcpServers can give a sub-agent servers the main conversation doesn't have (plugin sub-agents ignore it). Sub-agents generally inherit the parent's permission mode, and the parent's mode can override the one a sub-agent sets. omitClaudeMd skips user, project and local CLAUDE.md files, but managed policy files still load; CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH limits nesting.", ["CL-096"]),
    ("o8", "claude", cur("o8", "claude"), cur("o8", "claude") + " A manual claude update still works; DISABLE_UPDATES blocks every update path, and FORCE_AUTOUPDATE_PLUGINS turns plugin auto-update back on.", ["CL-113", "https://code.claude.com/docs/en/plugins/loading.md"]),
    ("i2", "codex", cur("i2", "codex"), "In the workspace-write sandbox, .git, and .agents, .codex and .aws when they exist as directories, stay read-only inside writable folders, for shell commands too. AGENTS.md isn't on that list.", ["CO-001", "https://learn.chatgpt.com/docs/permissions.md"]),
    ("m1", "codex", cur("m1", "codex"), "[features] memories (off by default), memories.generate_memories, memories.use_memories, memories.disable_on_external_context. Memories live in one store under $CODEX_HOME and are consolidated globally; the docs describe no per-project separation.", ["CO-014"]),
    ("m2", "codex", cur("m2", "codex"), "[features] memories (off by default), memories.generate_memories, memories.use_memories, memories.disable_on_external_context. Memories live in one store under $CODEX_HOME and are consolidated globally; the docs describe no per-project separation.", ["CO-017"]),
    ("m3", "codex", cur("m3", "codex"), "[features] memories (off by default), memories.generate_memories, memories.use_memories, memories.disable_on_external_context. Memories live in one store under $CODEX_HOME and are consolidated globally; the docs describe no per-project separation.", ["CO-020", "https://learn.chatgpt.com/docs/customization/memories.md"]),
    ("t3", "codex", cur("t3", "codex"), "shell_environment_policy filters the environment variables passed to commands; by default it keeps names containing KEY, SECRET or TOKEN. Credential files need managed [permissions.filesystem] deny_read.", ["CO-039", "https://learn.chatgpt.com/docs/enterprise/managed-configuration.md"]),
    ("x4", "codex", cur("x4", "codex"), "shell_environment_policy filters the environment variables passed to commands; by default it keeps names containing KEY, SECRET or TOKEN. Credential files need managed [permissions.filesystem] deny_read.", ["CO-064", "https://learn.chatgpt.com/docs/enterprise/managed-configuration.md"]),
    ("p2", "codex", cur("p2", "codex"), "The mcp_servers allowlist in requirements matches name and identity (command for stdio servers, URL for HTTP). The plain string form doesn't check arguments, cwd, env or env_vars; use the matcher-table form to pin the executable and arguments.", ["CO-044"]),
    ("x6", "codex", cur("x6", "codex"), "Check the .rules files (in ~/.codex/rules, the project and admin rules) for prefix_rule entries with decision \"allow\": matching commands run outside the sandbox without asking. Also check the approval policy.", ["CO-069"]),
    ("k5", "codex", None, "Codex skills can't pre-approve tools: skill metadata has no allowed-tools field, and scripts a skill runs have their own approval category (skill_approval).", ["CO-055"]),
    ("k5", "cursor", None, "Cursor skills can't pre-approve tools: the skill format has no allowed-tools field. Check plugin-bundled hooks, permissions.json and MCP allowlists instead.", ["CU-042"]),
    ("k5", "openclaw", None, "OpenClaw's skill docs describe no way for a skill to pre-approve tools. Check its tool policy and exec approvals instead.", ["OP-042"]),
    ("k5", "hermes", None, "Hermes skills can't pre-approve tools, but a loaded skill's required_environment_variables pass those secrets through to the commands it runs.", ["HE-042"]),
]

# ---- Batch 3 (partly-right claims). Question IDs here are the app's internal IDs (display C2 = c3, A7 = a8).
def opt_text(q, frag):
    hits = [o["t"] for o in QS[q]["a"] if frag in o["t"]]
    assert len(hits) == 1, (q, frag, hits)
    return hits[0]

def add(q, h, text, claims):
    """Add a harness-specific "Where to check" sentence: appended to this run's entry for (q, h) if
    there is one, otherwise to the app's current text, otherwise a new entry."""
    for n, (q2, h2, o, t, c) in enumerate(where):
        if (q2, h2) == (q, h):
            where[n] = (q2, h2, o, (t + " " + text).strip(), c + [x for x in claims if x not in c]); return
    o = cur(q, h)
    where.append((q, h, o, ((o + " ") if o else "") + text, claims))

def reword_option(q, frag, new, claims, why):
    t = opt_text(q, frag)
    for n, e in enumerate(options):
        if e[0] == q and e[1] == t:
            options[n] = (e[0], e[1], e[2], e[3] + claims, e[4] + " " + why, new); return
    options.append((q, t, None, claims, why, new))

def reword_note(q, new, claims, why):
    notes.append((q, QS[q]["hn"], new, claims, why))

themes = []
def reword_finding(old, new, claims, why):
    themes.append({"old": old, "new": new, "count": _src.count(old), "claims": claims, "why": why, "sources": urls_for(claims)})

# Shared notes and options whose wording was too narrow for some harnesses.
reword_note("p3", "Without a pinned version (such as pkg@1.2.3), the package runner installs whatever version the registry resolves when the package isn't already cached, so a later start can run a different version.", ["CL-045"], "Unpinned packages are fetched when not cached; npm doesn't promise a new resolution on every start.")
reword_note("p4", "Check what {H} shows before a server connects. As soon as it connects, the server's instructions and its tool names or descriptions can reach the model's context.", ["CL-046", "CO-047"], "Claude Code loads only tool names when tool search is on; Codex always reads the instructions field.")
reword_note("a3", "Business details such as recipient or amount need your own tool, an MCP server you built, the target service, or a hook that inspects each tool call before it runs, to check them.", ["CL-085"], "A pre-tool hook can inspect a call's input and block it.")
reword_note("i6", "Count every instruction file {H} loads, at every level it supports, and every skill file, not just the system prompt.", ["CO-008", "OP-005", "HE-005"], "Codex, OpenClaw and Hermes have no organization-level instruction files.")
reword_note("c1", "Check every tool that can do the same thing, including the shell, web tools and MCP servers.", ["CO-009"], "Codex has no separate web fetch tool.")
reword_note("w1", "Check which browser profile the integration drives and what it's signed in to, and, if {H} has per-site permissions, whether another path can bypass them.", ["CO-075", "CU-056", "OP-056", "HE-056"], "Not every harness has per-site permissions.")
reword_note("o6", "Everything in the session's context is sent to the provider, including files it reads and command output. Which terms apply depends on the account or API key {H} uses and its data settings, since consumer and commercial plans can differ.", ["CU-081", "OP-081", "HE-081"], "Terms also depend on API keys and data settings (Cursor's Privacy Mode; OpenClaw and Hermes use your provider key).")
reword_option("c1", "web fetch", "{H} denies that tool, but another tool (the shell, a web tool, an MCP server) can do the same thing unchecked", ["CO-010"], "Codex has no separate web fetch tool.")
reword_option("a2", "asks before each file edit", "{H} asks before each file edit, but doesn't treat files that run automatically, such as CI workflows, as special", ["CL-084", "CO-081"], "Claude Code and Codex protect some auto-run files (such as .git), but not CI workflows.")
reword_option("k3", "trust warning", "{H} warns or runs an automated scan before installing, but no person reviews what the item contains", ["CO-052", "CU-040", "OP-040", "HE-040"], "Several harnesses scan automatically; none has a person review the contents (Cursor's Marketplace review is covered in Where to check).")
reword_option("x4", "sandbox blocks credential reads", "{H}'s sandbox blocks credential reads for commands, but another route (its file tools, hooks, plugins or MCP servers) can still read the same credentials", ["CO-066", "CU-050", "OP-050", "HE-050"], "In Codex, OpenClaw and Hermes the file tools are covered with commands; hooks, plugins and MCP servers aren't.")
reword_finding("Whoever administers {H} settings for your organization", "Whoever administers {H}'s settings, for your organization or on the machine it runs on", [f"{h}-{n:03d}" for h in ("OP", "HE") for n in range(91, 98)], "OpenClaw has no organization-managed settings; Hermes has an admin-managed scope.")
reword_finding("Check whether {H}'s sandbox makes those paths read-only for shell commands too.", "Check whether {H}'s sandbox makes those paths read-only for shell commands too, or keeps them out of commands' reach.", ["HE-090"], "Hermes has no per-path read-only setting for commands.")

# Harness-specific facts, as "Where to check" lines.
add("i3", "claude", "Files, command output and MCP results go straight to the model that decides. WebFetch first summarizes pages with a separate model call, and auto mode adds a classifier that reviews actions: both are model judgments, not enforced separation.", ["CL-005"])
add("i3", "codex", "No documented filter screens content before the model reads it: Codex's safety monitoring runs asynchronously, and Auto-review checks only actions that need approval.", ["CO-005"])
add("i3", "cursor", "Untrusted content goes to the same model that decides. In Auto-review (the default since 3.6), a separate classifier checks non-allowlisted shell, MCP and Fetch calls; Cursor says this isn't a security boundary.", ["CU-004"])
add("i3", "openclaw", "OpenClaw marks external content as untrusted before the model sees it, but nothing outside the model blocks it; the model can still be influenced by what it reads.", ["OP-004"])
add("i3", "hermes", "Hermes pattern-scans context files, memory writes and skills for injection before they enter the prompt, but passes tool output and web pages through unchanged.", ["HE-004"])
add("i5", "claude", "The docs describe no new prompt when trusted files change later; project .mcp.json servers still need their own approval.", ["CL-007"])
add("i5", "codex", "Trust is a one-time decision per project for config, rules and AGENTS.md, but hooks are re-reviewed: new or changed hooks are skipped until you trust them.", ["CO-007"])
add("m4", "claude", "Claude Code's docs describe no filter for secrets or personal data in automatic memory.", ["CL-024"])
add("m4", "cursor", "Only Cursor Automations have memory (the Memories tool, on by default). Values marked as Runtime Secrets are kept out of the transcript and tool output; nothing else is filtered.", ["CU-017", "CU-016"])
add("m4", "openclaw", "OpenClaw documents no filter for secrets or personal data on memory writes; its admission policy only decides which sessions feed memory.", ["OP-017", "OP-016"])
add("m4", "hermes", "Hermes scans memory writes for injection and exfiltration patterns, not for secrets or personal data, and saves without approval by default (write_approval: false).", ["HE-017", "HE-016"])
add("k5", "claude", "In Claude Code, a skill's allowed-tools field pre-approves the listed tools for the turn that invokes it; workspace trust doesn't gate it, and managed allowManagedPermissionRulesOnly turns it off.", ["CL-055"])
add("x1", "claude", "Skill scripts Claude runs through Bash are sandboxed; the docs don't say whether a skill's inline ! commands are.", ["CL-060"])
add("x1", "codex", "", ["CO-059"])
add("x1", "cursor", "Agent commands, including skill scripts, run in Cursor's sandbox unless allowlisted; hooks and local MCP servers run outside it.", ["CU-045"])
add("x1", "openclaw", "OpenClaw's hooks and plugins run outside the sandbox with the Gateway's access; skill scripts run through the exec tool, so they're sandboxed when sandboxing is on (it's off by default).", ["OP-045"])
add("x3", "claude", "Claude Code doesn't review or verify packages; installs run when an allow rule, auto mode or an allowed registry domain lets the command through.", ["CL-064"])
add("x3", "codex", "Codex doesn't review packages. In the default workspace-write sandbox commands have no network, so registry installs need network enabled, an approval or an allow rule.", ["CO-063"])
add("a1", "claude", "Claude Code asks before each edit only in Manual mode; auto mode, the default in a terminal or VS Code from v2.1.283, doesn't.", ["CL-083"])
add("a1", "codex", "Codex asks before edits only in read-only mode or an untrusted project; by default it edits the workspace without asking.", ["CO-080"])
add("a2", "claude", "Protected paths (.git, .husky, .claude, .mcp.json, pre-commit config, shell rc files) always need approval, but CI workflows such as .github/workflows aren't on the list.", ["CL-084"])
add("a2", "codex", "In workspace-write, .git, .codex, .agents and .aws are protected, but CI and pipeline files aren't.", ["CO-081"])
add("a3", "claude", "Deny and ask rules can match exact parameter values (Tool(param:value)), but can't evaluate conditions such as amount limits or approved recipients; a PreToolUse hook can.", ["CL-086"])
add("a3", "cursor", "Allowlists match command prefixes or server:tool. The Auto-review classifier can take plain-English rules about recipients or amounts, but only as best-effort judgment; hooks can inspect arguments.", ["CU-062"])
add("a3", "hermes", "Hermes matches dangerous command patterns, can require approval for write calls to MCP servers marked trust: untrusted, and has per-server spend_limit budgets: a coarse limit, not a check of each request's recipient or amount.", ["HE-062"])
add("g4", "claude", "Claude Code labels sub-agent results as carrying no authority, and auto mode's classifier reviews them; that's model-level handling, not a constrained interface.", ["CL-099"])
add("g4", "hermes", "Hermes passes only a sub-agent's final summary into the parent's context, and a task can set an output_schema, which constrains structure, not truth.", ["HE-072"])
add("o1", "claude", "The agent can read transcripts; writes to ~/.claude are protected (prompted in Manual mode) and denied to sandboxed commands, but allowed in bypass mode or for unsandboxed commands.", ["CL-102"])
add("o1", "codex", "Transcripts live in CODEX_HOME (~/.codex), outside the workspace: commands can read them but change them only with full access or an approval. OpenTelemetry export (opt-in) is the outside store.", ["CO-098", "CO-099"])
add("o1", "cursor", "Local transcripts are on your machine; Cloud Agent transcripts are on Cursor's backend. Enterprise audit logs cover authentication and admin events only.", ["CU-073", "CU-074"])
add("o1", "openclaw", "OpenClaw also keeps a metadata-only audit ledger in its state database, on the same host as the agent.", ["OP-073", "OP-074"])
add("o4", "claude", "Checkpoints rewind Claude's file edits, and later shell changes to those same files, but not files only shell commands changed, or anything outside the machine.", ["CL-107"])
add("o4", "codex", "Codex's sandbox keeps .git read-only by default; check the full-access and push routes.", ["CO-103"])
add("o4", "cursor", "Checkpoints revert files the agent changed, not command side effects or anything outside the machine.", ["CU-079"])
add("o4", "hermes", "Checkpoints are opt-in (as of v2) and snapshot before file writes and some destructive commands, but not other shell effects or anything outside the machine.", ["HE-079"])
add("o5", "claude", "Claude Code records when each memory entry was written, not where it came from.", ["CL-108"])
add("o5", "codex", "Memory folders hold summaries with supporting evidence from prior chats, but no reliable per-entry source record.", ["CO-105"])
add("o5", "cursor", "Only Automations have memory; it's held by the Memories tool, not plain files, and the docs describe no record of where entries came from.", ["CU-080"])
add("o5", "hermes", "Hermes stores memory as plain entries the agent adds, patches or removes; the docs describe no record of where each came from.", ["HE-080"])
add("o8", "claude", "Only native installs update themselves; Homebrew, WinGet, apt, dnf and apk installs don't by default. To pin, use DISABLE_UPDATES or the managed requiredMinimumVersion and requiredMaximumVersion settings.", ["CL-114", "CL-115"])
add("o8", "codex", "The CLI checks for updates at startup, but you install them; the desktop app updates itself.", ["CO-112"])
add("o8", "openclaw", "Gateway automatic updates are off by default, but long-running packaged headless nodes update automatically by default.", ["OP-085", "OP-086"])
add("o8", "hermes", "Hermes never updates itself: updates run through hermes update or the desktop Update control; only plugin auto-update is opt-in.", ["HE-085"])
add("i6", "codex", "AGENTS.md loads at the user (CODEX_HOME) and project levels, plus fallback filenames; skills load from repository, user, admin (/etc/codex/skills) and system locations.", ["CO-008"])
add("i6", "openclaw", "OpenClaw loads the agent workspace files (AGENTS.md, SOUL.md, IDENTITY.md, USER.md, MEMORY.md), the project folder's AGENTS.md, and every skill file.", ["OP-005"])
add("i6", "hermes", "Hermes loads SOUL.md from HERMES_HOME, the project context chain (.hermes.md, AGENTS.md, CLAUDE.md, .cursorrules), the memory files and every skill.", ["HE-005"])
add("c1", "codex", "Codex has no separate web fetch tool: the other routes are web search (live mode), app and connector tools, MCP servers and, in the desktop app, the browser.", ["CO-009", "CO-010"])
add("m1", "codex", "Memories are generated in the background from idle past chats, not chosen by the agent during a session.", ["CO-016"])
add("m1", "cursor", "The editor's Memories feature was removed in 2.1; only Automations have memory, through the Memories tool, which is on by default.", ["CU-011", "CU-010"])
add("m1", "openclaw", "OpenClaw has no single memory switch: its workspace instructions tell the agent to save durable facts, and memory-core can add session ingestion and dreaming.", ["OP-011", "OP-010"])
add("m2", "codex", "In workspace-write the agent can read these files but needs approval to change them; with full access it can edit or delete them.", ["CO-019"])
add("m2", "cursor", "Automations memory is held by Cursor's Memories tool, not plain files; the agent can write and delete entries through it.", ["CU-013"])
add("m3", "codex", "", ["CO-022"])
add("m3", "openclaw", "OpenClaw keeps memory per agent workspace, not per project: projects handled by one agent share it, and the agent's file or shell access can reach other workspaces.", ["OP-014"])
add("m3", "hermes", "Hermes keeps memory per profile, not per project: projects handled by one profile share it.", ["HE-014"])
add("u4", "codex", "Codex reads AGENTS.md, AGENTS.override.md and .agents/skills; CLAUDE.md only if it's added to project_doc_fallback_filenames.", ["CO-034"])
add("u4", "openclaw", "OpenClaw loads the project folder's AGENTS.md; it doesn't load CLAUDE.md natively.", ["OP-026"])
add("p7", "codex", "Codex starts local stdio MCP servers outside its command sandbox, with your user's access.", ["CO-048"])
add("k3", "codex", "Codex asks you to trust hooks (recorded per hook), but nothing reviews a skill's or plugin's instructions, scripts or bundled servers.", ["CO-052"])
add("k3", "cursor", "Cursor reviews Marketplace plugins and their updates; local plugins, repo skills, community and team-marketplace items get no content review.", ["CU-040"])
add("k3", "openclaw", "ClawHub runs automated scans (VirusTotal, ClawScan, static analysis), shows the result before install and refuses blocking outcomes; a Review outcome lets installation continue, and no person reviews the contents.", ["OP-040"])
add("k3", "hermes", "Skills Guard scans every skill before it's indexed and blocks dangerous verdicts; other findings can be overridden with --force, and no person reviews the contents.", ["HE-040"])
add("x2", "codex", "Codex's network proxy blocks local and private addresses by default (allow_local_binding = false), but escalated commands, commands allowed outside the sandbox, local MCP servers and web tools bypass it.", ["CO-061"])
add("x4", "codex", "Managed deny_read blocks both commands and Codex's file tools (only the direct tools on native Windows); hooks and local MCP servers can still read.", ["CO-066"])
add("x4", "cursor", "By default sandboxed commands can read outside the workspace, and ~/.ssh is always readable; Read Access = Workspace (3.23+) or .cursorignore narrows this. Hooks, MCP servers and allowlisted commands aren't covered.", ["CU-050"])
add("x4", "openclaw", "OpenClaw's file tools run inside the sandbox with commands; hooks and plugins run outside it with the Gateway's access.", ["OP-050"])
add("x4", "hermes", "Hermes's file tools run through the same backend as commands; its code-execution tool, MCP servers, plugins and hooks run outside it.", ["HE-050"])
add("t3", "hermes", "Hermes strips most secret environment variables from terminal, code-execution and MCP child processes, so the main risk is secret files on disk.", ["HE-030"])
add("x6", "codex", "", ["CO-070"])
add("x7", "codex", "Each Codex Cloud task starts from the environment's prepared filesystem, with cached dependencies; follow-up turns in that task share its state.", ["CO-073"])
add("x7", "cursor", "Each Cloud Agent runs in its own VM, started from a saved environment snapshot that can carry state; follow-ups in that agent share it.", ["CU-055"])
add("x7", "openclaw", "OpenClaw has no hosted service; its cloud sessions run on throwaway workers you lease.", ["OP-055"])
add("x7", "hermes", "Hermes Cloud runs long-lived hosted agent instances, not a fresh machine per session.", ["HE-055"])
add("w1", "codex", "Computer Use can operate a browser as a native app, outside the browser's site rules.", ["CO-075"])
add("w1", "cursor", "Cursor's browser is a built-in web view with per-workspace cookies and logins that persist between sessions, not your own Chrome profile.", ["CU-056"])
add("w1", "openclaw", "OpenClaw drives either a managed, isolated browser or your own Chrome through its extension; it has no per-site permissions.", ["OP-056"])
add("w1", "hermes", "Hermes uses a fresh, throwaway profile by default, or, if you opt in, a managed copy of your everyday profile with its logins; it has no per-site permissions.", ["HE-056"])
add("w2", "codex", "", ["CO-077"])
add("w3", "codex", "", ["CO-079"])
add("w3", "hermes", "Hermes drives Chromium over the Chrome DevTools Protocol and has no extension channel.", ["HE-058"])
add("a8", "codex", "Codex's scheduled tasks exist in the desktop app and on the web, and run unattended with default sandbox settings; the CLI and IDE have none.", ["CO-087"])
add("o9", "codex", "Codex's safety monitoring can pause a task it flags, but tells only the user in the session; telemetry export is opt-in.", ["CO-113"])
add("o9", "openclaw", "OpenClaw keeps a metadata-only audit ledger and can export telemetry, but has no built-in alerting on suspicious activity.", ["OP-087"])
add("o9", "hermes", "Hermes's monitoring plane is content-free, and it has no built-in alerting on suspicious activity.", ["HE-087"])
add("i2", "cursor", "Cursor's edit tool doesn't block rule-file edits by default: only Enterprise .cursor Directory Protection or CLI Write() deny rules do. Shell commands, sandboxed or not, can still write .cursor/rules, AGENTS.md and CLAUDE.md.", ["CU-002"])
add("c3", "cursor", "Fetch calls, allowlisted commands and hooks bypass the command sandbox; stdio MCP servers are sandboxed only under admin MCP Network Controls.", ["CU-009"])
add("n1", "cursor", "Cursor has no connectors of its own: retrieval goes through MCP servers, which sign in with a shared key, a service account or each user's OAuth login; Automations can run as a dedicated service account.", ["CU-019", "CU-020"])
add("u2", "cursor", "Local agents run with your credentials. Cloud Agents limit repo access to the triggering user, but team follow-ups let others steer an agent that holds its creator's secrets.", ["CU-023"])
add("u2", "openclaw", "Everyone who can message a tool-enabled agent shares its tool authority; toolsBySender and operator roles can vary tools per sender, but credentials stay shared.", ["OP-023"])
add("u3", "cursor", "On a shared OS account, Cursor's local transcripts and caches are shared; Cloud Agents each run in their own VM. The editor has no memory store.", ["CU-025"])
add("u3", "hermes", "Hermes gives each user their own session in group chats by default, but memory is shared across the profile.", ["HE-025"])
add("u1", "openclaw", "OpenClaw's built-in channels pass the sender's platform ID to Gateway tool policy (toolsBySender), where the model can't change it; check custom or HTTP integrations.", ["OP-021", "OP-022"])
add("u1", "hermes", "Hermes authorizes senders through allowlists and pairing, then treats every authorized caller the same; check custom or HTTP integrations.", ["HE-021", "HE-022"])
add("g2", "cursor", "Hooks run inside sub-agents; readonly: true restricts a sub-agent's writes, and subagentStart hooks can check it; cloud sub-agents follow cloud rules, not local Run Modes.", ["CU-069"])
add("g2", "openclaw", "Sub-agents use the parent's profile and tool policy, plus a sub-agent restriction layer and a run timeout; authority isn't bound to the specific task.", ["OP-069"])
add("g2", "hermes", "Each sub-agent inherits the parent's enabled toolsets, some tools are blocked for children, and approvals go to the parent's chat; authority isn't bound to the specific task.", ["HE-069"])
add("o6", "cursor", "Requests go through Cursor's backend; which terms apply depends on Privacy Mode and on the model chosen (some need data retention).", ["CU-081"])
add("o6", "openclaw", "OpenClaw has no account of its own: terms depend on the provider API key or subscription login it's configured with.", ["OP-081"])
add("o6", "hermes", "Hermes has no account of its own: terms depend on the provider key or login it uses, which can be a borrowed Codex CLI login.", ["HE-081"])
add("t1", "openclaw", "OpenClaw only uses MCP servers saved in its configuration; check which of them support list-change notifications, which let a server change its tools mid-session.", ["OP-029"])
add("k4", "openclaw", "OpenClaw skill updates run when someone runs openclaw skills update; Gateway auto-update is off by default.", ["OP-041"])
add("k4", "hermes", "Hermes's own learning loop can modify or delete any skill, hermes update adds newly bundled skills, and plugin auto-update is opt-in.", ["HE-041"])
add("k7", "hermes", "Hermes has no per-project install scope: skills live in ~/.hermes/skills and are active in every project the profile works on.", ["HE-043"])
add("o2", "openclaw", "OpenClaw's /stop cancels a run's child sub-agents, but chat.abort doesn't cascade, and scheduled automations keep running.", ["OP-076"])
add("o7", "hermes", "Hermes has built-in short model names (user aliases take precedence); the docs don't say whether they move to newer models.", ["HE-084"])

out = {"checked": "2026-11-13",
       "about": "Corrections to the app's harness claims, applied by tools/build_index.py. Each entry lists the claim IDs it fixes (see harness-claims-mapping.md) and its sources.",
       "options": [dict({"q": q, "text": t, "hs": hs, "claims": c, "why": w, "sources": urls_for(c)}, **({"new_text": r[0]} if r else {})) for q, t, hs, c, w, *r in options],
       "notes": [{"q": q, "old": o, "new": n, "claims": c, "why": w, "sources": urls_for(c)} for q, o, n, c, w in notes],
       "where_to_check": [{"q": q, "harness": h, "old": o, "text": t, "claims": c, "sources": urls_for(c)} for q, h, o, t, c in where],
       "findings": themes}
missing = [e["claims"] for k in ("options", "notes", "where_to_check", "findings") for e in out[k] if not e["sources"]]
assert not missing, missing
json.dump(out, open("src/harness-corrections.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("options", len(options), "notes", len(notes), "where_to_check", len(where), "findings", len(themes))
