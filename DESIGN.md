# Chronicle Design System

## 0. Research Log

- Embedded refs: shortlisted Airtable, Notion, and Linear → picked the operational `taste-skill` execution lane and Airtable data-surface reference because the product is a personal database first.
- UI research: queried the local UI/UX database for a calm responsive time-tracking dashboard; it supported the selected dense-grid, focus-visible approach.
- Lazyweb: 1 query, 0 screens viewed — the required endpoint could not be reached because of a TLS connection failure.
- Imagen drafts: attempted desktop, mobile, and weekly-product concepts; the image-generation endpoint failed with a network error, so no generated artwork is used as a contract.

## 1. Atmosphere & Identity

Chronicle feels like a lucid, private time ledger: a scientific notebook that is pleasant to consult at the end of a demanding day. Its signature is the *ledger line*: fine horizontal rules carry the day across views, while restrained moss-green marks show deliberate time rather than gamified completion.

## 2. Color

| Role | Token | Value | Usage |
|---|---|---:|---|
| Primary surface | `--surface` | `#F4F4EF` | App canvas |
| Raised surface | `--panel` | `#FFFDF8` | Tables, menus, sheets |
| Ink | `--ink` | `#202A33` | Primary text and marks |
| Muted ink | `--muted` | `#687077` | Labels and secondary data |
| Rule | `--rule` | `#D9DCD5` | Grid lines and dividers |
| Accent | `--moss` | `#5E7659` | Primary actions, focused work |
| Accent hover | `--moss-deep` | `#445B42` | Active primary action |
| Exception | `--clay` | `#A64D33` | Interruptions and warnings |
| B/S social | `--social` | `#4D6680` | Social-energy indicator |

Only these semantic colors may appear in product UI. Moss is reserved for actions and completed deliberate time.

## 3. Typography

Primary: `ui-sans-serif, system-ui, -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif`. Mono: `ui-monospace, "SFMono-Regular", Consolas, monospace`.

| Level | Size | Weight | Usage |
|---|---:|---:|---|
| Page title | 28px | 650 | View title |
| Section title | 18px | 650 | Table and panel titles |
| Body | 15px | 450 | Content and controls |
| Small | 13px | 450 | Supporting information |
| Ledger label | 12px | 600 | Table columns and metadata |

## 4. Spacing & Layout

The base unit is 4px: `--space-1` 4px, `--space-2` 8px, `--space-3` 12px, `--space-4` 16px, `--space-5` 20px, `--space-6` 24px, `--space-8` 32px. Desktop uses a 248px navigation rail and a max 1520px content frame. At less than 900px, the rail becomes a compact top bar; below 640px, controls reflow and tables horizontally scroll within their own region.

## 5. Components

### Button
- **Structure**: native `<button>` with icon + label where useful.
- **Variants**: primary moss, quiet, outline, destructive clay.
- **States**: hover darkens, active moves down 1px, 2px moss focus ring, disabled at 45% opacity, loading changes label, error stays inline.
- **Accessibility**: native semantics, 44px minimum target on touch, labels never use icon-only text alternatives.

### Ledger table
- **Structure**: semantic table with sticky header and scroll container.
- **States**: populated rows, empty instruction, row hover, selected row, load skeleton, inline error.
- **Accessibility**: column headers use `scope="col"`; time entries remain readable in source order.

### Energy meter
- **Structure**: labeled horizontal meter with numeric 1–5 state.
- **Variants**: biological (moss) and social (blue-gray).
- **States**: zero/empty, selected, keyboard focus, editable controls.

### Sheet / modal
- **Structure**: native dialog-like overlay with labeled form fields.
- **States**: open/closing, validation error, saving, success.
- **Accessibility**: initial focus, Escape close, `aria-modal`, and focus restoration.

## 6. Motion & Interaction

Micro feedback uses 140ms ease-out; panels use 220ms ease-in-out. Motion only clarifies state changes: the entry form opening and timer state transition. `prefers-reduced-motion` removes all nonessential transitions.

## 7. Depth & Surface

Strategy: borders plus tonal shift. Panels are off-white with a one-pixel rule and a soft, tinted `0 10px 30px rgba(32,42,51,.06)` lift. Cards are not used when a ruled table or whitespace conveys grouping more clearly. Buttons are rounded 10px; inputs 8px; tables remain square-cornered inside their panels.

## 8. Accessibility Constraints & Accepted Debt

WCAG 2.2 AA target: body contrast at least 4.5:1, visible keyboard focus, 44px touch targets for primary mobile controls, and reduced-motion support. The first version is single-user and Tailnet-scoped; authentication is intentionally delegated to the Tailnet access boundary. Before exposure outside Tailnet, add identity and transport policy.

| Item | Location | Why accepted | Exit |
|---|---|---|---|
| No multi-user accounts | Whole app | Personal, Tailnet-only first release | Add identity before public exposure |
