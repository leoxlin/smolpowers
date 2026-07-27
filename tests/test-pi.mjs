import assert from "node:assert/strict";
import { dirname, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import test from "node:test";

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, "..");
const extensionPath = resolve(root, ".pi/extensions/smolpowers.js");

async function loadExtension() {
  const handlers = new Map();
  const pi = {
    on(event, handler) {
      assert.equal(handlers.has(event), false, `duplicate ${event} handler`);
      handlers.set(event, handler);
    },
  };
  const mod = await import(`${pathToFileURL(extensionPath).href}?${Math.random()}`);
  mod.default(pi);
  return handlers;
}

function textOf(message) {
  if (typeof message.content === "string") return message.content;
  return message.content.map((part) => part.text ?? "").join("\n");
}

test("discovers bundled skills", async () => {
  const handlers = await loadExtension();
  const result = await handlers.get("resources_discover")();
  assert.deepEqual(result.skillPaths, [resolve(root, "skills")]);
});

test("injects once at startup and stops after agent_end", async () => {
  const handlers = await loadExtension();
  const original = [{ role: "user", content: "Build a tiny feature", timestamp: 1 }];

  await handlers.get("session_start")();
  const injected = await handlers.get("context")({ messages: original });
  assert.equal(injected.messages.length, 2);
  assert.match(textOf(injected.messages[0]), /smolpowers:smol-activate bootstrap/);
  assert.equal(injected.messages[1], original[0]);
  assert.equal(await handlers.get("context")({ messages: injected.messages }), undefined);

  await handlers.get("agent_end")();
  assert.equal(await handlers.get("context")({ messages: original }), undefined);
});

test("reinjects after compaction without preceding the summary", async () => {
  const handlers = await loadExtension();
  const summary = { role: "compactionSummary", summary: "Earlier work", timestamp: 1 };
  const user = { role: "user", content: "Continue", timestamp: 2 };

  await handlers.get("session_compact")();
  const result = await handlers.get("context")({ messages: [summary, user] });
  assert.equal(result.messages[0], summary);
  assert.match(textOf(result.messages[1]), /smolpowers:smol-activate bootstrap/);
  assert.equal(result.messages[2], user);
});
