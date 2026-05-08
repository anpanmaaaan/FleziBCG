#!/usr/bin/env node
/**
 * i18n hardcode migration script.
 * For each .tsx page file, finds hardcoded user-facing strings and replaces them
 * with t() calls. Adds missing keys to en.ts and ja.ts registries.
 *
 * Three violation categories:
 *   A) JSX text literal          >Literal< (pattern: >[^<>{}\n\t][^<>{}]*<)
 *   B) toast.*('literal')
 *   C) title="literal"  (not already using t())
 */

import { readFileSync, writeFileSync, readdirSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");
const PAGES_DIR = join(ROOT, "src/app/pages");
const EN_PATH = join(ROOT, "src/app/i18n/registry/en.ts");
const JA_PATH = join(ROOT, "src/app/i18n/registry/ja.ts");

// ─── helpers ──────────────────────────────────────────────────────────────────

function slugify(text) {
  return text
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, "")
    .replace(/\s+/g, "_")
    .replace(/_+/g, "_")
    .substring(0, 40)
    .replace(/_$/, "");
}

function pagePrefix(filename) {
  // e.g. OperationList.tsx → operationList
  const base = filename.replace(/\.tsx$/, "");
  return base.charAt(0).toLowerCase() + base.slice(1);
}

/** Load registry file as { raw: string, keys: Map<key, value> } */
function loadRegistry(path) {
  const raw = readFileSync(path, "utf8");
  const keys = new Map();
  for (const m of raw.matchAll(/"([^"]+)":\s*"([^"\\]*)(?:\\.[^"\\]*)*/g)) {
    keys.set(m[1], m[2]);
  }
  return { raw, keys };
}

/** Insert a new key just before the closing `};` of a registry file */
function insertKey(raw, key, value) {
  // Don't insert duplicates
  if (raw.includes(`"${key}"`)) return raw;
  const insertBefore = raw.lastIndexOf("};");
  const line = `  "${key}": "${value.replace(/"/g, "'")}",\n`;
  return raw.slice(0, insertBefore) + line + raw.slice(insertBefore);
}

// ─── key registry for known/reusable strings ──────────────────────────────────

// Exact match table for very common strings → existing or canonical key
const EXACT_KEY_MAP = {
  "—": "common.na",
  "•": null, // decorative → aria-hidden, skip
  "N/A": "common.na",
  "Loading...": "common.loading",
  "Save": "common.action.save",
  "Cancel": "common.action.cancel",
  "Edit": "common.action.edit",
  "Delete": "common.action.delete",
  "Export": "common.action.export",
  "Search": "common.action.search",
  "Refresh": "common.action.refresh",
  "View": "common.action.view",
  "Close": "common.action.close",
  "Back": "common.action.back",
  "All": "common.filter.all",
  "Status": "common.status",
  "Required": "common.required",
  "Yes": "common.yes",
  "No": "common.no",
  "Progress": "common.progress",
};

// Common values also seen in title= and toast contexts
const KNOWN_KEYS = {
  "Backend required": "common.notice.backendRequired",
  "This action is not available for mock data": "common.notice.mockUnavailable",
  "This action requires backend IAM workflow": "common.notice.iamRequired",
  "Backend IAM workflow required": "common.notice.iamRequired",
  "This action requires backend session management": "common.notice.sessionRequired",
  "This action requires backend audit export": "common.notice.auditRequired",
  "Backend master data system manages hierarchy": "common.notice.hierarchyLocked",
  "Backend MMD governance workflow required": "common.notice.mmdRequired",
  "Backend supervisory workflow required": "common.notice.supervisoryRequired",
  "Backend WMS required": "common.notice.wmsRequired",
  "Resequence is not available for mock data": "common.notice.mockUnavailable",
  "Apply to Dispatch Queue feature coming soon": "common.notice.comingSoon",
  "Export feature coming soon": "common.notice.comingSoon",
  "Role creation requires backend workflow": "common.notice.iamRequired",
  "User creation requires backend IAM workflow": "common.notice.iamRequired",
  "Backend system manages tenant settings": "common.notice.tenantLocked",
  "Backend WMS required": "common.notice.wmsRequired",
};

// en values for common keys to add if not present
const COMMON_KEY_VALUES_EN = {
  "common.required": "Required",
  "common.notice.backendRequired": "Backend required",
  "common.notice.mockUnavailable": "This action is not available for mock data",
  "common.notice.iamRequired": "This action requires backend IAM workflow",
  "common.notice.sessionRequired": "This action requires backend session management",
  "common.notice.auditRequired": "This action requires backend audit export",
  "common.notice.hierarchyLocked": "Backend master data system manages hierarchy",
  "common.notice.mmdRequired": "Backend MMD governance workflow required",
  "common.notice.supervisoryRequired": "Backend supervisory workflow required",
  "common.notice.wmsRequired": "Backend WMS required",
  "common.notice.comingSoon": "Coming soon",
  "common.notice.tenantLocked": "Backend system manages tenant settings",
};

