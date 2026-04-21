"""JA message catalog — Japanese translations for API error messages."""

JA_MESSAGES: dict[str, str] = {
    # ── auth（認証）──
    "auth.invalid_credentials": "ユーザー名またはパスワードが無効です",
    "auth.token_expired": "トークンの有効期限が切れています",
    "auth.token_invalid": "トークンが無効または不正です",
    "auth.required": "認証が必要です",
    "auth.session_missing": "セッションがありません",
    "auth.session_invalid": "セッションが無効または失効しています",
    "auth.logout_success": "ログアウトしました",
    "auth.logout_all_success": "全セッションをログアウトしました",
    # ── rbac（権限管理）──
    "rbac.permission_denied": "権限がありません",
    "rbac.role_not_found": "ロールが見つかりません",
    "rbac.insufficient_permissions": "この操作に対する権限が不足しています",
    # ── operations（工程）──
    "operation.not_found": "工程が見つかりません",
    "operation.already_started": "工程は既に開始されています",
    "operation.already_completed": "工程は既に完了しています",
    "operation.cannot_complete": "現在の状態では工程を完了できません",
    "operation.cannot_abort": "現在の状態では工程を中止できません",
    "operation.clock_on_required": "数量を報告する前に作業開始(Clock-on)が必要です",
    "operation.invalid_quantity": "報告された数量が無効です",
    "operation.start_conflict": "工程の開始が現在の状態と競合しています",
    # ── station（ステーション）──
    "station.not_found": "ワークステーションが見つかりません",
    "station.already_claimed": "ワークステーションは他のオペレーターが取得中です",
    "station.not_claimed": "ワークステーションは取得されていません",
    "station.claim_not_owned": "このワークステーションの取得権限がありません",
    # ── work orders（作業指示）──
    "work_order.not_found": "作業指示が見つかりません",
    # ── production orders（製造指図）──
    "production_order.not_found": "製造指図が見つかりません",
    # ── approval（承認）──
    "approval.not_found": "承認リクエストが見つかりません",
    "approval.already_decided": "承認は既に決定されています",
    "approval.self_approval": "自身のリクエストを承認することはできません",
    "approval.permission_denied": "この承認を決定する権限がありません",
    # ── impersonation（代理操作）──
    "impersonation.not_allowed": "あなたのロールでは代理操作が許可されていません",
    "impersonation.target_admin": "管理者ロールへの代理操作はできません",
    "impersonation.already_active": "代理操作セッションが既に有効です",
    "impersonation.not_found": "代理操作セッションが見つかりません",
    "impersonation.expired": "代理操作セッションの有効期限が切れています",
    # ── tenant（テナント）──
    "tenant.missing": "テナントIDが必要です",
    "tenant.invalid": "テナントIDが無効です",
    # ── validation（バリデーション）──
    "validation.required_field": "必須フィールドが未入力です",
    "validation.invalid_format": "入力形式が無効です",
}
