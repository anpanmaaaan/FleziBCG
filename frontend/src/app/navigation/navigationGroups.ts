/**
 * navigationGroups.ts — FE-NAV-01
 *
 * Defines MOM domain groups for the collapsible sidebar navigation.
 *
 * IMPORTANT: This file is a PRESENTATION-LAYER grouping utility only.
 * It does NOT change route definitions, authorization rules, or persona semantics.
 * All auth/permission truth remains in personaLanding.ts and the backend.
 *
 * Future/to-be/shell screens are placed in their real domain group, not a catch-all.
 */

export interface NavGroup {
  id: string;
  label: string;
  /** Route path prefixes that belong to this group. Order matters — more specific first. */
  routePrefixes: string[];
}

export interface GroupedMenuItem {
  label: string;
  to: string;
}

export interface GroupedMenuSection {
  group: NavGroup;
  items: GroupedMenuItem[];
}

/**
 * MOM domain groups in display order.
 * Each group owns a set of route path prefixes.
 * The matching algorithm uses prefix matching (exact or startsWith after '/').
 *
 * Future/shell screens must stay inside their real domain group.
 * Do NOT add a "Future" or "To-Be" catch-all group.
 */
export const NAV_GROUPS: NavGroup[] = [
  {
    id: "home",
    label: "Home / Dashboard",
    routePrefixes: ["/home", "/dashboard"],
  },
  {
    id: "core-operations",
    label: "Core Operations",
    routePrefixes: [
      "/production-orders",
      // Work orders before /work-orders prefix to catch nested patterns
      "/work-orders",
      "/operations",
      "/dispatch",
      // Execution shells — belong here (they will become execution flows)
      "/station-session",
      "/station-execution",
      "/station",
      "/operator-identification",
      "/equipment-binding",
      "/line-monitor",
      "/station-monitor",
      "/shift-summary",
      "/supervisory",
    ],
  },
  {
    id: "mfg-master-data",
    label: "Mfg Master Data",
    routePrefixes: [
      "/products",
      "/routes",
      "/bom",
      "/resource-requirements",
      "/reason-codes",
    ],
  },
  {
    id: "quality",
    label: "Quality",
    routePrefixes: [
      // More-specific quality sub-routes first
      "/quality-dashboard",
      "/quality-measurements",
      "/quality-holds",
      "/quality",
      "/defects",
    ],
  },
  {
    id: "material-wip",
    label: "Material / WIP",
    routePrefixes: [
      "/material-readiness",
      "/staging-kitting",
      "/wip-buffers",
    ],
  },
  {
    id: "traceability",
    label: "Traceability",
    routePrefixes: ["/traceability"],
  },
  {
    id: "reporting-analytics",
    label: "Reporting & Analytics",
    routePrefixes: [
      "/performance",
      "/downtime-analysis",
    ],
  },
  {
    id: "planning-scheduling",
    label: "Planning & Scheduling",
    routePrefixes: ["/scheduling"],
  },
  {
    id: "governance-admin",
    label: "Governance & Admin",
    routePrefixes: [
      "/users",
      "/roles",
      "/action-registry",
      "/scope-assignments",
      "/sessions",
      "/audit-log",
      "/security-events",
      "/tenant-settings",
      "/plant-hierarchy",
      "/settings",
    ],
  },
];

/**
 * Returns the group id whose routePrefixes match the given pathname, or null.
 * Strips query string before matching.
 */
export function getGroupIdForPath(pathname: string): string | null {
  const cleanPath = pathname.split("?")[0];
  for (const group of NAV_GROUPS) {
    for (const prefix of group.routePrefixes) {
      if (cleanPath === prefix || cleanPath.startsWith(`${prefix}/`)) {
        return group.id;
      }
    }
  }
  return null;
}

/**
 * Groups a flat array of menu items into domain sections.
 * Preserves the order of NAV_GROUPS; items not matching any group
 * are collected in a trailing "_other" section.
 *
 * Does NOT modify personaLanding item visibility — this is display only.
 */
export function groupMenuItems(
  items: ReadonlyArray<{ label: string; to: string }>
): GroupedMenuSection[] {
  const buckets = new Map<string, GroupedMenuItem[]>();

  for (const item of items) {
    const cleanPath = item.to.split("?")[0];
    let matched = false;
    for (const group of NAV_GROUPS) {
      for (const prefix of group.routePrefixes) {
        if (cleanPath === prefix || cleanPath.startsWith(`${prefix}/`)) {
          if (!buckets.has(group.id)) buckets.set(group.id, []);
          buckets.get(group.id)!.push({ label: item.label, to: item.to });
          matched = true;
          break;
        }
      }
      if (matched) break;
    }
    if (!matched) {
      if (!buckets.has("_other")) buckets.set("_other", []);
      buckets.get("_other")!.push({ label: item.label, to: item.to });
    }
  }

  const result: GroupedMenuSection[] = [];
  for (const group of NAV_GROUPS) {
    const sectionItems = buckets.get(group.id);
    if (sectionItems?.length) {
      result.push({ group, items: sectionItems });
    }
  }

  const others = buckets.get("_other");
  if (others?.length) {
    result.push({
      group: { id: "_other", label: "Other", routePrefixes: [] },
      items: others,
    });
  }

  return result;
}

/**
 * Filters grouped menu sections to only those matching the search query.
 *
 * Matching logic:
 *   - Item label contains query (case-insensitive)
 *   - Item route path contains query (case-insensitive)
 *   - Group label contains query — all items in that group are included
 *
 * Returns only groups that have at least one matching item.
 * Groups with no matches are omitted entirely.
 *
 * IMPORTANT: This is a DISPLAY-ONLY filter. It does not change persona
 * permissions, route guards, or authorization behavior. It operates only
 * on items already returned by getMenuItemsForPersona().
 */
export function filterNavigationGroups(
  sections: GroupedMenuSection[],
  query: string
): GroupedMenuSection[] {
  const q = query.trim().toLowerCase();
  if (!q) return sections;

  return sections.reduce<GroupedMenuSection[]>((acc, section) => {
    const groupMatches = section.group.label.toLowerCase().includes(q);
    const filteredItems = groupMatches
      ? section.items
      : section.items.filter(
          (item) =>
            item.label.toLowerCase().includes(q) ||
            item.to.toLowerCase().includes(q)
        );
    if (filteredItems.length > 0) {
      acc.push({ group: section.group, items: filteredItems });
    }
    return acc;
  }, []);
}
