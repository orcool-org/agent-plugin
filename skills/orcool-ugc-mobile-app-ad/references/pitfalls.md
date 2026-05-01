# Common pitfalls

Each entry is a failure mode you'll hit eventually, paired with the fix. Grouped by pipeline stage.

## Brand and quotas

> [!NOTE]
> **Quota exhaustion mid-pipeline.** Trial brands ship with small `videoQuota` and `bannerAnimationQuota` budgets (as of 2026-Q2: 3 each). A single run consumes 2 banner animations (packshot + B-roll) and 1 video. Always read the live values from `studio_get_brand` rather than trusting these defaults, and abort early if either is 0.

> [!NOTE]
> **Missing signals on the brand.** If the brand has no competitor, no target audience, or fewer than three insights, `studio_generate_concept` produces a vague concept. Backfill signals (see "Before you start" in `SKILL.md`) before running the pipeline.

## Avatar

> [!NOTE]
> **`from_target_audience` picks the wrong TA.** When a brand has multiple target audiences, this methodology is unpredictable — it once returned a "first-time father, 43yo" avatar for a TA of "stressed professional woman, 32yo." Always use `methodology: "from_description"`.

> [!NOTE]
> **Under-specified description.** A description like "Stressed woman around 30, tired from work" lets the generator fill in random details. Use concrete descriptions with **negative constraints** (`NOT a new parent, NOT wearing pajamas`). See `SKILL.md` for a full example.

> [!NOTE]
> **Implicit sex.** Pass `sex` explicitly. Don't rely on the model inferring it from the description.

## Packshot and B-roll footages

> [!NOTE]
> **Horizontal source image.** A 16:9 source cropped down to 9:16 leaves black bars or a distorted image. Verify the source is vertical, or crop to 9:16 with `scripts/crop_to_9x16.py` before upload.

> [!NOTE]
> **Only a packshot, no app-screen B-roll.** The 2 TH + 2 footage default needs two footages. A pack with one packshot and no proof-point B-roll is structurally incomplete — regenerate will keep filling Scene 2 with talking-head. Register both footages before generating the creative pack.

> [!NOTE]
> **App-screen contains a conflicting name or growth-overlay banner.** If the screen shows "For Brian" while the avatar is Reyna, or carries a marketing overlay like "Your X is at your fingertips," it reads as two ads stacked. Patch the offending region with a filled PIL rectangle in the surrounding background color. Don't crop it out — you'll lose the proof point along with the noise.

> [!NOTE]
> **Zoom-cropping a full-screen as a second B-roll.** Cropping a 1160×760 region out of a full-screen and stretching to 1080×1920 produces a narrow band with black padding above and below. One good full-screen proof beat beats two distorted zooms. Register a different screenshot instead.

> [!NOTE]
> **Manual `x-amz-checksum-crc32` header on upload.** The signed URL from `studio_get_footage_upload_url` already includes the checksum in the query string. Adding the header by hand causes the server to reject the upload as malformed. `PUT` with `--data-binary` and no extra headers.

> [!NOTE]
> **Starting the packshot cascade too late.** Don't skip to the PIL text overlay fallback (Tier 4) without checking the Ad Library (Tier 1) and the brand's social accounts (Tier 2). An approved CTA card from the brand's own live ads always beats a synthesized overlay.

> [!NOTE]
> **Re-crawling the same brand on every run.** Once you find a working CTA asset, cache it via `studio_create_best_performing_reference_from_file`. Future runs start from the cached reference.

## Concept generation

> [!NOTE]
> **Missing preselected IDs.** Without all five preselected ID arrays (`preselectedAvatarIds`, `preselectedTargetAudienceIds`, `preselectedInsightIds`, `preselectedCompetitorReferenceIds`, `preselectedInspiringReferenceIds`), `studio_generate_concept` picks sources at random. The concept misses the target audience or pain point, and every downstream step amplifies the mismatch.

## Creative pack

> [!NOTE]
> **Talking-head majority.** If the pack comes back with more talking-head scenes than footage scenes, it's a fail. Update rules with `Non-talking-head count MUST be >= talking-head count` (already in the templates) and regenerate. Don't render a pack that violates this.

> [!NOTE]
> **Talking-head scene longer than 5s (paid).** AI-avatar micro-glitches become visible past ~5 seconds, so single takes of 7-11s are usually unusable for paid placements. Tighten the rules with `NO scene exceeds 5 seconds` and regenerate.

> [!NOTE]
> **`update_creative_pack_rules` returns a `ZodError`.** Known response-validation bug: the server returns `script`/`hooks`/`ctas` as objects while the client expects strings. The rules applied server-side despite the error. Continue with regenerate; confirm via `studio_list_creative_packs`.

> [!NOTE]
> **`regenerate_creative_pack` client timeout at 60s.** The server keeps working asynchronously. Wait 60-90s and check `updatedAt` on the pack — do not re-trigger regenerate on timeout, or you'll get a second async job racing with the first.

> [!NOTE]
> **Infinite regenerate loop.** Stop after three attempts. If the pack still violates invariants, surface the problem to the user with a short diagnosis ("Scene 2 keeps coming back as talking-head — the B-roll footage title may be too generic; consider renaming it").

## Video generation

> [!NOTE]
> **Wrong `methodology` value.** Only `"stable"` is valid for `studio_generate_video`. `"testimonial"` does not exist, throws on the server, and still consumes a video slot. Sanity-check against `list_video_generation_methodologies` on the first call of a session.

> [!NOTE]
> **Rendering before the audit checklist passes.** Video quota is the scarcest resource in the pipeline. Never call `studio_generate_video` until every item in the audit checklist ([`rules-templates.md`](rules-templates.md)) is true.
