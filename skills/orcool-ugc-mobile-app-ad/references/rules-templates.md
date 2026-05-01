# Creative-pack rules templates

Two ready-to-paste rules arrays for `studio_update_creative_pack_rules`, plus the regenerate flow and the audit checklist that gates rendering.

Orcool assigns `scene.visual.footageId` at (re)generate time based on these rules. Rules are the only lever for controlling storyboard shape — don't edit the storyboard directly.

## Placeholders to substitute

Before passing the rules array, replace every `<…>` placeholder with real IDs and titles from `list_avatars` and `list_footages`:

- `<AVATAR_ID>` — the selected avatar's ID.
- `<APP_SCREEN_BROLL_ID>` — the footage registered with `type: "b-roll"`.
- `<PACKSHOT_ID>` — the footage registered with `type: "packshot"`.
- `<descriptive title>` — copy the `title` field from the corresponding footage so Orcool can match by title if an ID drifts.
- `<pain statement>` / `<proof line with numbers>` / `<stat/benefit>` / `<peer-to-peer CTA>` — short example copy lines drawn from the insight and target audience, one short sentence each.

## Paid-optimized 15s (default — 4 scenes, 2 TH + 2 footage)

```python
rules = [
    "CRITICAL: TOTAL RUNTIME MUST BE 15 SECONDS (±1s). NO scene exceeds 5 seconds. NO scene is shorter than 2.5 seconds. This is a short-form paid UGC ad, not a long testimonial.",
    "EXACTLY 4 scenes. Distribution: 2 talking-head + 2 footage scenes. Non-talking-head (footage) count MUST be >= talking-head count.",
    "Scene 1 (2.5-3s) — Talking head (avatar <AVATAR_ID>): ONE SHORT sentence hook. Example: '<pain statement>'. Maximum 8 words.",
    "Scene 2 (4-5s) — MUST use B-roll footage id <APP_SCREEN_BROLL_ID> (<descriptive title>). Voiceover continues with proof. Example: '<proof line with numbers>'. Maximum 14 words.",
    "Scene 3 (2.5-3s) — Talking head (avatar): ONE punchy sentence with number. Example: '<stat/benefit>'. Maximum 8 words.",
    "Scene 4 (4-5s) — MUST use packshot footage id <PACKSHOT_ID> (<descriptive title>). Voiceover: soft CTA. Example: '<peer-to-peer CTA>'. Maximum 10 words.",
    "Tone: conversational first-person, ULTRA-SHORT sentences, concrete numbers. No corporate jargon, no feature list, no preamble. Every word earns its place.",
    "Final audit: sum of scene durations MUST equal 14-16 seconds. If total > 16s, cut words from longest scene. If any scene > 5s, split or trim. 2 talking / 2 footage is mandatory.",
]
```

## Organic-extended ~27s (4 scenes, 2 TH + 2 footage)

```python
rules = [
    "CRITICAL RULE: Non-talking-head scenes (using registered footages) MUST be >= talking-head scenes. Target: 2 talking-head + 2 footage scenes.",
    "Storyboard has EXACTLY 4 scenes, total runtime 25-28 seconds.",
    "Scene 1 (6-7s) — Talking head (avatar <AVATAR_ID>): combined hook + problem in ONE tight beat. Example: '<pain statement>'. No separate setup scene.",
    "Scene 2 (7-8s) — MUST use B-roll footage id <APP_SCREEN_BROLL_ID>. Avatar voiceover: solution + proof with concrete numbers. Example: '<proof line>'.",
    "Scene 3 (5-6s) — Talking head (avatar): emotional payoff / lifestyle benefit. Example: '<relief/benefit line>'.",
    "Scene 4 (5-6s) — MUST use packshot footage id <PACKSHOT_ID>. Soft peer-to-peer CTA. Example: '<CTA>'.",
    "Tone: conversational first-person, short sentences, concrete numbers. No corporate jargon.",
    "Final audit: count talking-head scenes and footage scenes. If talking-head > footage, RESTRUCTURE.",
]
```

A 5-scene variant (2 TH + 3 footage) is acceptable for organic when the story benefits from an extra proof beat. Keep total runtime ≤ 30s.

## Regenerate flow

1. `studio_update_creative_pack_rules(brandId, creativePackId, rules=[…])`.
2. `studio_regenerate_creative_pack(brandId, creativePackId)` — wait 60-90s; the MCP call often client-times-out at 60s while the server keeps working asynchronously.
3. `studio_list_creative_packs(brandId)` — confirm `updatedAt` moved forward and run the audit checklist below.
4. If invariants fail, tighten the rules (for example `ABSOLUTELY NO scene longer than 4 seconds` or `Scene 2 MUST be a footage scene, NOT talking-head`) and regenerate once more. Stop after three attempts and report to the user rather than burning video quota on a broken plan.

> [!NOTE]
> The response schema validator may throw `ZodError` on `script`/`hooks`/`ctas` fields. That's a known bug in the response validator only — the rules applied server-side. Continue.

## Audit checklist *(run before `studio_generate_video`)*

- [ ] Total duration 14-16s (paid) or 25-28s (organic).
- [ ] Scene count exactly 4 (paid) or 4-5 (organic).
- [ ] Footage scenes ≥ talking-head scenes.
- [ ] No scene longer than 5s (paid) or 8s (organic).
- [ ] Every `scene.visual.footageId` resolves in `list_footages`.
- [ ] Packshot footage is on the final scene (the CTA scene).
- [ ] App-screen B-roll is on the scene with the numeric proof.
- [ ] Copy uses ultra-short sentences with concrete numbers, no corporate jargon.

Only when every item is true, call `studio_generate_video`.

## Example — ride-share [brand] US (paid-15s, final 10-12s)

Rendered storyboard after two regenerate passes:

| Scene | Dur | Visual | VO |
|---|----|---|---|
| 1 | 3s | Talking head | "My friends bet on how late I'd be." |
| 2 | 4s | ETA screen B-roll | "Now my [brand] ride arrives in under five minutes. Every time." |
| 3 | 3s | Talking head | "My stress level dropped by 90 percent." |
| 4 | 4s | Packshot | "Seriously, just try it. Download the app." |

All four invariants satisfied; rendered first-pass.
