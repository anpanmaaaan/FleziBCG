import { readdirSync, readFileSync, statSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, "..");
const PAGES_DIR = path.join(ROOT, "src", "app", "pages");

const PATTERNS = [
  {
    label: "JSX text node with literal",
    regex: />([^<>{}\n\t][^<>{}\n\t]*)</g,
  },
  {
    label: "toast.* with literal",
    regex: /toast\.[a-zA-Z]+\(["'][^{}\)\n]*["']\)/g,
  },
  {
    label: "confirm() with literal",
    regex: /confirm\(["'][^{}\)\n]*["']\)/g,
  },
  {
    label: "title attribute literal",
    regex: /title=["'][^{}\)\n]*["']/g,
  },
];

function walkFiles(dirPath, collected = []) {
  const entries = readdirSync(dirPath);
  for (const name of entries) {
    const fullPath = path.join(dirPath, name);
    const info = statSync(fullPath);
    if (info.isDirectory()) {
      walkFiles(fullPath, collected);
      continue;
    }
    if (fullPath.endsWith(".tsx") || fullPath.endsWith(".ts")) {
      collected.push(fullPath);
    }
  }
  return collected;
}

function lineNumberFromIndex(source, index) {
  let line = 1;
  for (let i = 0; i < index; i += 1) {
    if (source[i] === "\n") {
      line += 1;
    }
  }
  return line;
}

let fail = 0;
const files = walkFiles(PAGES_DIR);

for (const filePath of files) {
  const source = readFileSync(filePath, "utf8");
  for (const { label, regex } of PATTERNS) {
    regex.lastIndex = 0;
    let match = regex.exec(source);
    while (match) {
      const snippet = match[0];
      const captured = typeof match[1] === "string" ? match[1].trim() : "";
      const hasTextContent =
        label !== "JSX text node with literal" ||
        (captured.length > 0 && /[\p{L}\p{N}]/u.test(captured));

      if (hasTextContent && !snippet.includes("t(")) {
        const line = lineNumberFromIndex(source, match.index);
        const rel = path.relative(ROOT, filePath).replace(/\\/g, "/");
        console.error(`[i18n-lint] ${label}: ${rel}:${line} :: ${snippet}`);
        fail = 1;
      }
      match = regex.exec(source);
    }
  }
}

if (fail) {
  console.error("[i18n-lint] FAIL: Hardcoded UI strings found. Use useI18n().t(key) for user-facing text.");
  process.exit(1);
}

console.log("[i18n-lint] PASS: No hardcoded UI strings detected.");