// ja values for the same keys
const COMMON_KEY_VALUES_JA = {
  "common.required": "必須",
  "common.notice.backendRequired": "バックエンドが必要です",
  "common.notice.mockUnavailable": "このアクションはモックデータでは使用できません",
  "common.notice.iamRequired": "このアクションにはバックエンドIAMワークフローが必要です",
  "common.notice.sessionRequired": "このアクションにはバックエンドのセッション管理が必要です",
  "common.notice.auditRequired": "このアクションにはバックエンドの監査エクスポートが必要です",
  "common.notice.hierarchyLocked": "バックエンドのマスターデータシステムが階層を管理します",
  "common.notice.mmdRequired": "バックエンドMMDガバナンスワークフローが必要です",
  "common.notice.supervisoryRequired": "バックエンドの管理ワークフローが必要です",
  "common.notice.wmsRequired": "バックエンドWMSが必要です",
  "common.notice.comingSoon": "近日公開予定",
  "common.notice.tenantLocked": "バックエンドシステムがテナント設定を管理します",
};

// ─── working state ─────────────────────────────────────────────────────────────

let enReg = loadRegistry(EN_PATH);
let jaReg = loadRegistry(JA_PATH);
const newEnKeys = new Map(); // key → en value
const newJaKeys = new Map(); // key → ja value (same value; JP fallback = EN for now)

function resolveKey(text, _prefix) {
  if (EXACT_KEY_MAP[text] !== undefined) return EXACT_KEY_MAP[text];
  if (KNOWN_KEYS[text]) return KNOWN_KEYS[text];
  return null; // generate later
}

function ensureKey(key, enValue, jaValue) {
  if (!enReg.keys.has(key) && !newEnKeys.has(key)) {
    newEnKeys.set(key, enValue);
    newJaKeys.set(key, jaValue ?? enValue);
  }
}

// Ensure all common.notice.* keys exist
for (const [k, v] of Object.entries(COMMON_KEY_VALUES_EN)) {
  ensureKey(k, v, COMMON_KEY_VALUES_JA[k] ?? v);
}
if (!enReg.keys.has("common.required")) {
  ensureKey("common.required", "Required", "必須");
}

// ─── per-file processing ───────────────────────────────────────────────────────

const files = readdirSync(PAGES_DIR).filter((f) => f.endsWith(".tsx"));

let fixedFiles = 0;
let fixedViolations = 0;

