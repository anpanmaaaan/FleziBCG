# Station Execution Workflow Diagrams

## 1. End-to-end overview

```mermaid
flowchart TD
    A[Operation dispatched / released by orchestration] --> B[OPR opens station session]
    B --> C[OPR claims operation]
    C --> D[OPR starts execution]
    D --> E[Execution RUNNING]

    E --> F[Report production]
    F --> E

    E --> G[Pause execution]
    G --> H[Execution PAUSED]
    H --> I[Resume execution]
    I --> E

    E --> J[Start downtime]
    J --> K[Downtime open]
    K --> L[End downtime]
    L --> H

    E --> M[Submit QC measurement]
    M --> N{Backend QC evaluation}
    N -->|Pass| O[QC_PASSED]
    N -->|Pending| P[QC_PENDING]
    N -->|Fail + no hold| Q[QC_FAILED]
    N -->|Fail + hold required| R[QC_HOLD + review required]

    O --> E
    P --> E
    Q --> S[Raise exception if needed]
    R --> T[Disposition decision by QCI/QAL]
    T --> U{Decision outcome}
    U -->|Approved with effect| V[Review done / quality derived]
    U -->|Rejected| W[Remain blocked / follow policy]
    V --> H

    E --> X[Raise operational exception]
    X --> Y[SUP disposition decision]
    Y --> Z{Approved effect?}
    Z -->|Yes| H
    Z -->|No| AB[Remain blocked / unresolved]

    E --> AC[Complete execution]
    H --> AC
    AC --> AD{Completion rules pass?}
    AD -->|Yes| AE[COMPLETED]
    AD -->|No| AF[Need approved effect / reject]

    AE --> AG[Close operation]
    AG --> AH[CLOSED]
    AH --> AI{Need reopen?}
    AI -->|Yes| AJ[SUP reopen decision / command]
    AJ --> AK[OPEN + PAUSED]
    AK --> E
```

## 2. Core operator flow

```mermaid
flowchart LR
    A[Open station session] --> B[Claim operation]
    B --> C[Start execution]
    C --> D[RUNNING]
    D --> E[Report production delta]
    E --> D
    D --> F[Pause]
    F --> G[PAUSED]
    G --> H[Resume]
    H --> D
    D --> I[Complete execution]
    I --> J[COMPLETED]
    J --> K[Close operation]
    K --> L[CLOSED]
```

## 3. Downtime path

```mermaid
flowchart TD
    A[RUNNING or PAUSED] --> B[Start downtime]
    B --> C[Downtime open]
    C --> D{Policy maps to}
    D -->|Soft stop| E[Execution stays PAUSED]
    D -->|Hard block| F[Execution becomes BLOCKED]
    E --> G[End downtime]
    F --> G
    G --> H[Downtime cleared]
    H --> I[Resume execution]
    I --> J[RUNNING]
```

## 4. QC and quality hold path

```mermaid
flowchart TD
    A[Submit QC measurement] --> B[Backend evaluates rule/spec]
    B --> C{Result}
    C -->|Pass| D[QC_PASSED]
    C -->|Pending| E[QC_PENDING]
    C -->|Fail| F{Hold required by policy?}
    F -->|No| G[QC_FAILED]
    F -->|Yes| H[QC_HOLD]
    H --> I[Review status = REVIEW_REQUIRED / DECISION_PENDING]
    I --> J[QCI/QAL records disposition decision]
    J --> K{Approved?}
    K -->|Yes| L[DISPOSITION_DONE + derived quality effect]
    K -->|No| M[Remain blocked / follow policy]
    L --> N[Resume only if no remaining blockers]
```

## 5. Operational exception path

```mermaid
flowchart TD
    A[Execution issue / non-standard situation] --> B[Raise exception]
    B --> C[Review required / decision pending]
    C --> D[SUP records disposition decision]
    D --> E{Decision outcome}
    E -->|Approved| F[Server derives approved effect]
    E -->|Rejected| G[No approved effect]
    F --> H{Effect type}
    H -->|ALLOW_FORCE_RESUME| I[Can resume]
    H -->|ALLOW_SHORT_CLOSE| J[Can complete with short close]
    H -->|ALLOW_FORCE_COMPLETE| K[Can complete]
    H -->|ALLOW_REOPEN| L[Can reopen after close]
    G --> M[Remain blocked / unresolved]
```

## 6. Complete -> close -> reopen path

```mermaid
flowchart TD
    A[RUNNING or PAUSED] --> B[Complete execution]
    B --> C{Checks pass?}
    C -->|No| D[Reject or require approved effect]
    C -->|Yes| E[execution_status = COMPLETED]
    E --> F[Close operation]
    F --> G{Post-execution validations pass?}
    G -->|No| H[Reject close]
    G -->|Yes| I[closure_status = CLOSED]
    I --> J{Need reopen?}
    J -->|No| K[End]
    J -->|Yes| L[Reopen operation]
    L --> M{Authorized + reason + downstream safe + approval if needed?}
    M -->|No| N[Reject reopen]
    M -->|Yes| O[operation_reopened]
    O --> P[closure_status = OPEN]
    P --> Q[execution_status = PAUSED]
```

## 7. Responsibility swimlane view

```mermaid
flowchart LR
    subgraph OPR[OPR - Operator]
        A1[Open session]
        A2[Claim]
        A3[Start / Pause / Resume]
        A4[Report production]
        A5[Start / End downtime]
        A6[Submit QC measurement]
        A7[Complete]
        A8[Raise exception]
    end

    subgraph BE[Backend]
        B1[Validate auth + state]
        B2[Append event]
        B3[Derive statuses]
        B4[Evaluate QC rule]
        B5[Project allowed actions]
    end

    subgraph SUP[SUP - Supervisor]
        C1[Review operational exception]
        C2[Record disposition decision]
        C3[Reopen when allowed]
    end

    subgraph Q[QCI/QAL - Quality]
        D1[Review QC hold]
        D2[Record quality-owned disposition decision]
    end

    A1 --> B1 --> B2 --> B3
    A2 --> B1
    A3 --> B1
    A4 --> B1
    A5 --> B1
    A6 --> B4 --> B2 --> B3
    A8 --> B1 --> B2 --> B3
    B3 --> C1 --> C2 --> B2
    B3 --> D1 --> D2 --> B2
    B2 --> B5
    A7 --> B1 --> B2 --> B3
    C3 --> B1 --> B2 --> B3
```
