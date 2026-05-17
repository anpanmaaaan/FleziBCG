# Industrial UX Standards — FleziBCG

> Concrete numbers, not "should be large". Every value here is the FleziBCG
> standard. Deviations require explicit justification in the implementation
> report.

## 1. Viewing Context Matrix

| Persona | Primary device | Viewing distance | Lighting | Glove use | Hands free |
|---|---|---|---|---|---|
| Operator (station) | Tablet landscape 10–13" wall-mounted or kiosk | 0.5–1.0 m | Mixed (fluorescent + spot) | Yes (nitrile/leather) | Often only one hand |
| Supervisor (line) | Tablet or laptop | 0.5–0.8 m | Office + shopfloor mix | No | Two hands |
| Cell lead (walkaround) | Phone or rugged tablet portrait | 0.3–0.5 m | Variable | Often | One hand |
| Plant manager (office) | Laptop/desktop | 0.5–0.7 m | Office | No | Two hands |
| Wall display (line status board) | TV/large screen | 3.0–6.0 m | Variable | N/A | N/A |

The viewing distance drives the minimum readable type size below.

## 2. Type Scale (minimums, not targets)

Base unit: `1rem = 16px` (default Tailwind).

| Role | Min size (operator/supervisor) | Min size (wall display) | Tailwind class | Token |
|---|---|---|---|---|
| Headline (screen title) | 24px (1.5rem) | 48px | `text-2xl` | — |
| Primary metric (lot number, qty, timer) | 32px (2rem) | 96px+ | `text-3xl` / `text-4xl` | — |
| Current state label | 20px (1.25rem) | 64px | `text-xl` | — |
| Body | 16px (1rem) | 32px | `text-base` | — |
| Status badge text | 14px (0.875rem) | 24px | `text-sm` | — |
| Secondary/helper | 14px (0.875rem) | — | `text-sm` | — |
| Timestamp/meta | 12px (0.75rem) | — | `text-xs` | — |

**Operator-critical data MUST NOT use sizes below 16px.** Timestamps and audit
metadata are exceptions because they are reference, not actionable.

Line height: 1.4 for body, 1.2 for metric/headline.

## 3. Touch Targets

| Use | Min tap size | Min visual size | Min spacing between targets |
|---|---|---|---|
| Primary CTA on operator screen | 56 × 56 dp | 56 × 56 dp | 16 dp |
| Secondary action | 48 × 48 dp | 44 × 44 dp (with 4 dp padding to tap area) | 12 dp |
| Inline link / chip | 44 × 44 dp tap area | 32 dp visual | 8 dp |
| Destructive action | 56 × 56 dp + confirmation dialog | 56 × 56 dp | 24 dp from non-destructive |

Apply Radix `Slot` + `cva` size variants. Do not size buttons with arbitrary
`h-8`/`h-9` on operator screens — use `size="lg"` (Tailwind `h-12`+) minimum.

## 4. Color Contrast (WCAG 2.1 AA minimum, AAA preferred for cockpit)

| Element | Min ratio |
|---|---|
| Body text | 4.5:1 |
| Large text (≥18.66px bold or 24px regular) | 3.0:1 |
| Operator-critical state label | **7.0:1 (AAA)** |
| Status indicator (color region) | 3.0:1 against background AND distinguishable when desaturated |
| Focus ring | 3.0:1 against background |

**Three-channel coding rule:** every status MUST use color + icon + text label
together. Test by setting display to grayscale — status must still be readable.

## 5. Color Blindness Safety

FleziBCG status palette is tested for deuteranopia (most common). Do not use
red/green as the *only* differentiator. The 3-channel rule enforces this.

Avoid color pairs that fail under common deficiencies:

- pure red (`#FF0000`) vs pure green (`#00FF00`) — banned.
- amber (`#F59E0B`) vs red (`#EF4444`) without icon — banned for status.
- prefer the FleziBCG status tokens which are pre-checked.

## 6. Glove and Wet-Hand Tolerance

- No drag-only interactions on operator screens — provide tap-button equivalent.
- No hold-to-confirm interactions — use tap + confirm dialog.
- No precision sliders for critical values — use stepper with `+`/`−` buttons (`-`/`+` ≥48dp each).
- Long-press is permitted only for non-critical context menus.

## 7. Scanner / Barcode Input

When a screen accepts barcode input:

- The expected input field auto-focuses on screen mount and re-focuses after every command success/failure.
- Show a visible "Scanner ready" indicator (small `cmdk`-style chip).
- Scan-then-confirm: never auto-submit a destructive action from a scan. Show preview + Confirm button.
- Buffer protection: debounce scanner input (typical scanner emits 50–80ms between chars) but commit on `Enter` or carriage return.
- Provide manual-entry fallback within the same field.
- Show last-scanned value with `Undo` for 5 seconds.

## 8. Animation and Motion

Industrial UI tolerance for motion is **low**. Operators interpret motion as
state change.

- Transition: 150ms max for state changes; 200ms for panel transitions.
- No decorative animation (no parallax, no springy hovers, no shimmer beyond skeleton).
- No auto-playing video or auto-rotating carousel on operator screens.
- Toast / sonner: 4 seconds for info, 6 seconds for warning, **sticky for danger** (operator must dismiss).
- Reduce-motion preference: respect `prefers-reduced-motion`; disable all decorative animation when set.

## 9. Sound

- No background sound or music.
- One alert sound for `status.danger` arriving on a station, debounced to once per 10 seconds.
- Sound must be optional and respect OS-level mute.

## 10. Latency Budgets

| Interaction | Target | Max |
|---|---|---|
| Tap → visual ack | 16ms (1 frame at 60fps) | 100ms |
| Tap → optimistic state | 100ms | 250ms |
| Tap → backend ack | 500ms | 2000ms |
| Backend ack > 500ms | show progress indicator at 500ms | — |
| Backend ack > 2s | show estimated time + cancel affordance | — |

Skeleton vs spinner: use skeleton for content loads >300ms; use inline spinner
on the button for commands.

## 11. Density Modes

| Mode | Use | Padding (Tailwind) | Row height | Font scale |
|---|---|---|---|---|
| `cockpit` | Single-station operator focus | `p-6` to `p-8` | n/a (panel layout) | base |
| `dashboard` | Supervisor multi-line | `p-4` | 56–64px | base |
| `form` | Admin/master data | `p-4` | n/a | base |
| `list` | Inventory/work order browse | `p-2` to `p-3` | 40–48px | sm |
| `multi-station` | Wall display / N-up | `p-3` | n/a | scaled per viewing distance |
| `wizard` | Step-by-step (Mode A pattern) | `p-6` | n/a | base+ for primary action |

Mixing density modes in one screen breaks the anti-clutter rule. Pick one.

## 12. References

- Apple HIG iPad guidelines on tap target (44pt baseline; we exceed for shopfloor).
- Material 3 touch target 48dp baseline (we exceed for gloved use).
- WCAG 2.1 AA/AAA.
- ISA-95 part 3 (operations management) for context, not UI directly.

Numbers in this file are FleziBCG-specific calibrations and override generic
HIG/Material when in conflict for operator/shopfloor surfaces.
