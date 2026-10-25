#!/usr/bin/env node
// Image generation adapter — the only script that touches the network.
// Gemini (default, reference images inline) or OpenAI gpt-image-1 (multipart
// images/edits). Node 18+ or Bun, stdlib only.
//
//   generate.mjs --out shots/s01.png --prompt-file prompts/s01.txt \
//                --ref characters/klik/reference.png [--engine auto] [--size 1024x1024]
//
// Writes <out>.meta.json {engine, model, ms} for the cost tally.
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { spawn } from "node:child_process";

function arg(name, fallback) {
  const i = process.argv.indexOf(`--${name}`);
  if (i === -1) return fallback;
  if (process.argv[i + 1] === undefined || process.argv[i + 1].startsWith("--")) return true;
  return process.argv[i + 1];
}

const out = arg("out");
const promptFile = arg("prompt-file");
const refs = process.argv.flatMap((a, i) => (a === "--ref" ? [process.argv[i + 1]] : []));
const size = arg("size", "1024x1024");
let engine = arg("engine", "auto");
if (!out || !promptFile) die("usage: --out FILE --prompt-file FILE [--ref PNG] [--engine auto|codex|gemini|openai] [--size WxH]");

const prompt = fs.readFileSync(promptFile, "utf8");
if (engine === "auto") {
  engine = hasCodex() ? "codex"
         : hasGrok() ? "grok"
         : process.env.GEMINI_API_KEY ? "gemini"
         : process.env.OPENROUTER_API_KEY ? "openrouter"
         : process.env.OPENAI_API_KEY ? "openai" : null;
  if (!engine) die("no subscription CLI (pi codex login, grok login) and no GEMINI_API_KEY / OPENROUTER_API_KEY / OPENAI_API_KEY");
}

function die(msg) { console.error(`generate: ${msg}`); process.exit(1); }
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function hasCodex() {
  try {
    const auth = JSON.parse(fs.readFileSync(path.join(process.env.HOME, ".pi/agent/auth.json"), "utf8"));
    return Boolean(auth["openai-codex"] || JSON.stringify(auth).includes("openai-codex"));
  } catch { return false; }
}

// Engine "codex": drive a non-interactive pi session to call its active
// `imagegen` tool (gpt-image-2.5 via the user's OpenAI Codex login — no API
// key). The tool saves into <workspace>/.pi/openai-codex-images/ (workspace =
// nearest .git parent of cwd); we pick the newest file written by this call.
function workspaceRoot() {
  let cur = path.resolve(process.cwd());
  for (;;) {
    if (fs.existsSync(path.join(cur, ".git"))) return cur;
    const parent = path.resolve(cur, "..");
    if (parent === cur) return path.resolve(process.cwd());
    cur = parent;
  }
}

function newestImage(dir, afterMs) {
  let best = null, bestM = 0;
  for (const f of fs.readdirSync(dir)) {
    if (!/\.(png|jpe?g|webp)$/i.test(f)) continue;
    const m = fs.statSync(path.join(dir, f)).mtimeMs;
    if (m > afterMs && m > bestM) { best = path.join(dir, f); bestM = m; }
  }
  return best;
}

async function codex(outPath) {
  const [w, h] = size.split("x").map(Number);
  const aspect = w > h ? "wide 3:2 landscape" : h > w ? "tall 2:3 portrait" : "square 1:1";
  const imagegenPrompt = `${prompt}\n\nAspect ratio: ${aspect}. Quality: high.`;
  const params = [
    `prompt: ${JSON.stringify(imagegenPrompt)}`,
    refs.length ? `referenced_image_paths: ${JSON.stringify(refs.map((r) => path.resolve(r)))}` : null,
  ].filter(Boolean).join("\n");
  const msg = `Call the imagegen tool exactly once with exactly these parameters:\n${params}\nDo not reply with text instead of an image. Do not call any other tool.`;
  const outDir = path.join(workspaceRoot(), ".pi", "openai-codex-images");
  const t0 = Date.now();
  let outLog = "";
  await new Promise((resolve, reject) => {
    const child = spawn("pi", ["-p", "--mode", "text", msg],
                        { stdio: ["inherit", "pipe", "pipe"] });
    const timer = setTimeout(() => child.kill("SIGKILL"), 300_000);
    child.stdout.on("data", (d) => { outLog += d; });
    child.stderr.on("data", (d) => { outLog += d; });
    child.on("error", (e) => { clearTimeout(timer); reject(e); });
    child.on("close", (code) => {
      clearTimeout(timer);
      if (code === 0) return resolve();
      reject(new Error(`pi exited ${code}: ${outLog.slice(-300)}`));
    });
  });
  if (!fs.existsSync(outDir)) {
    throw new Error(`codex: no output dir ${outDir}. pi said: ${outLog.slice(-300)}`);
  }
  const saved = newestImage(outDir, t0);
  if (!saved) {
    throw new Error(`codex: pi session finished but saved no image. pi said: ${outLog.slice(-400)}`);
  }
  if (/\.png$/i.test(saved)) {
    fs.copyFileSync(saved, outPath);
  } else {
    // Convert with macOS's built-in sips so the pipeline stays dependency-free.
    await new Promise((resolve, reject) => {
      const c = spawn("sips", ["-s", "format", "png", saved, "--out", path.resolve(outPath)],
                      { stdio: ["ignore", "ignore", "pipe"] });
      let e = "";
      c.stderr.on("data", (d) => { e += d; });
      c.on("error", reject);
      c.on("close", (code) => code === 0 ? resolve() : reject(new Error(`sips: ${e.slice(-200)}`)));
    });
  }
  return { ms: Date.now() - t0 };
}

