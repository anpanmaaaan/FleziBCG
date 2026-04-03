export const I18N_NAMESPACES = {
  common: "common",
  execution: "execution",
  operations: "operations",
  dashboard: "dashboard",
  quality: "quality",
  persona: "persona",
  navigation: "navigation",
} as const;

export type I18nNamespace = (typeof I18N_NAMESPACES)[keyof typeof I18N_NAMESPACES];

// TODO(Phase 5B): Introduce runtime namespace loading strategy.
