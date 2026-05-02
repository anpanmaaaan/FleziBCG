/**
 * MMD-FULLSTACK-05: MMD Read Integration Regression Check
 *
 * Static source-code invariant checks that lock the MMD read integration
 * baseline after MMD-FULLSTACK-01 through 04 and MMD-READ-BASELINE-01.
 *
 * Guards against:
 * - Removing extended fields from routing API type
 * - Reintroducing rejected fields (required_skill, qc_checkpoint_count, etc.)
 * - Reverting Routing Operation Detail to shell/mock
 * - Removing the context link to Resource Requirements
 * - Reverting Resource Requirements to shell/mock
 * - Removing query-param scope filtering from Resource Requirements
 * - Regressing screen status from PARTIAL/BACKEND_API to SHELL/MOCK
 * - Removing MMD routes from route registry
 * - Dropping i18n keys added by MMD-FULLSTACK-04
 *
 * Usage: node scripts/mmd-read-integration-regression-check.mjs
 * Exit 0 = all PASS; Exit 1 = one or more FAIL; Exit 2 = ABORT (file not found)
 */

import fs from "node:fs/promises";
import path from "node:path";

const FRONTEND_ROOT = process.cwd();
const SRC = path.join(FRONTEND_ROOT, "src");
const PREFIX = "[MMD READ REGRESSION]";

const results = [];

function pass(name) {
  results.push({ name, status: "PASS" });
  console.log(`${PREFIX} PASS ${name}`);
}

function fail(name, reason) {
  results.push({ name, status: "FAIL", reason });
  console.error(`${PREFIX} FAIL ${name}: ${reason}`);
}

async function readSource(relPath) {
  const fullPath = path.join(SRC, relPath);
  try {
    return await fs.readFile(fullPath, "utf8");
  } catch {
    return null;
  }
}

function abort(msg) {
  console.error(`${PREFIX} ABORT: ${msg}`);
  process.exit(2);
}

// ─── Load source files ────────────────────────────────────────────────────────

const routingApi      = await readSource("app/api/routingApi.ts");
const rodPage         = await readSource("app/pages/RoutingOperationDetail.tsx");
const rrPage          = await readSource("app/pages/ResourceRequirements.tsx");
const screenStatus    = await readSource("app/screenStatus.ts");
const routesTsx       = await readSource("app/routes.tsx");
const i18nEn          = await readSource("app/i18n/registry/en.ts");
const i18nJa          = await readSource("app/i18n/registry/ja.ts");
const productApi      = await readSource("app/api/productApi.ts");
const productDetail   = await readSource("app/pages/ProductDetail.tsx");
const bomList         = await readSource("app/pages/BomList.tsx");
const bomDetail       = await readSource("app/pages/BomDetail.tsx");

if (!routingApi)   abort("src/app/api/routingApi.ts not found");
if (!rodPage)      abort("src/app/pages/RoutingOperationDetail.tsx not found");
if (!rrPage)       abort("src/app/pages/ResourceRequirements.tsx not found");
if (!screenStatus) abort("src/app/screenStatus.ts not found");
if (!routesTsx)    abort("src/app/routes.tsx not found");
if (!i18nEn)       abort("src/app/i18n/registry/en.ts not found");
if (!i18nJa)       abort("src/app/i18n/registry/ja.ts not found");
if (!productApi)   abort("src/app/api/productApi.ts not found");
if (!productDetail) abort("src/app/pages/ProductDetail.tsx not found");
if (!bomList)      abort("src/app/pages/BomList.tsx not found");
if (!bomDetail)    abort("src/app/pages/BomDetail.tsx not found");

// ═══════════════════════════════════════════════════════════════════════════════
// A. Routing API contract lock (MMD-FULLSTACK-01 + MMD-FULLSTACK-03)
// ═══════════════════════════════════════════════════════════════════════════════

