# Dashboard Improvement Plan — EduTech AI

**Version:** 1.0  
**Date:** 2026-05-22  
**Status:** Ready for Design & Development Handoff  
**Scope:** [`templates/courses/dashboard.html`](templates/courses/dashboard.html:1), [`courses/views.py`](courses/views.py:280), [`static/css/styles.css`](static/css/styles.css:1), [`static/js/main.js`](static/js/main.js:1)

---

## Executive Summary

The current dashboard is a visually ambitious but functionally shallow data-display page. It renders four static KPI cards with circular gauges, a course card grid, and a hidden drawer containing a streak heatmap and an ambient-theme customizer. Nearly all styling is inline (776 lines of HTML with embedded `style=""` attributes), there are zero interactive filters, no trend visualizations, no alerting mechanisms, and no mobile adaptation. This plan provides a 10-dimension roadmap to transform it into a clear, actionable, user-centered decision-making tool.

---

## 1. User & Purpose Clarity

### 1.1 Primary User Roles

| Role | Description | Critical Need |
|------|-------------|---------------|
| **Self-Directed Learner** | Individual studying via imported YouTube playlists | "Am I on track? What should I do next?" |
| **Power Learner (Pro/Ultra)** | Paying user with multiple courses | "Which course needs attention? How efficient am I?" |
| **Returning User** | Comes back after days/weeks away | "Where did I leave off? Has my streak broken?" |

### 1.2 Key Tasks & Metrics Hierarchy

**Tier 1 — At-a-Glance (Always Visible, No Scroll)**
- Daily Focus Streak (days) + trend arrow
- Courses In Progress (count)
- This Week's Study Hours (with % vs target)
- Next Action: "Continue [Course Name]" CTA

**Tier 2 — Quick Scan (First Scroll)**
- Course progress cards sorted by "most recently active"
- Weekly activity sparkline (mini line chart of study minutes)

**Tier 3 — Drill-Down (On Demand)**
- Per-course detailed progress (videos completed, exam status, time spent)
- 28-day contribution heatmap
- Study habit patterns (time-of-day, session length distribution)

### 1.3 Business Questions Each Element Must Answer

| Element | Must Answer |
|---------|-------------|
| Streak KPI | "Am I consistent?" |
| Study Hours KPI | "Am I putting in enough time?" |
| Course Cards | "What should I work on next?" |
| Heatmap | "When was I most/least productive?" |

> **Priority:** Strategic Overhaul | **Rationale:** The current dashboard shows data that _exists_ but doesn't answer "what should I do next?" — the single most important question for a learner.

---

## 2. Data Visualization Best Practices

### 2.1 Current State Audit

| Current Element | Problem | Recommendation |
|----------------|---------|----------------|
| 4 × Circular SVG gauges | Circular gauges are space-inefficient and hard to compare; the SVG stroke-dashoffset math ([`dashboard.html`](templates/courses/dashboard.html:42-44)) uses arbitrary max values for streaks | Replace with **horizontal bar + number + trend arrow** for 3 of 4; keep one donut for "overall completion %" |
| Red-only heatmap scale | The streak heatmap ([`dashboard.html`](templates/courses/dashboard.html:296-300)) uses only red shades — inaccessible for color-blind users and doesn't convey "good/bad" intuitively | Use a **green-to-red diverging scale** or **blue-to-purple sequential scale** with 5 levels |
| No trend indicators | All numbers are point-in-time snapshots with no direction | Add **sparklines** (7-day mini line charts) beside each KPI |
| No goal/threshold lines | Progress bars show `completed_percentage` but no target | Add a **goal marker** (e.g., small triangle at 70% weekly target) on progress bars |

### 2.2 Proposed Visualization Map

