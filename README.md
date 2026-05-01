# Orcool Plugin Guide

The Orcool plugin brings UGC ad production directly into your Cowork workflow by connecting your agent to [Orcool](https://app.orcool.com) — brands, avatars, footages, concepts, creative packs, and video rendering — through a single MCP server and a focused skill.

> [!NOTE]
> Authentication uses OAuth at [mcp.orcool.com](https://mcp.orcool.com); no manual API keys, no env variables. You authorize once on first use.

## Features

- **Generate Pure UGC Testimonial ads**

  Produce a 15-second 9:16 talking-head ad for any mobile app — one AI avatar, four scenes, animated packshot, app-screen B-roll. Triggered conversationally through the `orcool-ugc-mobile-app-ad` skill.

- **End-to-end Orcool Studio integration**

  The bundled MCP server exposes the full Studio surface: brand and signal management, avatars, footages, concepts, creative packs, and video generation. No Veo, ElevenLabs, or Replicate keys required.

- **App Store packshot extraction**

  Pull a 9:16 hero image straight from the iTunes lookup API for any live app, normalize it with the bundled `crop_to_9x16.py` helper, and animate it into a packshot scene in one Studio call.

- **Creative-pack auditing built in**

  The skill enforces hard invariants — exact scene count, footage-vs-talking-head balance, max scene durations — before rendering, so you never render a broken plan.

- **Optional ad-library research** *(requires the Claude in Chrome extension)*

  When a brand already runs paid ads, you can cascade through Meta Ad Library, TikTok Ads Library, and brand social accounts to find an approved CTA card stronger than a raw screenshot. Falls back to the App Store path automatically.

## Installation & Setup

### Claude Cowork

1. Open **Claude Desktop** and switch to the **Cowork** tab.
2. Click **Customize** in the left sidebar, then **Plus** icon.
3. Click **Create plugin** → **Add marketplace** in the dropdown and paste the marketplace source:
   ```
   orcool-org/agent-plugin
   ```
4. Find **Orcool** in the list (**Personal** tab → **agent-plugin** sub-tab), click **Install**, and approve the requested permissions.
5. **Authorize Orcool.** On first skill use, Cowork opens your browser for OAuth at [mcp.orcool.com](https://mcp.orcool.com). Sign in with your Orcool account and approve the connection.

### Other MCP clients

The Orcool MCP server is a standard Streamable HTTP server. If your client supports HTTP MCP transports, you can register it directly:

```json
{
  "mcpServers": {
    "orcool": {
      "url": "https://mcp.orcool.com"
    }
  }
}
```

Skills shipped in this plugin are Cowork-specific and won't activate in other clients, but the underlying `studio_*` tools work anywhere.

## Prompting your MCP client

Once authorized, prompt your agent in natural language. The skill auto-triggers on UGC-ad phrasing and walks the full pipeline.

> [!NOTE]
> Make sure the target brand exists in Orcool with at least one competitor, one target audience, three insights, and one inspiring reference. Without populated signals, concept generation falls back to vague defaults.

## Skills

### `orcool-ugc-mobile-app-ad`

**Supported assets:** any mobile app with a populated Orcool brand. Default output is a 14-16s paid-optimized 9:16 vertical video.

Use this to produce a Pure UGC Testimonial ad end-to-end — avatar selection, packshot and B-roll preparation, concept generation, creative-pack audit, and final render.

**You can ask it to:**

- **Generate a testimonial for a brand**
  - `"Make a UGC testimonial for [brand]"`
  - `"Make a pure testimonial video for [brand]"`
- **Describe the output instead of naming the format**
  - `"I need a talking-head ad for [brand]"`
  - `"Quick Meta ad with a user reviewing my app"`
  - `"15-second UGC for TikTok Ads"`

[See the full playbook →](skills/orcool-ugc-mobile-app-ad/SKILL.md)

## Best practices

### Set up brand signals before you run the skill

Concept quality is bounded by signal quality. Populate competitors, target audiences, insights, and inspiring references in Orcool Studio (or via the `studio_create_*` MCP tools) before the first run. A vague brand produces a vague concept, and every downstream step amplifies the mismatch.

### Write tight, concrete avatar descriptions

The `from_description` avatar generator rewards specificity. Include age, ethnicity-readable features, wardrobe, environment, lighting, expression — and **negative constraints** (`NOT a new parent, NOT wearing pajamas`). Pass `sex` explicitly. Don't trust the model to infer.

### Don't render until the audit checklist passes

Always run the audit checklist in [`rules-templates.md`](skills/orcool-ugc-mobile-app-ad/references/rules-templates.md) — duration totals, footage-vs-talking-head ratio, packshot on the final scene — before triggering a render. If the pack fails twice in a row, tighten the rules; if it fails three times, stop and report rather than rendering a broken plan.

### Cache successful packshot sources

When the cascade in [`packshot-sources.md`](skills/orcool-ugc-mobile-app-ad/references/packshot-sources.md) finds a strong CTA asset, persist it via `studio_create_best_performing_reference_from_file`. Future runs on the same brand start from the cached reference instead of re-crawling.

Think of the skill like a brief to a teammate. Clear signals, concrete examples, and tight rules lead to better video on the first render.

## Requirements

- Cowork (desktop app).
- Active Orcool account with at least one brand and populated signals.
- Python with Pillow for `crop_to_9x16.py`.

## License

MIT. Feedback and issues welcome at [app.orcool.com](https://app.orcool.com).