for (const filename of files) {
  const filepath = join(PAGES_DIR, filename);
  const prefix = pagePrefix(filename);
  let src = readFileSync(filepath, "utf8");
  let modified = false;
  const hasTImport = src.includes("useI18n");

  // ── Category B: toast.*('literal')
  src = src.replace(
    /toast\.([a-zA-Z]+)\(['"]([^'"\{\}\)\n]+)['"]\)/g,
    (match, method, text) => {
      const key = resolveKey(text, prefix);
      if (key === null) {
        // generate page-scoped key
        const slug = slugify(text);
        const generatedKey = `${prefix}.notice.${slug}`;
        ensureKey(generatedKey, text, text);
        modified = true;
        fixedViolations++;
        return `toast.${method}(t("${generatedKey}"))`;
      }
      if (key) {
        ensureKey(key, text, COMMON_KEY_VALUES_JA[key] ?? text);
        modified = true;
        fixedViolations++;
        return `toast.${method}(t("${key}"))`;
      }
      return match;
    }
  );

  // ── Category C: title="literal" (not already using t())
  // Only match title=".." that doesn't already contain {t(
  src = src.replace(
    /title="([^"{\n]+)"/g,
    (match, text) => {
      if (match.includes("t(")) return match;
      const key = resolveKey(text, prefix);
      if (key === null) {
        const slug = slugify(text);
        const generatedKey = `${prefix}.tooltip.${slug}`;
        ensureKey(generatedKey, text, text);
        modified = true;
        fixedViolations++;
        return `title={t("${generatedKey}")}`;
      }
      if (key) {
        ensureKey(key, text, COMMON_KEY_VALUES_JA[key] ?? text);
        modified = true;
        fixedViolations++;
        return `title={t("${key}")}`;
      }
      return match;
    }
  );

  // ── Category A: JSX text nodes — inline on any line
  // The lint pattern finds >LiteralText< anywhere in a line (not already using t())
  // We process line-by-line, but do an inline regex replace per-line.
  const lines = src.split("\n");
  const newLines = [];
  for (const line of lines) {
    // Skip lines that already use t()
    if (line.includes("t(") || line.includes("{t(")) {
      newLines.push(line);
      continue;
    }

    // Test whether this line contains a >literal< pattern
    if (!/>[^<>{}\n\t][^<>{}]*</.test(line)) {
      newLines.push(line);
      continue;
    }

    // Replace all >literal< occurrences in the line
    let newLine = line;
    newLine = newLine.replace(/>([^<>{}\n\t][^<>{}]*)</g, (match, rawText) => {
      const text = rawText.trim();
      // Skip empty, pure digits, or single non-special chars — but keep em-dash and hyphen
      if (!text) return match;
      if (text !== "—" && text !== "-" && text !== "•" && (text.length <= 1 || /^[\d.]+$/.test(text))) return match;

      // Decorative bullet -> aria-hidden approach handled differently (keep as-is, handled in span)
      if (text === "•") return match; // handled separately per-element

      if (text === "—" || text === "-") {
        modified = true;
        fixedViolations++;
        return `>{t("common.na")}<`;
      }

      const key = resolveKey(text, prefix);
      let resolvedKey = key;
      if (resolvedKey === null) {
        const slug = slugify(text);
        resolvedKey = `${prefix}.label.${slug}`;
        ensureKey(resolvedKey, text, text);
      } else if (resolvedKey) {
        ensureKey(resolvedKey, text, COMMON_KEY_VALUES_JA[resolvedKey] ?? text);
      } else {
        return match; // skip (null from EXACT_KEY_MAP means decorative/skip)
      }

      modified = true;
      fixedViolations++;
      // Preserve surrounding whitespace
      const leadingSpace = rawText.match(/^(\s*)/)?.[1] ?? "";
      const trailingSpace = rawText.match(/(\s*)$/)?.[1] ?? "";
      return `>${leadingSpace}{t("${resolvedKey}")}${trailingSpace}<`;
    });

    // Handle <span ...>•</span> → aria-hidden
    newLine = newLine.replace(/<span([^>]*)>•<\/span>/g, (_, attrs) => {
      modified = true;
      fixedViolations++;
      return `<span${attrs} aria-hidden="true">{String.fromCharCode(8226)}</span>`;
    });

    newLines.push(newLine);
  }
  src = newLines.join("\n");

  // If file was modified and doesn't already import useI18n, we need to ensure
  // t is available. Check if `const { t } = useI18n();` already exists.
  if (modified) {
    const hasT = src.includes("const { t }") || src.includes("const {t}");
    if (!hasT && hasTImport) {
      // Already imports useI18n but doesn't destructure t — patch
      src = src.replace(
        /const\s*\{([^}]+)\}\s*=\s*useI18n\(\)/,
        (m, inner) => {
          if (inner.includes("t")) return m;
          return `const { t, ${inner.trim()} } = useI18n()`;
        }
      );
    } else if (!hasT && !hasTImport) {
      // Need to add import and usage. Find the first function component and add `const { t } = useI18n();`
      // First add import
      const importLine = `import { useI18n } from "@/app/i18n";\n`;
      if (!src.includes(`from "@/app/i18n"`)) {
        // Insert after the last import line
        const lastImportIdx = src.lastIndexOf("\nimport ");
        const endOfLastImport = src.indexOf("\n", lastImportIdx + 1);
        src = src.slice(0, endOfLastImport + 1) + importLine + src.slice(endOfLastImport + 1);
      }
      // Find the export function body and insert `const { t } = useI18n();`
      src = src.replace(
        /(export function [A-Z][a-zA-Z]+\([^)]*\)\s*\{)/,
        (m) => `${m}\n  const { t } = useI18n();`
      );
    }
    writeFileSync(filepath, src, "utf8");
    fixedFiles++;
    console.log(`  fixed: ${filename} (modified)`);
  }
}

// ─── write registries ──────────────────────────────────────────────────────────

if (newEnKeys.size > 0) {
  console.log(`\nAdding ${newEnKeys.size} new keys to registries...`);
  let enRaw = enReg.raw;
  let jaRaw = readFileSync(JA_PATH, "utf8");

  for (const [k, v] of newEnKeys) {
    enRaw = insertKey(enRaw, k, v);
    jaRaw = insertKey(jaRaw, k, newJaKeys.get(k) ?? v);
  }

  writeFileSync(EN_PATH, enRaw, "utf8");
  writeFileSync(JA_PATH, jaRaw, "utf8");
  console.log("  en.ts and ja.ts updated.");
}

console.log(`\nDone. Fixed ${fixedViolations} violations in ${fixedFiles} files.`);