// A1 — Extended fields present in RoutingOperationItemFromAPI
if (/setup_time/.test(routingApi)) {
  pass("routing_api_has_setup_time");
} else {
  fail("routing_api_has_setup_time", "routingApi.ts missing setup_time in RoutingOperationItemFromAPI");
}

if (/run_time_per_unit/.test(routingApi)) {
  pass("routing_api_has_run_time_per_unit");
} else {
  fail("routing_api_has_run_time_per_unit", "routingApi.ts missing run_time_per_unit in RoutingOperationItemFromAPI");
}

if (/work_center_code/.test(routingApi)) {
  pass("routing_api_has_work_center_code");
} else {
  fail("routing_api_has_work_center_code", "routingApi.ts missing work_center_code in RoutingOperationItemFromAPI");
}

// A2 — Resource Requirement type exists (MMD-FULLSTACK-03)
if (/ResourceRequirementItemFromAPI/.test(routingApi)) {
  pass("routing_api_has_resource_requirement_type");
} else {
  fail("routing_api_has_resource_requirement_type", "routingApi.ts missing ResourceRequirementItemFromAPI interface");
}

// A3 — listResourceRequirements helper exists (MMD-FULLSTACK-03)
if (/listResourceRequirements/.test(routingApi)) {
  pass("routing_api_has_list_resource_requirements_helper");
} else {
  fail("routing_api_has_list_resource_requirements_helper", "routingApi.ts missing listResourceRequirements method");
}

// A4 — Rejected field: work_center (bare, not work_center_code) must NOT appear in routingApi.ts
// Match "work_center" that is NOT immediately followed by "_code"
if (/\bwork_center\b(?!_code)/.test(routingApi)) {
  fail("routing_api_no_bare_work_center", "routingApi.ts contains bare 'work_center' (should be work_center_code)");
} else {
  pass("routing_api_no_bare_work_center");
}

// A5 — Rejected fields must NOT appear in routingApi.ts
if (/required_skill(?!_level\b)/.test(routingApi) && /\brequired_skill\b/.test(routingApi)) {
  fail("routing_api_no_required_skill", "routingApi.ts contains required_skill — this field is rejected/deferred to ResourceRequirement domain");
} else {
  pass("routing_api_no_required_skill");
}

if (/required_skill_level/.test(routingApi)) {
  fail("routing_api_no_required_skill_level", "routingApi.ts contains required_skill_level — this field is rejected/deferred");
} else {
  pass("routing_api_no_required_skill_level");
}

if (/qc_checkpoint_count/.test(routingApi)) {
  fail("routing_api_no_qc_checkpoint_count", "routingApi.ts contains qc_checkpoint_count — this field belongs to Quality domain, not MMD routing operation");
} else {
  pass("routing_api_no_qc_checkpoint_count");
}

// ═══════════════════════════════════════════════════════════════════════════════
// B. Routing Operation Detail contract lock (MMD-FULLSTACK-01 + 02 + 04)
// ═══════════════════════════════════════════════════════════════════════════════

// B1 — Backend read integration: uses useParams
if (/useParams/.test(rodPage)) {
  pass("rod_uses_use_params");
} else {
  fail("rod_uses_use_params", "RoutingOperationDetail.tsx does not use useParams — may have lost backend read integration");
}

// B2 — Backend read integration: calls routingApi.getRouting
if (/routingApi\.getRouting/.test(rodPage)) {
  pass("rod_calls_routing_api_get_routing");
} else {
  fail("rod_calls_routing_api_get_routing", "RoutingOperationDetail.tsx does not call routingApi.getRouting — shell/mock regression likely");
}

// B3 — Resolves operation by operation_id
if (/operation_id/.test(rodPage)) {
  pass("rod_resolves_operation_by_operation_id");
} else {
  fail("rod_resolves_operation_by_operation_id", "RoutingOperationDetail.tsx does not reference operation_id — backend lookup may be broken");
}

// B4 — Uses work_center_code (correct field)
if (/work_center_code/.test(rodPage)) {
  pass("rod_uses_work_center_code");
} else {
  fail("rod_uses_work_center_code", "RoutingOperationDetail.tsx does not use work_center_code — may have reverted to incorrect field");
}

