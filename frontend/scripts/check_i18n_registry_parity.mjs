import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const registryFiles = {
  en: path.resolve(__dirname, "../src/app/i18n/registry/en.ts"),
  ja: path.resolve(__dirname, "../src/app/i18n/registry/ja.ts"),
};

function extractKeys(filePath) {
  const source = readFileSync(filePath, "utf8");
  const keyRegex = /^\s*"([^"]+)"\s*:/gm;
  const keys = [];

  for (const match of source.matchAll(keyRegex)) {
    keys.push(match[1]);
  }

  const counts = new Map();
  for (const key of keys) {
    counts.set(key, (counts.get(key) ?? 0) + 1);
  }

  const duplicates = [...counts.entries()]
    .filter(([, count]) => count > 1)
    .map(([key]) => key)
    .sort();

  return {
    keys: new Set(keys),
    duplicates,
  };
}

function difference(left, right) {
  return [...left].filter((key) => !right.has(key)).sort();
}

const en = extractKeys(registryFiles.en);
const ja = extractKeys(registryFiles.ja);

const missingInEn = difference(ja.keys, en.keys);
const missingInJa = difference(en.keys, ja.keys);

let hasFailure = false;

if (en.duplicates.length > 0) {
  hasFailure = true;
  console.error("[i18n-registry] Duplicate keys in en.ts:");
  for (const key of en.duplicates) {
    console.error(`  - ${key}`);
  }
}

if (ja.duplicates.length > 0) {
  hasFailure = true;
  console.error("[i18n-registry] Duplicate keys in ja.ts:");
  for (const key of ja.duplicates) {
    console.error(`  - ${key}`);
  }
}

if (missingInEn.length > 0) {
  hasFailure = true;
  console.error("[i18n-registry] Keys present in ja.ts but missing in en.ts:");
  for (const key of missingInEn) {
    console.error(`  - ${key}`);
  }
}

if (missingInJa.length > 0) {
  hasFailure = true;
  console.error("[i18n-registry] Keys present in en.ts but missing in ja.ts:");
  for (const key of missingInJa) {
    console.error(`  - ${key}`);
  }
}

if (hasFailure) {
  process.exit(1);
}

console.log(`[i18n-registry] PASS: en.ts and ja.ts are key-synchronized (${en.keys.size} keys).`);