```
┌─────────────────────────────────────────────────────────┐
│  🔥 12 Day Streak  ↑2    📊 8.5h This Week  92% of goal │
│  [████████░░] 70%       [sparkline: ▂▃▅▇▆▄▅]          │
├─────────────────────────────────────────────────────────┤
│  🎯 Continue Learning          [Import Playlist]        │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Python Bootcamp                    [████████░░] 78%│   │
│  │ ⏱ 4.2h this week  📈 +12% vs last week  ▼ goal  │   │
│  │ [sparkline: ▁▂▄▅▇██]                              │   │
│  │ [Continue] [Exam] [Delete]                         │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │ React Masterclass                  [████░░░░] 45%│   │
│  │ ⏱ 1.8h this week  📉 -8% vs last week           │   │
│  │ [sparkline: ▅▃▂▁▁▂▃]  ⚠️ Falling behind          │   │
│  │ [Continue]                                         │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 2.3 Specific Replacements

- **Pie/Donut Charts → None needed.** Current design has none, and none are recommended. If course-category breakdown is needed later, use a **horizontal stacked bar**.
- **Circular Gauges → Horizontal progress bars + sparklines.** A bar with a goal marker communicates proportion and target simultaneously.
- **Emoji as data labels → Semantic icons with `aria-label`.** Replace `📚`, `🏆`, `🎥`, `🔥` with SVG icons that have proper accessible labels.

> **Priority:** Strategic Overhaul | **Rationale:** Visualization is the single highest-impact change — it transforms the dashboard from a "data printer" into an "insight surface."

---

## 3. Layout & Visual Hierarchy

### 3.1 Current Problems

- Everything lives in one `<div class="container">` with no grid system
- The 4-KPI strip is equal-weight — nothing signals relative importance
- Critical streak data is **hidden inside a retractable drawer** ([`dashboard.html`](templates/courses/dashboard.html:260))
- The ambient-theme customizer occupies the drawer's prime real estate — decorative, not functional
- Course cards use `auto-fill, minmax(340px, 1fr)` which creates awkward gaps at certain widths

### 3.2 Proposed Grid Layout (Desktop)

```
┌──────────────────────────────────────────────────────────┐
│  HEADER: Welcome back, [Name] · [Plan Badge] · [Date]    │
├──────────┬──────────┬──────────┬─────────────────────────┤
│ STREAK   │ COURSES  │ HOURS    │ NEXT ACTION CTA         │
│ 12 🔥    │ 5 Active │ 8.5h     │ [Continue Python →]     │
│ ↑2 days  │ 2 Done   │ 92% goal │                         │
├──────────┴──────────┴──────────┴─────────────────────────┤
│  FILTER BAR: [All Courses ▾] [Sort: Recent ▾] [Search...]│
├──────────────────────────────────────────────────────────┤
│  COURSE CARD 1 (wide)         │  COURSE CARD 2 (wide)    │
│  ┌────────────────────────┐   │  ┌────────────────────┐  │
│  │ Thumbnail │ Progress   │   │  │ Thumb │ Progress   │  │
│  │           │ Sparkline   │   │  │       │ Sparkline   │  │
│  │           │ Actions     │   │  │       │ Actions     │  │
│  └────────────────────────┘   │  └────────────────────┘  │
├──────────────────────────────────────────────────────────┤
│  COURSE CARD 3               │  COURSE CARD 4            │
├──────────────────────────────────────────────────────────┤
│  [Expand: 28-Day Activity Heatmap + Study Patterns]      │
└──────────────────────────────────────────────────────────┘
```

### 3.3 Inverted-Pyramid Principle

1. **Summary Row (4 KPIs):** Answer "How am I doing?" in < 3 seconds
2. **Course Cards:** Answer "What needs my attention?" in < 10 seconds
3. **Expandable Detail:** Answer "Why?" and "What patterns exist?" on demand

### 3.4 Scrolling Strategy

- **Above the fold (no scroll):** Header + KPI row + first 2 course cards + filter bar
- **One scroll:** Remaining course cards
- **Expand-on-click:** Heatmap, study patterns, per-course analytics

> **Priority:** Strategic Overhaul | **Rationale:** The current layout buries actionable information in a drawer and gives equal visual weight to decorative theming as it does to learning progress.

---

## 4. Color, Typography & Accessibility

### 4.1 Current Problems

- `--text-secondary: #999999` on `--bg-dark: #050505` = contrast ratio ~4.5:1 (barely AA for large text, fails AA for body text)
- `--text-muted: #666666` on `#050505` = contrast ratio ~3.2:1 (fails WCAG AA entirely)
- Red-only heatmap fails for red-green colorblind users (~8% of males)
- Four font families loaded (`Inter`, `Outfit`, `Space Grotesk`, `Aspekta`, `Manrope`) — the `Aspekta` font is referenced but not imported via Google Fonts, causing fallback inconsistencies
- Font weights 200, 300, 400, 500, 600, 700, 800, 900 all used — excessive

