# Monetization playbook — selling character packs

The foundation (this repo) stays free and open — that is the distribution.
The product is **original character packs** in a separate private repo
(`~/Projects/illo-packs`). This is the exact playbook to go from zero to
first sale.

## The money flow

```
buyer ──► store page (Gumroad / Lemon Squeezy) ──► pays $9
      ◄── email: license key + pack download link
buyer ──► license.py activate <key> ──► pack.py install <pack> ──► works
```

## One-time setup (about an hour)

1. **Create a store account** — [Gumroad](https://gumroad.com) (simplest) or
   [Lemon Squeezy](https://lemonsqueezy.com) (merchant-of-record, handles
   VAT). Both work with `license.py`; pick one.
2. **Create one product per pack** (or a bundle). Suggested pricing:
   - single pack **$9** (impulse tier)
   - **bundle of 3 packs $19** ("studio tier")
   - commercial license (use in a product's own marketing) **$49**
3. **Get the licensing IDs**:
   - Gumroad: product settings → copy the permanent product id → put it in
     the checkout + activation commands.
   - Lemon Squeezy: no product id needed for activation; the response
     carries it.
4. **Fill `skills/sketsa/store.json`** in the foundation repo with the real
   store URL and per-pack links. This is what the in-agent upsell reads.
5. **Mark packs paid**: in the packs repo's `index.json`, set
   `"paid": true` on each sellable pack (Bugsi already is). The pack
   manager then refuses installs without a valid entitlement (or `--dev`).

## Product per pack (what the buyer gets)

- `pack.zip` — the pack folder (character.md, reference.png, preview.png,
  index entry)
- A README inside: install commands, license terms (personal vs commercial)
- The license key (auto-emailed by the store)

## License enforcement — honest posture

The foundation is open source; a determined user can bypass any local gate.
The license layer (`scripts/license.py` + the `paid` gate in `pack.py`) is
**a goodwill mechanism and a purchase record**, exactly like illo and Oil
UI. What actually protects revenue:

- **Low price** — $9 is easier to pay than to pirate.
- **Updates** — buyers get new model sheets, poses, and new packs; pirated
  copies freeze.
- **New packs regularly** — the catalog is the moat, not the DRM.
- **Commercial tier** — teams that put the mascot on a landing page buy
  the $49 tier because their company needs clean paperwork.

## Buyer journey (copy for your product page)

1. Buy the pack → get license key + download by email.
2. `license.py activate GUMROAD-KEY --provider gumroad --product PRODUCT_ID`
3. Unzip and `pack.py install ~/Downloads/bugsi`
4. `pack.py default bugsi` (optional)
5. `/sketsa our new pricing page is live` — your mascot shows up on-model.

## Suggested launch sequence

1. Publish the foundation repo (done: `madearga/drawdraw`).
2. Ship **3 packs** before charging — a one-pack catalog doesn't sell; a
   three-pack catalog with a bundle does. Use the character builder flow.
3. Post one illustration per day on X/LinkedIn with the pack credit line.
4. Open the store with the bundle pricing above; keep one pack free
   (Bugsi-as-free-trial is an option: sell the others).
5. Once ~20 sales/mo are steady, add a "custom mascot commission" tier
   ($199+) — highest margin, uses the same builder flow with the client.

## Ops checklist

- [ ] Store account + product(s) created, pricing set
- [ ] store.json filled with real URLs
- [ ] packs repo index.json: `"paid": true` on sellable packs
- [ ] license terms document (personal vs commercial) in each pack zip
- [ ] Test purchase yourself: activate with the real key, install, render
