/**
 * SidebarSearch.tsx — FE-NAV-01B
 *
 * Lightweight search/filter input for the sidebar navigation.
 * Filters persona-visible nav items by label, route path, or group label.
 *
 * SAFETY: This component only filters items already returned by
 * getMenuItemsForPersona(). It does NOT expose routes outside the current
 * persona's menu, and it is NOT authorization truth.
 */
import { Search, X } from "lucide-react";
import { useId } from "react";

interface SidebarSearchProps {
  value: string;
  onChange: (value: string) => void;
  placeholder: string;
  ariaLabel: string;
  clearLabel: string;
}

export function SidebarSearch({
  value,
  onChange,
  placeholder,
  ariaLabel,
  clearLabel,
}: SidebarSearchProps) {
  const inputId = useId();

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Escape" && value) {
      e.preventDefault();
      onChange("");
    }
  }

  return (
    <div className="relative mx-3 mb-2 mt-1">
      <label htmlFor={inputId} className="sr-only">
        {ariaLabel}
      </label>
      <Search className="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-400" />
      <input
        id={inputId}
        type="search"
        autoComplete="off"
        spellCheck={false}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        className="w-full rounded-lg border border-slate-200 bg-slate-50 py-2 pl-8 pr-7 text-sm text-slate-800 placeholder:text-slate-400 focus:border-blue-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-100"
      />
      {value && (
        <button
          type="button"
          title={clearLabel}
          aria-label={clearLabel}
          onClick={() => onChange("")}
          className="absolute right-2 top-1/2 -translate-y-1/2 rounded p-0.5 text-slate-400 hover:text-slate-600 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-blue-500"
        >
          <X className="h-3.5 w-3.5" />
        </button>
      )}
    </div>
  );
}
