---
name: orcool-ugc-mobile-app-ad
description: >-
  Produces a 15-second 9:16 Pure UGC Testimonial ad for a mobile app — one
  AI avatar narrating over 4 scenes with an animated packshot and an
  app-screen B-roll, rendered entirely through Orcool MCP tools.
  Use when the user asks for a "UGC testimonial", "talking-head ad", or
  describes the output (e.g. "a person reviewing my app for Meta/TikTok").
---

# Pure UGC Testimonial — Orcool Studio pipeline

Use this skill to produce a 15-second 9:16 Pure UGC Testimonial ad for a mobile app, end-to-end, using only the Orcool MCP server. The pipeline is self-contained — every step runs against `studio_*` tools.

> [!NOTE]
> Every video this skill produces satisfies these invariants. They are checked **before** render, not after.
> <br><br>
> • Aspect ratio 9:16, duration 14-16s (paid) or 25-28s (organic).<br>
> • Exactly 4 scenes (paid) or 4-5 scenes (organic).<br>
> • Footage scenes (B-roll + packshot) ≥ talking-head scenes.<br>
> • No single talking-head scene longer than 5s (paid) or 8s (organic).<br>
> • Scene 2 uses an app-screen B-roll tied to a numeric proof point.<br>
> • Final scene uses an animated packshot and a soft CTA.<br>
> • Ultra-short sentences, concrete numbers, no corporate jargon.
> <br><br>
> If any invariant fails, regenerate the creative pack with tighter rules instead of rendering. Video quota is scarce — don't burn it on a bad plan.

## Before you start

You'll need a brand in Orcool with populated signals: at least 1 competitor, 1 target audience, 3+ insights, and 1+ inspiring reference. If signals are missing, fill them first via `studio_create_competitor`, `studio_create_target_audience`, `studio_create_insight`, and `studio_create_inspiring_reference`, then come back.

You'll also need an App Store or Google Play listing for the default packshot and B-roll sources. If neither exists, ask the user for an asset or fall back to the cascade in [`references/packshot-sources.md`](references/packshot-sources.md).

## How it works

Run these steps in order. Each maps to one or two MCP calls.

### 1. Check the brand and quotas

```
studio_get_brand → confirm videoQuota > 0 and bannerAnimationQuota ≥ 2
```

If either quota is 0, stop and tell the user. Continuing anyway means a partial run.

### 2. Pick or generate an avatar

Always run `studio_list_avatars` first and reuse a matching avatar if one exists. Only call `studio_generate_avatar` when nothing fits the target audience.

When you do generate, use `methodology: "from_description"` (never `from_target_audience` — it picks unpredictably when a brand has multiple TAs). Pass `sex` explicitly. Write a description that's concrete and includes negative constraints:

> A 32-year-old woman, light olive skin, dark brown shoulder-length hair, casual beige oversized sweater, sitting in a softly lit modern bedroom at night. Tired but calm expression. NOT a new parent, NOT wearing pajamas. Selfie-style framing, phone camera quality, warm lamp lighting, UGC aesthetic.

### 3. Prepare the packshot footage

The default source is the App Store hero — public, free, available for any live app:

```
curl "https://itunes.apple.com/lookup?id=<APP_ID>" | jq '.results[0].screenshotUrls'
```

Screenshot 1 is your packshot source. For brands with active paid creatives, an approved CTA card is stronger than a raw screenshot — see [`references/packshot-sources.md`](references/packshot-sources.md) for the optional 5-tier cascade.

Then:

```
crop_to_9x16.py → studio_get_footage_upload_url → PUT (no extra checksum header)
              → studio_animate_banner → poll get_job
              → studio_create_footage (type: "packshot")
```

### 4. Prepare an app-screen B-roll footage

Same flow as the packshot, but pick a screen with a visual proof point — a map + ETA, a balance chart, a notes list. Register with `type: "b-roll"` and a descriptive `title`; the title is what the creative-pack rules reference.

Example title: `App ETA screen — 2 min pickup + driver 4.9★`