### 4.2 Proposed Color Palette

```css
:root {
  /* Background */
  --bg-canvas: #0a0a0b;
  --bg-surface: #141416;
  --bg-surface-raised: #1c1c1f;

  /* Text — all meet WCAG AA on bg-canvas (4.5:1 min) */
  --text-primary: #f4f4f5;     /* contrast: 17.2:1 */
  --text-secondary: #a1a1aa;   /* contrast: 7.8:1  */
  --text-muted: #71717a;       /* contrast: 4.6:1  */

  /* Semantic — avoid red/green-only pairing for status */
  --accent-brand: #ef233c;      /* primary brand red */
  --status-positive: #22c55e;   /* green */
  --status-warning: #f59e0b;    /* amber */
  --status-negative: #ef4444;   /* red (always paired with icon) */
  --status-info: #3b82f6;       /* blue */

  /* Heatmap Scale (diverging, colorblind-safe) */
  --heat-0: #1c1c1f;
  --heat-1: #1e3a5f;  /* dark blue */
  --heat-2: #2563eb;  /* blue */
  --heat-3: #7c3aed;  /* violet */
  --heat-4: #a855f7;  /* purple */
}
```

### 4.3 Typographic Scale

| Role | Family | Size | Weight | Line Height | Usage |
|------|--------|------|--------|-------------|-------|
| KPI Value | `Inter` | 2rem / 32px | 700 | 1.1 | "12", "8.5h" |
| KPI Label | `Inter` | 0.75rem / 12px | 500 | 1.0 | "Day Streak" |
| Section Title | `Inter` | 1.125rem / 18px | 600 | 1.3 | "Your Courses" |
| Card Title | `Inter` | 1rem / 16px | 600 | 1.3 | Course name |
| Body | `Inter` | 0.875rem / 14px | 400 | 1.5 | Descriptions |
| Meta/Caption | `Inter` | 0.75rem / 12px | 400 | 1.4 | Timestamps, counts |

**Single font family** (`Inter`) with controlled weights (400, 500, 600, 700). Eliminate `Outfit`, `Space Grotesk`, `Aspekta`, `Manrope`. This reduces font download from ~500KB to ~80KB (Latin subset).

### 4.4 Accessibility Checklist

- [ ] All text meets **WCAG 2.1 AA** (4.5:1 for body, 3:1 for large text)
- [ ] Status never communicated by color alone — always paired with an icon or text label
- [ ] Heatmap uses **blue-to-purple** sequential scale (safe for all color vision deficiencies)
- [ ] Focus indicators visible on all interactive elements (`:focus-visible` with 2px ring)
- [ ] All icons have `aria-label` or are hidden with `aria-hidden="true"` if decorative
- [ ] `prefers-reduced-motion` respected — disable WebGL background and card hover animations

> **Priority:** Quick Win (color/text fixes) + Strategic Overhaul (font consolidation) | **Rationale:** Color contrast fixes are high-impact, low-effort. Font consolidation reduces payload and eliminates rendering inconsistencies.

---

## 5. Interactivity & User Control

### 5.1 Current State

- **Zero interactive data controls.** The dashboard is a static server-rendered page.
- The only interactive elements are: drawer toggle, ambient theme buttons, and ambient sliders — all decorative.
- Course cards have hover effects but no clickable drill-down beyond "Learn Mode" and "Final Exam" buttons.

### 5.2 Proposed Interactive Elements

#### 5.2.1 Global Controls (Persist Across Sessions)

| Control | Type | Stores In |
|---------|------|-----------|
| Course Sort | Dropdown: Recent / Progress (asc/desc) / Alphabetical | `localStorage` |
| Course Filter | Multi-select: In Progress / Completed / Has Exam Available | `localStorage` |
| Date Range | Quick-select: This Week / This Month / Last 30 Days / Custom | URL param or `localStorage` |
| View Density | Toggle: Comfortable / Compact | `localStorage` |

#### 5.2.2 Per-Element Interactions