function grokHome() {
  return process.env.GROK_HOME || path.join(os.homedir(), ".grok");
}

function hasGrok() {
  try {
    return fs.existsSync(path.join(grokHome(), "auth.json"));
  } catch { return false; }
}

function newestImageRecursive(dir, afterMs) {
  let best = null, bestM = 0;
  const walk = (d) => {
    for (const f of fs.readdirSync(d, { withFileTypes: true })) {
      const full = path.join(d, f.name);
      if (f.isDirectory()) { walk(full); continue; }
      if (!/\.(png|jpe?g|webp)$/i.test(f.name)) continue;
      const m = fs.statSync(full).mtimeMs;
      if (m > afterMs && m > bestM) { best = full; bestM = m; }
    }
  };
  try { walk(dir); } catch { /* unreadable tree counts as no image */ }
  return best;
}

// Engine "grok": drive the user's Grok (xAI) CLI headless single-turn mode
// (`grok -p`) to reach its built-in image_gen/image_edit tools — free for Grok
// subscribers, no API key, same design as illo's grok backend. Grok reads
// reference images by path inside the prompt text (there is no -i flag), and
// returns JPEG (no alpha). Sandbox confines writes to cwd/tmp/~/.grok.
async function grok(outPath) {
  const outAbs = path.resolve(outPath);
  const runDir = path.dirname(outAbs);
  fs.mkdirSync(runDir, { recursive: true });
  const toolLine = refs.length
    ? `Use your image_edit tool with the reference image(s) at ${refs.map((r) => path.resolve(r)).join(", ")} to keep the character on-model, then render`
    : "Use your image_gen tool to render";
  const single = `${prompt}\n\n${toolLine} this illustration and save the resulting image to ${outAbs} (overwrite if it exists). Do not construct the image with code (HTML/SVG/Python) — use the image generation tool. Do not ask for confirmation.`;
  fs.rmSync(outAbs, { force: true });
  const t0 = Date.now();
  let log = "";
  await new Promise((resolve, reject) => {
    const child = spawn("grok", ["-p", single, "--always-approve",
                                 "--sandbox", "workspace", "--cwd", runDir],
                        { stdio: ["inherit", "pipe", "pipe"] });
    const timer = setTimeout(() => child.kill("SIGKILL"), 600_000);
    child.stdout.on("data", (d) => { log += d; });
    child.stderr.on("data", (d) => { log += d; });
    child.on("error", (e) => { clearTimeout(timer); reject(new Error(`grok could not run: ${e.message}`)); });
    child.on("close", (code) => {
      clearTimeout(timer);
      if (code === 0) return resolve();
      reject(new Error(`grok exited ${code}: ${log.slice(-300)}`));
    });
  });
  let saved = fs.existsSync(outAbs) && fs.statSync(outAbs).size > 0 ? outAbs : null;
  if (!saved) saved = newestImageRecursive(path.join(grokHome(), "sessions"), t0);
  if (!saved) throw new Error(`grok produced no retrievable image. grok said: ${log.slice(-300)}`);
  if (path.resolve(saved) === outAbs) return { ms: Date.now() - t0, saved };
  if (/\.png$/i.test(saved)) {
    fs.copyFileSync(saved, outAbs);
  } else {
    // Grok returns JPEG; convert with macOS's built-in sips.
    await new Promise((resolve, reject) => {
      const c = spawn("sips", ["-s", "format", "png", saved, "--out", outAbs],
                      { stdio: ["ignore", "ignore", "pipe"] });
      let e = "";
      c.stderr.on("data", (d) => { e += d; });
      c.on("error", reject);
      c.on("close", (code) => code === 0 ? resolve() : reject(new Error(`sips: ${e.slice(-200)}`)));
    });
  }
  return { ms: Date.now() - t0, saved };
}

