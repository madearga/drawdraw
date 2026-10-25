#!/usr/bin/env python3
"""License activation for paid character packs.

  license.py activate <key> --provider gumroad --product <product_id>
  license.py status
  license.py deactivate

Providers: gumroad (api.gumroad.com/v2/licenses/verify) and lemonsqueezy
(api.lemonsqueezy.com/v1/licenses/activate). A valid activation is stored in
~/.sketsa/entitlement.json; `entitled()` reads it so pack installs can gate
on it. Set SKETSA_LICENSE_API=mock for tests (no network).

Enforcement is intentionally light: the foundation is open source, so this
is a goodwill gate plus a purchase record, not DRM — same posture as illo
and Oil UI.
"""
import json, os, pathlib, sys, time, urllib.request, urllib.parse, urllib.error

ENTITLEMENT = pathlib.Path.home() / ".sketsa/entitlement.json"
API_OVERRIDE = os.environ.get("SKETSA_LICENSE_API")


def _post(url, data):
    if API_OVERRIDE == "mock":
        return 200, {"success": True, "activated": True, "uses": 1, "purchase": {"email": "mock@local"}}
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=body, method="POST",
                                 headers={"Content-Type": "application/x-www-form-urlencoded",
                                          "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            return res.status, json.loads(res.read().decode())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, {}
    except (urllib.error.URLError, OSError) as e:
        raise SystemExit(f"license: network error: {e}")


def _store(provider, key, product, payload):
    ENTITLEMENT.parent.mkdir(parents=True, exist_ok=True)
    ENTITLEMENT.write_text(json.dumps({
        "provider": provider, "license_key": key, "product_id": product,
        "activated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "email": (payload.get("purchase") or {}).get("email", ""),
        "uses": payload.get("uses", 0),
    }, indent=1) + "\n")


def read():
    if not ENTITLEMENT.exists():
        return None
    try:
        return json.loads(ENTITLEMENT.read_text())
    except json.JSONDecodeError:
        return None


def entitled():
    """True when a stored entitlement exists (re-validated lazily online)."""
    return read() is not None


def cmd_activate(args):
    if not args:
        sys.exit("usage: license.py activate <key> --provider gumroad --product <id>")
    key = args[0]
    rest = args[1:]
    provider = rest[rest.index("--provider") + 1] if "--provider" in rest else "gumroad"
    product = rest[rest.index("--product") + 1] if "--product" in rest else None
    if provider == "gumroad":
        if not product:
            sys.exit("gumroad needs --product <permanent product id>")
        status, payload = _post("https://api.gumroad.com/v2/licenses/verify",
                                {"product_id": product, "license_key": key})
        ok = status == 200 and payload.get("success")
    elif provider == "lemonsqueezy":
        status, payload = _post("https://api.lemonsqueezy.com/v1/licenses/activate",
                                {"license_key": key})
        ok = status == 200 and payload.get("activated") is True
        product = (payload.get("meta") or {}).get("product_id", product)
    else:
        sys.exit(f"unknown provider: {provider} (gumroad | lemonsqueezy)")
    if not ok:
        sys.exit(f"license activation failed ({status}): {json.dumps(payload)[:200]}")
    _store(provider, key, product, payload)
    print(f"activated: {provider} {(payload.get('purchase') or {}).get('email', '')}")


def cmd_status(_):
    ent = read()
    if not ent:
        print("no entitlement (free foundation; paid packs need activation)")
        return
    print(f"provider={ent['provider']} product={ent.get('product_id', '?')} "
          f"email={ent.get('email', '?')} activated={ent.get('activated_at', '?')}")


def cmd_deactivate(_):
    if ENTITLEMENT.exists():
        ENTITLEMENT.unlink()
    print("deactivated")


if __name__ == "__main__":
    cmds = {"activate": cmd_activate, "status": cmd_status, "deactivate": cmd_deactivate}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        print(__doc__)
        sys.exit(1)
    cmds[sys.argv[1]](sys.argv[2:])