| Element | Interaction | Response |
|---------|-------------|----------|
| KPI Card | Click | Expands to show 7/30 day trend sparkline |
| Course Card | Click | Navigates to [`learn_view`](courses/views.py) for that course |
| Progress Bar | Hover | Tooltip: "42/60 videos · 12.4h remaining · Est. finish: Jun 15" |
| Heatmap Cell | Hover | Tooltip: "May 18: 3 study events, 2.5h total" |
| Sparkline | Hover | Vertical cursor line with daily value |

#### 5.2.3 Performance Budget for Interactions

- Tooltip reveal: < 50ms (pure CSS or pre-rendered data)
- Sort/Filter toggle: < 100ms (client-side on loaded data; re-fetch only if dataset > 50 courses)
- Sparkline render: < 150ms (lightweight canvas or SVG, no charting library needed for 7-30 data points)
- Date range change: < 300ms (HTMX partial swap or fetch + DOM diff)

### 5.3 Implementation Approach

Use **HTMX** for partial page updates (filter/sort/daterange) to avoid a heavy JS framework while still providing SPA-like responsiveness. The server already renders templates — HTMX lets the server return HTML fragments for targeted swaps.

```html
<!-- Example: Sort dropdown triggers server-rendered course list swap -->
<select
  name="sort"
  hx-get="{% url 'dashboard_courses_partial' %}"
  hx-target="#course-list"
  hx-trigger="change"
  hx-swap="innerHTML transition:true">
  <option value="recent">Most Recent</option>
  <option value="progress_desc">Highest Progress</option>
  <option value="progress_asc">Lowest Progress</option>
</select>
```

> **Priority:** Strategic Overhaul | **Rationale:** Interactivity is the defining difference between a "report" and a "tool." HTMX adds this without the complexity of React/Vue in a Django project.

---

## 6. Performance & Data Freshness

### 6.1 Current Problems

- Every [`dashboard`](courses/views.py:280) request iterates over all courses, all videos per course, all Progress records (via `completed_percentage` property), and 28 days of study history
- `sync_course_video_durations()` is called on every request for courses with auto-generated durations
- No database query optimization — potential N+1 problem on `course.videos.count()` and `Progress.objects.filter()`
- No caching layer
- No loading state — if data takes 2+ seconds, the user sees a blank page

### 6.2 Optimization Plan

#### 6.2.1 Database Query Optimization

```python
# BEFORE (current): N+1 queries — one per course
for c in courses:
    total_videos_count += c.videos.count()
    total_completed_videos += Progress.objects.filter(
        user=request.user, video__course=c, is_completed=True
    ).count()

# AFTER: Single annotated query
from django.db.models import Count, Q, Sum

courses = Course.objects.filter(user=request.user).annotate(
    video_count=Count('videos'),
    completed_video_count=Count(
        'videos__progress',
        filter=Q(videos__progress__user=request.user) & Q(videos__progress__is_completed=True)
    )
).order_by('-created_at')
```

#### 6.2.2 Caching Strategy

| Data | TTL | Invalidation Trigger |
|------|-----|---------------------|
| KPI row (streak, counts, hours) | 5 min | Video completion, session log, streak update |
| Course card list | 2 min | Course import, video progress change |
| Streak heatmap data | 15 min | Session logged, video completed |
| Dashboard page (full) | 1 min | Any mutation on courses/progress |

Use Django's [`cache_page`](https://docs.djangoproject.com/en/stable/topics/cache/) decorator with `@vary_on_cookie` for user-specific caching:

```python
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie

@login_required
@vary_on_cookie
@cache_page(60)  # 1-minute full-page cache
def dashboard(request):
    ...
```

#### 6.2.3 Skeleton Screens & Loading States

Replace the current blank-load problem with:

```html
<!-- Skeleton screen shown during HTMX swaps or initial slow loads -->
<div class="skeleton-kpi" aria-busy="true">
  <div class="skeleton-bar w-16 h-8"></div>
  <div class="skeleton-bar w-24 h-3 mt-1"></div>
</div>
```

CSS for skeleton animation:
```css
.skeleton-bar {
  background: linear-gradient(90deg, #1c1c1f 25%, #27272a 50%, #1c1c1f 75%);
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s infinite;
  border-radius: 4px;
}
@keyframes skeleton-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

#### 6.2.4 Data Freshness Indicator

Add a subtle timestamp:

```html
<div class="data-freshness" title="Data as of server render time">
  Updated <time datetime="{{ last_updated_iso }}">{{ last_updated_relative }}</time>
