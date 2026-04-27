# Authorization Model Overview

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v1.0 | Added platform-level authorization model overview. |

Status: Canonical authorization overview.

## 1. Purpose

This document explains how FleziBCG decides whether an action is allowed.
It is a synthesis document for contributors and stakeholders.

## 2. Core model

FleziBCG uses a **backend-enforced RBAC model with hierarchical scope**, combined with:
- action-code-based authorization checks
- policy/approval checks where required
- separation-of-duties rules where required
- session/security governance rules

The effective model is:

> **Identity + Role + Scope + Action + Policy/Approval + SoD + Current operational context**

## 3. Key principles

- JWT proves identity only
- backend authorizes per request
- frontend never decides permission truth
- persona/menu visibility are UX only
- governed actions require more than RBAC alone

## 4. Decision layers

### 4.1 Identity layer
Who is the authenticated user?

### 4.2 Role layer
What role families are assigned?

Examples:
- OPR
- SUP
- IEP
- QAL
- PMG
- PLN
- INV
- ADM

### 4.3 Scope layer
Where does the user's authorization apply?

Canonical scope hierarchy:
- tenant
- plant
- area
- line
- station
- equipment

### 4.4 Action layer
What action code is being requested?

Examples:
- `execution.start`
- `execution.complete`
- `approval.decide`
- `auth.logout_all`
- `admin.session.revoke`

### 4.5 Policy / approval layer
Some actions require policy or approval checks beyond basic RBAC.

### 4.6 SoD layer
Requester must not equal decider where governed separation is required.

### 4.7 Operational context layer
Some actions depend on current operational context, for example:
- active session exists
- operator is identified
- equipment is bound where required
- target state allows progression

## 5. What this is not

FleziBCG does not rely on:
- frontend filtering as authorization
- JWT claims alone as authorization
- persona alone as authorization
- screen visibility as authorization

## 6. Governance implication

A governed action is valid only when all required layers pass.
RBAC alone is not sufficient where approval/SoD/policy applies.
