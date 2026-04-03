import { enRegistry } from "./registry/en";
import type { I18nSemanticKey } from "./keys";

export interface I18nHook {
  t: (key: I18nSemanticKey, fallback?: string) => string;
  locale: "en";
}

// Phase 5A stub: deterministic EN lookup without runtime language behavior.
export function useI18n(): I18nHook {
  const t = (key: I18nSemanticKey, fallback?: string): string => {
    return enRegistry[key] ?? fallback ?? key;
  };

  return {
    t,
    locale: "en",
  };
}

// TODO(Phase 5B): Source locale from user/tenant preference.
// TODO(Phase 5B): Wire runtime language switching and interpolation.