// B5 — Does NOT use bare work_center (rejected drift)
// Matches "work_center" not followed by "_code" and not preceded by "_" in a way that makes it part of another compound
if (/\bwork_center\b(?!_code)/.test(rodPage)) {
  fail("rod_no_bare_work_center", "RoutingOperationDetail.tsx contains bare 'work_center' — should be work_center_code only");
} else {
  pass("rod_no_bare_work_center");
}

// B6 — Links to /resource-requirements (MMD-FULLSTACK-04)
if (/resource-requirements/.test(rodPage)) {
  pass("rod_links_to_resource_requirements");
} else {
  fail("rod_links_to_resource_requirements", "RoutingOperationDetail.tsx missing link to /resource-requirements");
}

// B7 — Link includes routeId query param (MMD-FULLSTACK-04)
if (/routeId/.test(rodPage)) {
  pass("rod_link_includes_routeId");
} else {
  fail("rod_link_includes_routeId", "RoutingOperationDetail.tsx link to resource-requirements missing routeId param");
}

// B8 — Link includes operationId query param (MMD-FULLSTACK-04)
if (/operationId/.test(rodPage)) {
  pass("rod_link_includes_operationId");
} else {
  fail("rod_link_includes_operationId", "RoutingOperationDetail.tsx link to resource-requirements missing operationId param");
}

// B9 — Uses encodeURIComponent for URL safety
if (/encodeURIComponent/.test(rodPage)) {
  pass("rod_uses_encode_uri_component");
} else {
  fail("rod_uses_encode_uri_component", "RoutingOperationDetail.tsx link to resource-requirements does not use encodeURIComponent — URL injection risk");
}

// B10 — Rejected fields absent from ROD
if (/required_skill(?!_level\b)/.test(rodPage) && /\brequired_skill\b/.test(rodPage)) {
  fail("rod_no_required_skill", "RoutingOperationDetail.tsx contains required_skill — rejected field reintroduced");
} else {
  pass("rod_no_required_skill");
}

if (/required_skill_level/.test(rodPage)) {
  fail("rod_no_required_skill_level", "RoutingOperationDetail.tsx contains required_skill_level — rejected field reintroduced");
} else {
  pass("rod_no_required_skill_level");
}

if (/qc_checkpoint_count/.test(rodPage)) {
  fail("rod_no_qc_checkpoint_count", "RoutingOperationDetail.tsx contains qc_checkpoint_count — Quality domain boundary violation");
} else {
  pass("rod_no_qc_checkpoint_count");
}

// ═══════════════════════════════════════════════════════════════════════════════
// C. Resource Requirements read integration lock (MMD-FULLSTACK-03 + 04)
// ═══════════════════════════════════════════════════════════════════════════════

// C1 — Uses listResourceRequirements (backend read integration active)
if (/listResourceRequirements/.test(rrPage)) {
  pass("rr_uses_list_resource_requirements");
} else {
  fail("rr_uses_list_resource_requirements", "ResourceRequirements.tsx does not call listResourceRequirements — may have reverted to mock");
}

// C2 — Consumes routeId query param
if (/routeId/.test(rrPage)) {
  pass("rr_consumes_routeId_param");
} else {
  fail("rr_consumes_routeId_param", "ResourceRequirements.tsx does not consume routeId query param");
}

// C3 — Consumes operationId query param
if (/operationId/.test(rrPage)) {
  pass("rr_consumes_operationId_param");
} else {
  fail("rr_consumes_operationId_param", "ResourceRequirements.tsx does not consume operationId query param");
}