> [!NOTE]
> If the screen contains a conflicting name ("For Brian" while your avatar is Reyna) or a growth-screen overlay, patch it with PIL before upload — draw a filled rectangle over the offending region in the background color. Don't crop it out; you'll lose the proof point along with the noise.

### 5. Generate the concept

`studio_generate_concept` must be called with **every** preselected ID array filled in — missing any one causes the model to pick sources at random:

- `preselectedAvatarIds`
- `preselectedTargetAudienceIds` — pick a single best TA
- `preselectedInsightIds` — pick a single sharpest insight describing a concrete pain, not a generic pattern
- `preselectedCompetitorReferenceIds` — a reference with similar pain
- `preselectedInspiringReferenceIds` — an example of good UGC tone

Set `channel: "paid"` and `format: "ugc_testimonial"` when available.

### 6. Generate the creative pack

Visuals in the storyboard (`scene.visual.footageId`) are assigned by Orcool at (re)generate time based on the rules array. Never pass visuals directly; describe them in rules and let regenerate place them.

Use the rules templates from [`references/rules-templates.md`](references/rules-templates.md). Substitute `<AVATAR_ID>`, `<APP_SCREEN_BROLL_ID>`, `<PACKSHOT_ID>`, and title references with real IDs from `list_avatars` and `list_footages`.

```
studio_update_creative_pack_rules → studio_regenerate_creative_pack
                                  → wait 60-90s (client may time out at 60s)
                                  → studio_list_creative_packs (confirm updatedAt moved)
```

> [!NOTE]
> `update_creative_pack_rules` may return a `ZodError` on `script`/`hooks`/`ctas` — the rules applied server-side anyway. Continue. The `regenerate` call often client-times-out at 60s while the server keeps working asynchronously; do not retrigger.

### 7. Audit the storyboard

Run the audit checklist from [`references/rules-templates.md`](references/rules-templates.md). If any invariant fails, tighten rules and regenerate. Two or three attempts is usually enough; stop after three and report to the user rather than burning more quota.

### 8. Render the video

```
studio_generate_video (methodology: "stable") → poll studio_list_videos
                                              → download fileUrl
                                              → save under brand folder
                                              → return computer:// link
```

> [!NOTE]
> `methodology: "stable"` is the only valid value. `"testimonial"` does not exist, throws on the server, and still consumes a video slot. Sanity-check against `list_video_generation_methodologies` on your first call of a session.

Save the MP4 to the user's workspace under the brand's subdirectory as `<brand>_<concept-slug>_testimonial_v1.mp4`. Return the local file as a `computer://` URI so the user can open it from chat — one short line of context is enough.

## You can ask it to:

- **Generate a testimonial for a brand**
  - `"Make a UGC testimonial for [brand]"`
  - `"Make a pure testimonial video for [brand]"`
- **Describe the output instead of naming the format**
  - `"I need a talking-head ad for [brand]"`
  - `"Quick Meta ad with a user reviewing my app"`
  - `"15-second UGC for TikTok Ads"`
- **Re-render after a tweak**
  - `"Re-run the testimonial with a younger avatar"`
  - `"Tighten Scene 2 — the proof line is too long"`

## When not to use this skill

- **Problem/Solution, Before/After, or App Demo formats** — those need lifestyle B-roll or an in-app screencast, which this pipeline does not cover.
- **Multi-screen in-app screencasts with tap/scroll animation** — one `animate_banner` call does not produce screencast motion.
- **Premium hand-shot production with real creators** — this skill is about speed and iteration scale, not production value.

## Reference material

- [`references/packshot-sources.md`](references/packshot-sources.md) — optional 5-tier cascade for sourcing packshot images when the App Store default isn't enough.
- [`references/rules-templates.md`](references/rules-templates.md) — ready-to-paste rules arrays for paid-15s and organic-27s, plus the audit checklist and regenerate flow.
- [`references/pitfalls.md`](references/pitfalls.md) — failure modes and their fixes, grouped by pipeline stage.
- [`scripts/crop_to_9x16.py`](scripts/crop_to_9x16.py) — the 9:16 cropping helper referenced in Steps 3 and 4.
