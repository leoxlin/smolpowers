import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const MARKER = "smolpowers:using-smolpowers bootstrap";
const extensionDir = dirname(fileURLToPath(import.meta.url));
const packageRoot = resolve(extensionDir, "../..");
const skillsDir = resolve(packageRoot, "skills");
const bootstrapPath = resolve(skillsDir, "using-smolpowers", "SKILL.md");

let cachedBootstrap;

export default function smolpowersExtension(pi) {
  let injectBootstrap = true;

  pi.on("resources_discover", () => ({ skillPaths: [skillsDir] }));
  pi.on("session_start", () => {
    injectBootstrap = true;
  });
  pi.on("session_compact", () => {
    injectBootstrap = true;
  });
  pi.on("agent_end", () => {
    injectBootstrap = false;
  });
  pi.on("context", (event) => {
    if (!injectBootstrap || event.messages.some(containsBootstrap)) return undefined;

    const message = {
      role: "user",
      content: [{ type: "text", text: bootstrap() }],
      timestamp: Date.now(),
    };
    const index = firstNonSummary(event.messages);
    return {
      messages: [
        ...event.messages.slice(0, index),
        message,
        ...event.messages.slice(index),
      ],
    };
  });
}

function bootstrap() {
  if (cachedBootstrap !== undefined) return cachedBootstrap;

  const skill = stripFrontmatter(readFileSync(bootstrapPath, "utf8"));
  cachedBootstrap = `<EXTREMELY_IMPORTANT>
${MARKER}

The using-smolpowers skill is already loaded for this Pi session. Follow it now and do not load it again.

${skill}

## Pi tool mapping

Use Pi's native skill discovery or \`/skill:name\`. Use lowercase coding tools for repository work. Use an optional task or subagent extension only when it is installed and the skill's criteria are met; otherwise track plan checkboxes and execute directly.
</EXTREMELY_IMPORTANT>`;
  return cachedBootstrap;
}

function stripFrontmatter(content) {
  const match = content.match(/^---\n[\s\S]*?\n---\n([\s\S]*)$/);
  return (match ? match[1] : content).trim();
}

function containsBootstrap(message) {
  const { content } = message;
  if (typeof content === "string") return content.includes(MARKER);
  if (!Array.isArray(content)) return false;
  return content.some(
    (part) =>
      part?.type === "text" &&
      typeof part.text === "string" &&
      part.text.includes(MARKER),
  );
}

function firstNonSummary(messages) {
  let index = 0;
  while (messages[index]?.role === "compactionSummary") index += 1;
  return index;
}
