import { useContext } from "react";
import { I18nContext } from "./I18nContext";

export type SupportedLocale = "en" | "ja";

export interface I18nHook {
  /**
   * Translate a semantic key.
   * Overloads:
   *   t(key)                       — lookup only
   *   t(key, fallback)             — lookup with fallback string (backward-compat)
   *   t(key, vars)                 — lookup with interpolation vars
   *   t(key, vars, fallback)       — lookup with vars + fallback
   */
  t: {
    (key: I18nSemanticKey): string;
    (key: I18nSemanticKey, fallback: string): string;
    (key: I18nSemanticKey, vars: Record<string, string | number>): string;
    (key: I18nSemanticKey, vars: Record<string, string | number>, fallback: string): string;
  };
  locale: SupportedLocale;
  setLocale: (locale: SupportedLocale) => void;
}

import type { I18nSemanticKey } from "./keys";

/**
 * i18n hook — consumes shared I18nContext.
 * Wrap your app in <I18nProvider> for locale to propagate globally.
 */
export function useI18n(): I18nHook {
  const ctx = useContext(I18nContext);
  if (!ctx) {
    throw new Error("useI18n must be used within <I18nProvider>");
  }
  return ctx;
}
