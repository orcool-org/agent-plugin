# Packshot source cascade *(optional)*

The default packshot source is the App Store listing — public, free, and available for every live app via the iTunes lookup API. Use this cascade only when you want a stronger packshot than a raw screenshot, typically because the brand already runs paid ads with an approved CTA card (app icon, rating, "Download" button).

Work the tiers in order. Each is a fallback for the previous one. Stop at the first tier that returns a usable asset.

> [!NOTE]
> All tiers except Tier 4 (iTunes API) require the **Claude in Chrome** extension as an optional dependency — its MCP tools (`navigate`, `read_page`, `javascript_tool`, `get_screenshot`) are not bundled with this plugin. If the extension isn't installed and active, skip Tiers 1-3 and Tier 2-alt and go straight to Tier 4.

## Tier 1 — Meta Ad Library

Use this when the brand actively runs Meta ads. Approved CTA cards from live ads are the strongest packshot source you can find.

```
navigate("https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=US&q=<BrandName>")
read_page()
get_screenshot()   # only if you need to pick visually
```

Extract the image URL of a top ad:

```js
javascript_tool({ code: `
  const ads = Array.from(document.querySelectorAll('div[role="article"]'));
  return ads.slice(0,5).map(a => ({
    text: a.innerText.slice(0, 200),
    imgs: Array.from(a.querySelectorAll('img')).map(i => i.src),
  }));
`})
```

Download via Bash: `curl -L -o cta_source.jpg "<url>"`.

If the first search returns nothing, retry with `country=ALL`. Meta Ad Library is public; no login required.

## Tier 1-alt — TikTok Ads Library

Use this when the brand runs TikTok ads but is dark on Meta. Pairs naturally with Tier 1 — if one library is empty, the other is worth one navigation.

```
navigate("https://library.tiktok.com/ads?region=US&adLanguage=en&adType=ALL&name_or_id=<BrandName>")
read_page()
```

## Tier 2 — Brand social accounts

Use this when the brand has no ad-library presence but is active on social. Check in this order; each check is one `navigate` plus one `read_page` or `javascript_tool` extraction.

- **Instagram** — `https://instagram.com/<handle>/`. Pinned posts usually carry promo overlays. If IG shows a login interstitial (`read_page` returns "Log in to see"), skip to Google Images (Tier 2-alt).
- **TikTok** — `https://www.tiktok.com/@<handle>`. Public grid, no login required. Top-viewed thumbnails are the best packshot candidates.
- **YouTube Shorts** — `https://www.youtube.com/@<handle>/shorts`. End cards often contain an app icon and CTA button.
- **Facebook page** — `https://www.facebook.com/<handle>`. Cover image plus recent promo posts. Usually weaker than IG/TikTok.

## Tier 2-alt — Google Images

Use this when social accounts are locked behind login walls or empty. Brand promo art republished on affiliate or review sites usually copies the official CTA banner.

```
navigate("https://www.google.com/search?q=<BrandName>+app+download+cta&tbm=isch")
```

## Tier 3 — Client-provided asset

Use this when the user has uploaded a hero banner or CTA card to their session. Skip the crawling and use the asset directly.

## Tier 4 — App Store hero with PIL text overlay

The default. Works for every live app and requires no browser tooling:

```
curl "https://itunes.apple.com/lookup?id=<APP_ID>" | jq -r '.results[0].screenshotUrls[0]'
```

If the screenshot is plain, overlay a text CTA with PIL before calling `studio_animate_banner`:

```python
from PIL import Image, ImageDraw, ImageFont
img = Image.open("appstore_hero.jpg").convert("RGB")
draw = ImageDraw.Draw(img)
# Overlay a pill-shaped "Download Free · 4.8★ · #1 Sleep" at bottom
# (implementation left as-is — match the brand's ad style)
```

Google Play is the same flow via `navigate("https://play.google.com/store/apps/details?id=<packageName>")` and `javascript_tool` for screenshot `src` extraction.

## Tier 5 — Talking-head CTA fallback

Use this when Tiers 1-4 are all impossible — for example the app isn't live yet, or it's a B2B SaaS with no public creative presence. Drop the packshot scene and let Scene 4 stay talking-head with a verbal CTA ("Search [brand] in the App Store").

> [!NOTE]
> Warn the user that a talking-head CTA without a visual packshot typically costs 15-25% in CTR on paid placements.

## Caching successful sources

Once you find a good CTA asset, cache it on the brand via `studio_create_best_performing_reference_from_file`. Future runs of this skill (or other skills on the same brand) start from the cached reference instead of re-crawling.
