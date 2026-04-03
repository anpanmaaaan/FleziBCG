import type { I18nNamespace } from "./namespaces";

export type I18nSemanticKey = `${I18nNamespace}.${string}`;

export type I18nRegistry = Record<I18nSemanticKey, string>;

// TODO(Phase 5B): Add lint/check tooling to prevent non-semantic text keys.