</div>
```

> **Priority:** Quick Win (query optimization) + Strategic Overhaul (caching, skeletons) | **Rationale:** Query optimization is low-risk and immediately reduces server load. Caching and skeletons improve perceived performance dramatically.

---

## 7. Actionability & Alerts

### 7.1 Current State

The dashboard is purely descriptive — it shows data but never suggests action. The only "call to action" is the "Import Playlist" button.

### 7.2 Contextual Callouts

Add an **insight bar** below the KPI row that surfaces the single most important message:

| Condition | Message | Action |
|-----------|---------|--------|
| Streak > 0 and studied today | "🔥 You're on a {{ streak }}-day streak! Keep it going." | None (reinforcement) |
| Streak == 0 and last active > 2 days | "⏰ It's been {{ days_since }} days. Just 10 minutes keeps your streak alive." | [Start 10-min Session] |
| Course progress < 10% after 7 days | "🐢 {{ course.title }} is moving slowly. Try a focused 25-min session." | [Focus on This] |
| Exam available (100% complete, not passed) | "🏅 You've earned the right to take the {{ course.title }} final exam!" | [Take Exam] |
| No courses imported | "🚀 Import your first YouTube playlist to get started." | [Import Playlist] |
| Subscription expiring within 7 days | "⚠️ Your {{ plan }} plan expires in {{ days }} days." | [Renew] |

### 7.3 Threshold-Based Conditional Formatting

| Metric | Threshold | Visual Treatment |
|--------|-----------|-----------------|
| Weekly study hours | < 50% of goal | Amber left-border on KPI card + "Below target" label |
| Weekly study hours | < 25% of goal | Red left-border + pulsing dot |
| Course progress | 0% for 3+ days | Card gets `opacity: 0.6` + "Stalled" badge |
| Streak | At risk (no activity today, 8pm+) | Subtle reminder toast |

### 7.4 Proactive Alert Mechanisms

1. **Browser Notification** (opt-in): "Your streak is at risk! Study for 5 minutes to keep your 12-day streak."
2. **Email Digest** (Pro/Ultra): Weekly summary with "Courses that need attention"
3. **In-App Toast**: Non-blocking, auto-dismiss after 8 seconds, shown on dashboard load for time-sensitive items

```javascript
// Example: Streak-at-risk detection
if (lastActiveDate < today && currentHour >= 20) {
  showToast({
    message: "🌙 Your 12-day streak is at risk! Just 5 minutes of study saves it.",
    action: { label: "Quick Session", url: "/focus-room/" },
    duration: 8000
  });
}
```

> **Priority:** Quick Win (contextual callouts, conditional formatting) | **Rationale:** These are pure template-logic changes that dramatically increase the dashboard's utility without infrastructure changes.

---

## 8. Minimalism & Clutter Reduction

### 8.1 Elements to Remove

| Element | Reason | Replacement |
|---------|--------|-------------|
| **Ambient Theme Customizer** ([`dashboard.html`](templates/courses/dashboard.html:356-529)) | Decorative, not functional; occupies premium drawer space; gated behind paywall creating friction | Move to a dedicated "Settings → Appearance" page |
| **Ambient Tuning Sliders** ([`dashboard.html`](templates/courses/dashboard.html:447-527)) | Advanced controls for a background effect; only Ultra users can use them | Move to Settings page; accessible via gear icon in header |
| **WebGL LightRays Background** ([`dashboard.html`](templates/courses/dashboard.html:7-8)) | GPU-intensive, adds visual noise, reduces text contrast, inaccessible to screen readers | Replace with subtle CSS gradient or solid dark background |
| **"✨ Central Command Center" badge** ([`dashboard.html`](templates/courses/dashboard.html:17-19)) | Jargon; no information value | Remove entirely; the header speaks for itself |
| **Emoji as primary data labels** ([`dashboard.html`](templates/courses/dashboard.html:46)) | Inconsistent rendering across OS; not semantic | Replace with SVG icons |
| **Retractable Drawer** ([`dashboard.html`](templates/courses/dashboard.html:260)) | Hides critical streak data behind a toggle | Integrate heatmap into expandable section below course cards |
| **Duplicate "Import Playlist" CTAs** | Header + section title + empty state = 3 CTAs for same action | Keep one: in the header, always visible |
| **Inline `<style>` blocks** ([`dashboard.html`](templates/courses/dashboard.html:306-353, 466-481)) | Bloats HTML, hard to cache, harder to maintain | Extract to [`styles.css`](static/css/styles.css) |
| **Inline `onmouseover`/`onmouseout` handlers** ([`dashboard.html`](templates/courses/dashboard.html:38)) | Mixes behavior with structure; not accessible (no `:focus` equivalent) | Replace with CSS `:hover` and `:focus-visible` pseudo-classes |

### 8.2 Elements to De-emphasize

| Element | Current Treatment | Proposed Treatment |
|---------|-------------------|-------------------|
| Course card badges ("📚 EduTech AI") | Always visible on thumbnail | Remove; it's self-referential branding |
| Video count badge | Prominent in card body | Move to a metadata row below title |
| "Enrolled Courses" count | Separate text element | Integrate into section title: "Your Courses (5)" |

### 8.3 Whitespace Strategy

- KPI row: `gap: 1rem` between cards, `padding: 1.5rem` inside cards
- Section spacing: `margin-bottom: 2rem` between KPI row and course grid, `margin-bottom: 1.5rem` between grid and expandable heatmap
- Course cards: `gap: 1rem` in grid, `padding: 1.25rem` inside
- Card internal: `gap: 0.75rem` between thumbnail and body, `gap: 0.5rem` between body rows

### 8.4 Clutter Audit Checklist

- [ ] Remove the ambient customizer drawer entirely from dashboard
- [ ] Remove WebGL LightRays from dashboard (keep for marketing/landing pages)
- [ ] Extract all inline styles to CSS classes
- [ ] Extract inline event handlers to JS event listeners
- [ ] Remove "Central Command Center" badge
- [ ] Consolidate duplicate Import Playlist buttons
- [ ] Remove "📚 EduTech AI" overlay badge from course cards
- [ ] Remove inline `<style>` blocks

> **Priority:** Quick Win (badge removal, CTA consolidation, drawer content relocation) + Strategic Overhaul (inline style extraction) | **Rationale:** Clutter removal is the fastest path to a more professional appearance. The ambient customizer is a feature that belongs in Settings, not the dashboard.

---

## 9. Mobile/Responsive Adaptation

### 9.1 Current State

- The dashboard has **no responsive breakpoints** beyond the course grid's `auto-fill, minmax(340px, 1fr)`
- The 4-KPI strip uses `flex` but no wrap behavior
- The drawer is fixed-position and would overlap content on narrow screens
- Font sizes are fixed in `rem`/`px` — no viewport-relative scaling

### 9.2 Responsive Strategy

#### Breakpoints

| Breakpoint | Width | Layout |
|------------|-------|--------|
| Desktop | ≥ 1024px | Full grid: 4 KPI columns, 2-column course cards |
| Tablet | 768–1023px | 2×2 KPI grid, 1-column course cards |
| Mobile | < 768px | Stacked KPIs (2×2), 1-column cards, collapsed filter bar |

#### Mobile-Specific Adaptations

```
┌──────────────────────┐
│  Welcome, Ajay       │
│  Pro Member          │
├──────────┬───────────┤
│ 🔥 12    │ 📊 8.5h   │
│ Streak   │ This Week │
├──────────┼───────────┤
│ 📚 5     │ 🏆 2      │
│ Active   │ Mastered  │
├──────────────────────┤
│ [Continue Python →]  │  ← Full-width primary action
├──────────────────────┤
│ [Filters ▾] [Sort ▾] │  ← Collapsible filter bar
├──────────────────────┤
│ ┌──────────────────┐ │
│ │ Python Bootcamp  │ │
│ │ [████████░░] 78% │ │
│ │ 4.2h this week   │ │
│ │ [Continue]       │ │
│ └──────────────────┘ │
│ ┌──────────────────┐ │
│ │ React Masterclass│ │
│ │ [████░░░░] 45%   │ │
│ │ ⚠️ Falling behind │ │
│ │ [Continue]       │ │
│ └──────────────────┘ │
├──────────────────────┤
│ [View Activity Log]  │  ← Expandable heatmap
└──────────────────────┘
```

#### Implementation

```css
/* KPI Row: 4-up → 2×2 → stacked */
.dashboard-kpi-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

