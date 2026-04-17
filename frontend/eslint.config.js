import tseslint from "typescript-eslint";

export default tseslint.config(
  ...tseslint.configs.recommended,
  {
    files: ["src/**/*.{ts,tsx}"],
    languageOptions: {
      parserOptions: {
        ecmaFeatures: { jsx: true },
      },
    },
    linterOptions: {
      reportUnusedDisableDirectives: false,
    },
    rules: {
      // Disable rules that conflict with the codebase style
      "@typescript-eslint/no-unused-vars": "off",
      "@typescript-eslint/no-explicit-any": "off",
      "@typescript-eslint/no-empty-object-type": "off",
      "prefer-const": "off",

      // Enforce @/ alias for cross-module imports
      "no-restricted-imports": [
        "error",
        {
          patterns: [
            {
              group: ["../**/auth/*"],
              message: "Use @/app/auth barrel instead.",
            },
            {
              group: ["../**/api/*"],
              message: "Use @/app/api barrel instead.",
            },
            {
              group: ["../**/impersonation/*"],
              message: "Use @/app/impersonation barrel instead.",
            },
            {
              group: ["../**/persona/*"],
              message: "Use @/app/persona barrel instead.",
            },
            {
              group: ["../**/components/[A-Z]*"],
              message: "Use @/app/components barrel instead.",
            },
            {
              group: ["../**/data/*"],
              message: "Use @/app/data/<file> with @/ alias instead.",
            },
            {
              group: ["../**/i18n", "../**/i18n/*"],
              message: "Use @/app/i18n instead.",
            },
          ],
        },
      ],

      // Warn on hardcoded hex color literals — prefer theme tokens
      "no-restricted-syntax": [
        "warn",
        {
          selector:
            "Literal[value=/^#[0-9a-fA-F]{3,8}$/]",
          message:
            "Avoid hardcoded hex colors. Use a CSS variable / theme token instead.",
        },
      ],
    },
  },
);