// C4 — Has clear-filter behavior (link back to /resource-requirements without params)
// Look for the clear-filter pattern: Link to "/resource-requirements" (no params)
if (/to="\/resource-requirements"/.test(rrPage) || /to='\/resource-requirements'/.test(rrPage) || /to={`\/resource-requirements`}/.test(rrPage) || (/\/resource-requirements"/.test(rrPage) && /clearFilter/.test(rrPage))) {
  pass("rr_has_clear_filter_behavior");
} else {
  fail("rr_has_clear_filter_behavior", "ResourceRequirements.tsx missing clear-filter link back to /resource-requirements without params");
}

// C5 — Does not contain a named primary inline mock array (reversion guard)
// Guard against: "const mockReqs = [" or similar primary data source replacements
if (/const\s+mock[A-Za-z]*\s*=\s*\[/.test(rrPage)) {
  fail("rr_no_inline_mock_array", "ResourceRequirements.tsx contains an inline mock array (e.g. const mockReqs = [...]) — backend read integration may have been reverted");
} else {
  pass("rr_no_inline_mock_array");
}

// C6 — Write actions remain disabled (no enabled onClick with write verbs beside read)
// This is a heuristic: we check that any button with "assign" or "create requirement" text is still disabled
// We check for the disabled attribute on buttons that reference assign-related actions
// The pattern: disabled + (assign or create or edit or delete keyword in proximity)
const rrWriteButtonEnabled = /(?<!disabled[^>]{0,200})<button[^>]+onClick[^>]*>.*?(?:assign|create requirement|edit requirement|delete requirement)/is.test(rrPage);
if (rrWriteButtonEnabled) {
  fail("rr_write_actions_remain_disabled", "ResourceRequirements.tsx appears to have an enabled write-action button (assign/create/edit/delete) — read-only contract violated");
} else {
  pass("rr_write_actions_remain_disabled");
}

// ═══════════════════════════════════════════════════════════════════════════════
// D. Screen status lock
// ═══════════════════════════════════════════════════════════════════════════════

// D1 — routingOpDetail is PARTIAL + BACKEND_API (not SHELL/MOCK/FUTURE)
const rodStatusBlock = screenStatus.match(/routingOpDetail\s*:\s*\{[^}]*\}/s);
if (!rodStatusBlock) {
  fail("screen_status_routing_op_detail_registered", "screenStatus.ts does not have routingOpDetail entry");
} else {
  const block = rodStatusBlock[0];
  if (/phase\s*:\s*["']SHELL["']|phase\s*:\s*["']MOCK["']|phase\s*:\s*["']FUTURE["']/.test(block)) {
    fail("screen_status_routing_op_detail_not_regressed", "screenStatus.ts routingOpDetail has regressed to SHELL/MOCK/FUTURE — must be PARTIAL/BACKEND_API");
  } else if (/phase\s*:\s*["']PARTIAL["']/.test(block) && /BACKEND_API/.test(block)) {
    pass("screen_status_routing_op_detail_partial_backend");
  } else {
    fail("screen_status_routing_op_detail_partial_backend", "screenStatus.ts routingOpDetail is not PARTIAL/BACKEND_API");
  }
}

// D2 — resourceRequirements is PARTIAL + BACKEND_API (not SHELL/MOCK/FUTURE)
const rrStatusBlock = screenStatus.match(/resourceRequirements\s*:\s*\{[^}]*\}/s);
if (!rrStatusBlock) {
  fail("screen_status_resource_requirements_registered", "screenStatus.ts does not have resourceRequirements entry");
} else {
  const block = rrStatusBlock[0];
  if (/phase\s*:\s*["']SHELL["']|phase\s*:\s*["']MOCK["']|phase\s*:\s*["']FUTURE["']/.test(block)) {
    fail("screen_status_resource_requirements_not_regressed", "screenStatus.ts resourceRequirements has regressed to SHELL/MOCK/FUTURE — must be PARTIAL/BACKEND_API");
  } else if (/phase\s*:\s*["']PARTIAL["']/.test(block) && /BACKEND_API/.test(block)) {
    pass("screen_status_resource_requirements_partial_backend");
  } else {
    fail("screen_status_resource_requirements_partial_backend", "screenStatus.ts resourceRequirements is not PARTIAL/BACKEND_API");
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// E. Route registry lock
// ═══════════════════════════════════════════════════════════════════════════════

const mmdRoutes = [
  { key: "route_products",               pattern: /["']products["']/ },
  { key: "route_products_detail",        pattern: /["']products\/:productId["']/ },
  { key: "route_routes",                 pattern: /["']routes["']/ },
  { key: "route_routes_detail",          pattern: /["']routes\/:routeId["']/ },
  { key: "route_routing_operation_detail", pattern: /["']routes\/:routeId\/operations\/:operationId["']/ },
  { key: "route_resource_requirements",  pattern: /["']resource-requirements["']/ },
  { key: "route_bom",                    pattern: /["']bom["']/ },
  { key: "route_bom_detail",             pattern: /["']bom\/:bomId["']/ },
  { key: "route_reason_codes",           pattern: /["']reason-codes["']/ },
];

for (const { key, pattern } of mmdRoutes) {
  if (pattern.test(routesTsx)) {
    pass(key);
  } else {
    fail(key, `routes.tsx missing MMD route matching ${pattern}`);
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// F. i18n keys lock (MMD-FULLSTACK-04 keys)
// ═══════════════════════════════════════════════════════════════════════════════

const i18nChecks = [
  { key: "i18n_en_view_resource_reqs",   file: i18nEn, lang: "en", pattern: /routingOpDetail\.action\.viewResourceReqs/ },
  { key: "i18n_en_clear_filter",         file: i18nEn, lang: "en", pattern: /resourceReqs\.action\.clearFilter/ },
  { key: "i18n_ja_view_resource_reqs",   file: i18nJa, lang: "ja", pattern: /routingOpDetail\.action\.viewResourceReqs/ },
  { key: "i18n_ja_clear_filter",         file: i18nJa, lang: "ja", pattern: /resourceReqs\.action\.clearFilter/ },
  // MMD-FULLSTACK-03 scope keys
  { key: "i18n_en_scope_label",          file: i18nEn, lang: "en", pattern: /resourceReqs\.scope\.label/ },
  { key: "i18n_en_scope_operation",      file: i18nEn, lang: "en", pattern: /resourceReqs\.scope\.operation/ },
  { key: "i18n_en_error_invalid_filter", file: i18nEn, lang: "en", pattern: /resourceReqs\.error\.invalidFilter/ },
  { key: "i18n_en_routing_op_detail_back", file: i18nEn, lang: "en", pattern: /routingOpDetail\.back/ },
  { key: "i18n_en_routing_op_detail_section_resources", file: i18nEn, lang: "en", pattern: /routingOpDetail\.section\.resources/ },
];

for (const { key, file, lang, pattern } of i18nChecks) {
  if (pattern.test(file)) {
    pass(key);
  } else {
    fail(key, `${lang}.ts missing i18n key matching ${pattern}`);
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// G. Product Version FE read integration lock (MMD-FULLSTACK-06)
// ═══════════════════════════════════════════════════════════════════════════════

// G1 — ProductVersionItemFromAPI type exists in productApi.ts
if (/ProductVersionItemFromAPI/.test(productApi)) {
  pass("pv_api_type_exists");
} else {
  fail("pv_api_type_exists", "productApi.ts missing ProductVersionItemFromAPI interface");
}

// G2 — listProductVersions helper exists in productApi.ts
if (/listProductVersions/.test(productApi)) {
  pass("pv_api_list_helper_exists");
} else {
  fail("pv_api_list_helper_exists", "productApi.ts missing listProductVersions method");
}

// G3 — getProductVersion helper exists in productApi.ts
if (/getProductVersion/.test(productApi)) {
  pass("pv_api_get_helper_exists");
} else {
  fail("pv_api_get_helper_exists", "productApi.ts missing getProductVersion method");
}

// G4 — ProductDetail consumes listProductVersions (backend read integration present)
if (/listProductVersions/.test(productDetail)) {
  pass("pv_product_detail_consumes_list");
} else {
  fail("pv_product_detail_consumes_list", "ProductDetail.tsx does not call listProductVersions — backend read integration missing");
}

// G5 — No Product Version create/update/delete UI in ProductDetail
// Check that no write-style action for versions exists in the UI
if (/createVersion|updateVersion|deleteVersion|addVersion|editVersion/.test(productDetail)) {
  fail("pv_no_write_ui_in_product_detail", "ProductDetail.tsx contains Product Version write UI — must be read-only in MMD-FULLSTACK-06");
} else {
  pass("pv_no_write_ui_in_product_detail");
}

// ═══════════════════════════════════════════════════════════════════════════════
// H. BOM FE read integration lock (MMD-FULLSTACK-07)
// ═══════════════════════════════════════════════════════════════════════════════

// H1 — BomItemFromAPI type exists in productApi.ts
if (/BomItemFromAPI/.test(productApi)) {
  pass("bom_api_type_exists");
} else {
  fail("bom_api_type_exists", "productApi.ts missing BomItemFromAPI interface");
}

// H2 — BomComponentItemFromAPI type exists in productApi.ts
if (/BomComponentItemFromAPI/.test(productApi)) {
  pass("bom_api_component_type_exists");
} else {
  fail("bom_api_component_type_exists", "productApi.ts missing BomComponentItemFromAPI interface");
}

// H3 — listProductBoms helper exists in productApi.ts
if (/listProductBoms/.test(productApi)) {
  pass("bom_api_list_helper_exists");
} else {
  fail("bom_api_list_helper_exists", "productApi.ts missing listProductBoms method");
}

// H4 — getProductBom helper exists in productApi.ts
if (/getProductBom/.test(productApi)) {
  pass("bom_api_get_helper_exists");
} else {
  fail("bom_api_get_helper_exists", "productApi.ts missing getProductBom method");
}

// H5 — BomList calls listProductBoms (backend read integration active)
if (/listProductBoms/.test(bomList)) {
  pass("bom_list_uses_list_product_boms");
} else {
  fail("bom_list_uses_list_product_boms", "BomList.tsx does not call listProductBoms — shell/mock regression likely");
}

// H6 — BomList has no primary inline mock array (reversion guard)
if (/const\s+mockBoms\s*=\s*\[/.test(bomList)) {
  fail("bom_list_no_primary_mock_array", "BomList.tsx contains const mockBoms = [...] — backend read integration may have been reverted");
} else {
  pass("bom_list_no_primary_mock_array");
}

// H7 — BomList handles product selection (product context required invariant)
if (/selectedProductId/.test(bomList)) {
  pass("bom_list_product_selection");
} else {
  fail("bom_list_product_selection", "BomList.tsx does not manage selectedProductId — product-scoped API context invariant broken");
}

// H8 — BomList view links include productId query param
if (/productId/.test(bomList) && /encodeURIComponent/.test(bomList)) {
  pass("bom_list_view_links_pass_product_id");
} else {
  fail("bom_list_view_links_pass_product_id", "BomList.tsx view links missing productId query param or encodeURIComponent");
}

// H9 — BomDetail calls getProductBom (backend read integration active)
if (/getProductBom/.test(bomDetail)) {
  pass("bom_detail_uses_get_product_bom");
} else {
  fail("bom_detail_uses_get_product_bom", "BomDetail.tsx does not call getProductBom — shell/mock regression likely");
}

// H10 — BomDetail handles missing productId (boundary invariant)
if (/productId/.test(bomDetail) && /useSearchParams/.test(bomDetail)) {
  pass("bom_detail_product_context_handling");
} else {
  fail("bom_detail_product_context_handling", "BomDetail.tsx does not use useSearchParams to read productId — product context boundary invariant broken");
}

// H11 — BomDetail has no primary inline mock fixtures (reversion guard)
if (/const\s+mockBomHeaders\s*=/.test(bomDetail) || /const\s+mockBomComponents\s*=/.test(bomDetail)) {
  fail("bom_detail_no_primary_mock_fixtures", "BomDetail.tsx contains mockBomHeaders or mockBomComponents — backend read integration may have been reverted");
} else {
  pass("bom_detail_no_primary_mock_fixtures");
}

// H12 — Screen status: bomList is PARTIAL + BACKEND_API
const bomListStatusBlock = screenStatus.match(/bomList\s*:\s*\{[^}]*\}/s);
if (!bomListStatusBlock) {
  fail("screen_status_bom_list_registered", "screenStatus.ts does not have bomList entry");
} else {
  const block = bomListStatusBlock[0];
  if (/phase\s*:\s*["']SHELL["']|phase\s*:\s*["']MOCK["']|phase\s*:\s*["']FUTURE["']/.test(block)) {
    fail("screen_status_bom_list_partial_backend", "screenStatus.ts bomList has regressed to SHELL/MOCK/FUTURE — must be PARTIAL/BACKEND_API");
  } else if (/phase\s*:\s*["']PARTIAL["']/.test(block) && /BACKEND_API/.test(block)) {
    pass("screen_status_bom_list_partial_backend");
  } else {
    fail("screen_status_bom_list_partial_backend", "screenStatus.ts bomList is not PARTIAL/BACKEND_API");
  }
}

// H13 — Screen status: bomDetail is PARTIAL + BACKEND_API
const bomDetailStatusBlock = screenStatus.match(/bomDetail\s*:\s*\{[^}]*\}/s);
if (!bomDetailStatusBlock) {
  fail("screen_status_bom_detail_registered", "screenStatus.ts does not have bomDetail entry");
} else {
  const block = bomDetailStatusBlock[0];
  if (/phase\s*:\s*["']SHELL["']|phase\s*:\s*["']MOCK["']|phase\s*:\s*["']FUTURE["']/.test(block)) {
    fail("screen_status_bom_detail_partial_backend", "screenStatus.ts bomDetail has regressed to SHELL/MOCK/FUTURE — must be PARTIAL/BACKEND_API");
  } else if (/phase\s*:\s*["']PARTIAL["']/.test(block) && /BACKEND_API/.test(block)) {
    pass("screen_status_bom_detail_partial_backend");
  } else {
    fail("screen_status_bom_detail_partial_backend", "screenStatus.ts bomDetail is not PARTIAL/BACKEND_API");
  }
}

// H14 — BOM uses component_product_id (correct backend field, not component_code)
if (/component_product_id/.test(bomDetail)) {
  pass("bom_detail_uses_component_product_id");
} else {
  fail("bom_detail_uses_component_product_id", "BomDetail.tsx does not reference component_product_id — may be using rejected component_code field");
}

// H15 — BOM does not use rejected fields
if (/\bcomponent_code\b/.test(bomDetail) || /\bcomponent_name\b/.test(bomDetail) || /\bitem_type\b/.test(bomDetail)) {
  fail("bom_no_rejected_fields", "BomDetail.tsx contains rejected fields (component_code, component_name, item_type) — these are not in BomComponentItem schema");
} else {
  pass("bom_no_rejected_fields");
}

// ═══════════════════════════════════════════════════════════════════════════════
// Final summary
// ═══════════════════════════════════════════════════════════════════════════════

const failed = results.filter((r) => r.status === "FAIL");
const passed = results.filter((r) => r.status === "PASS");

console.log("");
console.log(`${PREFIX} ──────────────────────────────────────────────────`);
console.log(`${PREFIX} SUMMARY: ${passed.length} passed, ${failed.length} failed`);

if (failed.length === 0) {
  console.log(`${PREFIX} PASS all checks`);
  process.exit(0);
} else {
  console.log(`${PREFIX} FAIL ${failed.length} check(s):`);
  for (const f of failed) {
    console.error(`  ✗ ${f.name}: ${f.reason}`);
  }
  process.exit(1);
}