@media (max-width: 1023px) {
  .dashboard-kpi-row {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 767px) {
  .dashboard-kpi-row {
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
  }
  .kpi-card {
    padding: 1rem;
  }
  .kpi-value {
    font-size: 1.5rem;
  }
  .course-card {
    /* Remove thumbnail on very small screens? Or make it a small left-aligned avatar */
  }
}
```

- **Course cards on mobile:** Reduce thumbnail to a 60px square avatar left of the title + progress (horizontal layout), or hide thumbnail entirely below 400px.
- **Heatmap:** Collapse to a horizontal scrollable strip or reduce cell size.
- **Navigation:** The fixed navbar should collapse to a hamburger menu below 768px (already handled in [`base.html`](templates/courses/base.html) nav).

> **Priority:** Strategic Overhaul | **Rationale:** Mobile responsiveness requires a CSS restructure but is essential — many learners will check progress on their phones between study sessions.

---

## 10. Testing & Iteration

### 10.1 Usability Testing Protocol

#### Phase 1: 5-Second Test (Immediate, Low-Cost)

**Method:** Show the redesigned dashboard for exactly 5 seconds, then ask:
1. "What do you think your streak is?"
2. "Which course should you work on next?"
3. "Are you behind or ahead on your weekly goal?"

**Success Criteria:** 80%+ correct answers on all three questions.

#### Phase 2: Task-Based Observation (3–5 Users)

| Task | Measure |
|------|---------|
| "Find the course you've made the least progress on" | Time to completion, clicks |
| "Check if you studied yesterday" | Accuracy, path taken (heatmap vs. sparkline) |
| "Figure out how many videos remain in Python Bootcamp" | Time, whether tooltip was used |
| "Change the sort order of your courses" | Discoverability of filter bar |

#### Phase 3: A/B Metrics (Post-Launch)

| Metric | Current Baseline | Target |
|--------|-----------------|--------|
| Dashboard bounce rate | ? (measure first) | < 30% |
| "Continue Learning" CTR | ? | > 40% of dashboard visits |
| Time-to-first-action | ? | < 10 seconds |
| Courses resumed within 1 visit | ? | +20% |

### 10.2 Iteration Cadence

```
Week 1-2:   Implement Phase 1 changes (color, font, clutter removal)
Week 2:     5-second test with 3 users → quick fixes
Week 3-4:   Implement Phase 2 changes (visualization, interactivity)
Week 4:     Task-based observation with 5 users → prioritize fixes
Week 5-6:   Implement Phase 3 (responsive, alerts, performance)
Week 6:     Soft launch → collect analytics for 2 weeks
Week 8:     A/B metrics review → plan next iteration
```

### 10.3 Feedback Collection

- Add a subtle **"Feedback?"** link in the dashboard footer linking to a simple form (Google Form or Tally)
- Track **"Continue Learning" button clicks** vs. **course card clicks** to understand which CTA placement works better
- Monitor **filter/sort usage** — if nobody sorts, the control may be unnecessary

> **Priority:** Quick Win (5-second test, feedback link) + Ongoing (A/B metrics) | **Rationale:** Testing must start immediately after even the smallest change to validate direction. Don't wait for the full redesign.

---

## Prioritized Implementation Roadmap

### 🔴 Quick Wins (Week 1–2, Low Effort / High Impact)

| # | Change | Files Affected | Effort |
|---|--------|---------------|--------|
| 1 | Fix color contrast: `--text-secondary` → `#a1a1aa`, `--text-muted` → `#71717a` | [`styles.css`](static/css/styles.css:20-22) | 15 min |
| 2 | Remove "Central Command Center" badge | [`dashboard.html`](templates/courses/dashboard.html:16-19) | 5 min |
| 3 | Consolidate duplicate "Import Playlist" buttons — keep only header CTA | [`dashboard.html`](templates/courses/dashboard.html:30-31,152-157) | 10 min |
| 4 | Remove "📚 EduTech AI" badge from course card thumbnails | [`dashboard.html`](templates/courses/dashboard.html:179-182) | 5 min |
| 5 | Move heatmap from drawer to below course grid (always visible) | [`dashboard.html`](templates/courses/dashboard.html:263-303) | 20 min |
| 6 | Add data freshness timestamp | [`dashboard.html`](templates/courses/dashboard.html:13) | 10 min |
| 7 | Add contextual insight bar below KPIs | [`dashboard.html`](templates/courses/dashboard.html:105), [`views.py`](courses/views.py:344) | 30 min |
| 8 | Replace `onmouseover`/`onmouseout` with CSS `:hover` | [`dashboard.html`](templates/courses/dashboard.html:38,55,72,89) + [`styles.css`](static/css/styles.css) | 20 min |

### 🟡 Strategic Overhauls (Week 3–6, High Effort / Transformational)

| # | Change | Files Affected | Effort |
|---|--------|---------------|--------|
| 9 | Extract all inline styles to CSS classes | [`dashboard.html`](templates/courses/dashboard.html:1-776), [`styles.css`](static/css/styles.css) | 3–4 hours |
| 10 | Redesign KPI row: bars + sparklines replace circular gauges | [`dashboard.html`](templates/courses/dashboard.html:36-104), [`views.py`](courses/views.py:280) | 2 hours |
| 11 | Add filter/sort controls with HTMX partial rendering | [`dashboard.html`](templates/courses/dashboard.html), [`views.py`](courses/views.py), [`urls.py`](courses/urls.py) | 4 hours |
| 12 | Implement responsive grid (breakpoints + mobile layout) | [`styles.css`](static/css/styles.css), [`dashboard.html`](templates/courses/dashboard.html) | 3 hours |
| 13 | Add skeleton loading states | [`dashboard.html`](templates/courses/dashboard.html), [`styles.css`](static/css/styles.css) | 1 hour |
| 14 | Optimize database queries with `annotate`/`aggregate` | [`views.py`](courses/views.py:280-353) | 1 hour |
| 15 | Add Django caching with `@cache_page` | [`views.py`](courses/views.py:279) | 30 min |
| 16 | Move ambient customizer to dedicated Settings page | New template + [`urls.py`](courses/urls.py) | 2 hours |

### 🟢 Future Iterations (Week 7+)

| # | Change | Notes |
|---|--------|-------|
| 17 | Replace WebGL background with CSS gradient on dashboard | Performance + accessibility |
| 18 | Browser notification for streak-at-risk | Requires Service Worker |
| 19 | Weekly email digest for Pro/Ultra | Requires email backend |
| 20 | Custom dashboard layout per user (drag-and-drop cards) | Major feature |
| 21 | A/B testing framework for dashboard variations | Infrastructure |

---

## Appendix A: Current Architecture Notes

- **Framework:** Django with server-rendered templates (no SPA framework)
- **CSS:** Vanilla CSS (3012 lines) + Tailwind CSS via CDN (redundant; consider dropping Tailwind and relying on refined vanilla CSS)
- **JS:** Vanilla JS (1317 lines) with WebGL LightRays library
- **Database:** SQLite (development); queries are unoptimized with N+1 patterns
- **Caching:** None currently configured
- **Key Models:** [`UserProfile`](courses/models.py:14), [`Course`](courses/models.py), [`Progress`](courses/models.py), [`StudySession`](courses/models.py)

## Appendix B: Files to Modify (Complete List)

| File | Type of Change |
|------|---------------|
| [`templates/courses/dashboard.html`](templates/courses/dashboard.html:1) | Major rewrite — extract inline styles, restructure layout, add interactive elements |
| [`courses/views.py`](courses/views.py:280) | Optimize queries, add caching, add partial-render endpoint for HTMX |
| [`courses/urls.py`](courses/urls.py) | Add `dashboard_courses_partial` route |
| [`static/css/styles.css`](static/css/styles.css:1) | Add dashboard-specific classes, responsive breakpoints, skeleton animations |
| [`static/js/main.js`](static/js/main.js:1) | Add filter/sort logic, toast notification system, HTMX event handlers |
| [`templates/courses/base.html`](templates/courses/base.html:1) | Add skeleton CSS, reduce font imports to Inter only |
| New: `templates/courses/settings_appearance.html` | Relocate ambient customizer here |