// OpenRouter: OpenAI-compatible chat completions with image output. One key,
// many image models — the catch-all engine when no subscription is available.
async function openrouter() {
  const key = process.env.OPENROUTER_API_KEY;
  const model = process.env.OPENROUTER_IMAGE_MODEL || "google/gemini-2.5-flash-image";
  const content = [{ type: "text", text: prompt }];
  for (const ref of refs) {
    content.push({
      type: "image_url",
      image_url: { url: `data:image/png;base64,${fs.readFileSync(ref).toString("base64")}` },
    });
  }
  const res = await withRetry(() =>
    fetch("https://openrouter.ai/api/v1/chat/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${key}`,
        "Content-Type": "application/json",
        "HTTP-Referer": "https://sketsa.dev",
        "X-Title": "Sketsa",
      },
      body: JSON.stringify({ model, modalities: ["image", "text"], messages: [{ role: "user", content }] }),
    }));
  if (!res.ok) die(`openrouter ${res.status}: ${JSON.stringify(await res.json()).slice(0, 300)}`);
  const body = await res.json();
  const images = body.choices?.[0]?.message?.images;
  if (!images?.length) die(`openrouter returned no image: ${JSON.stringify(body).slice(0, 300)}`);
  const url = images[0].image_url.url;
  return Buffer.from(url.slice(url.indexOf(";base64,") + 8), "base64");
}

async function withRetry(fn) {
  let last;
  for (let attempt = 0; attempt < 3; attempt++) {
    try { return await fn(); }
    catch (e) {
      last = e;
      const retry = e.status === 429 || e.status >= 500;
      if (!retry) throw e;
      await sleep(2000 * 2 ** attempt);
    }
  }
  throw last;
}

async function gemini() {
  const key = process.env.GEMINI_API_KEY;
  const model = process.env.GEMINI_IMAGE_MODEL || "gemini-2.5-flash-image";
  const parts = [{ text: prompt }];
  for (const ref of refs) {
    parts.push({
      inline_data: {
        mime_type: "image/png",
        data: fs.readFileSync(ref).toString("base64"),
      },
    });
  }
  const res = await withRetry(() =>
    fetch(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${key}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [{ parts }],
        generationConfig: { responseModalities: ["IMAGE"] },
      }),
    }));
  if (!res.ok) die(`gemini ${res.status}: (await res.text())`.slice(0, 300));
  const body = await res.json();
  const img = (body.candidates?.[0]?.content?.parts || [])
    .find((p) => p.inlineData || p.inline_data);
  if (!img) die(`gemini returned no image: ${JSON.stringify(body).slice(0, 300)}`);
  const b64 = img.inlineData?.data || img.inline_data?.data;
  return Buffer.from(b64, "base64");
}

async function openai() {
  const key = process.env.OPENAI_API_KEY;
  const model = process.env.OPENAI_IMAGE_MODEL || "gpt-image-1";
  const [w, h] = size.split("x").map(Number);
  const aspect = w > h ? "1536x1024" : h > w ? "1024x1536" : "1024x1024";
  const form = new FormData();
  form.append("model", model);
  form.append("prompt", prompt);
  form.append("size", aspect);
  refs.forEach((ref, i) => {
    form.append("image[]", new Blob([fs.readFileSync(ref)], { type: "image/png" }), `ref${i}.png`);
  });
  const res = await withRetry(() =>
    fetch("https://api.openai.com/v1/images/edits", {
      method: "POST",
      headers: { Authorization: `Bearer ${key}` },
      body: form,
    }));
  if (!res.ok) die(`openai ${res.status}: ${JSON.stringify(await res.json()).slice(0, 300)}`);
  const body = await res.json();
  const b64 = body.data?.[0]?.b64_json;
  if (!b64) die(`openai returned no image`);
  return Buffer.from(b64, "base64");
}

const t0 = Date.now();
let meta;
if (engine === "grok") {
  const r = await grok(out);
  meta = { engine, model: "grok image_gen/image_edit (grok CLI subscription)", refs: refs.length, ms: r.ms };
} else if (engine === "codex") {
  // The codex backend sometimes refuses silently; retry the pi session.
  let r, last;
  for (let attempt = 0; attempt < 3; attempt++) {
    try { r = await codex(out); last = null; break; }
    catch (e) {
      last = e;
      if (!/saved no image|pi exited/.test(e.message)) throw e;
      await sleep(5000);
    }
  }
  if (last) throw last;
  meta = { engine, model: "gpt-image-2.5 (codex backend)", refs: refs.length, ms: r.ms };
} else {
  const png = engine === "gemini" ? await gemini()
            : engine === "openrouter" ? await openrouter()
            : await openai();
  fs.writeFileSync(out, png);
  meta = {
    engine,
    model: engine === "gemini" ? (process.env.GEMINI_IMAGE_MODEL || "gemini-2.5-flash-image")
         : engine === "openrouter" ? (process.env.OPENROUTER_IMAGE_MODEL || "google/gemini-2.5-flash-image")
         : (process.env.OPENAI_IMAGE_MODEL || "gpt-image-1"),
    refs: refs.length,
    ms: Date.now() - t0,
  };
}
fs.writeFileSync(`${out}.meta.json`, JSON.stringify(meta, null, 1));
console.log(`wrote ${out} (${engine}, ${((Date.now() - t0) / 1000).toFixed(1)}s)`);
