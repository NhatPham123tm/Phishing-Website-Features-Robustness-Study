#!/usr/bin/env python3
"""
web_features_to_csv.py  —  multi-part dataset + extended HTML + URL features

Run:
  python web_features_to_csv.py --sql index.sql --dataset-root ./dataset --out features.csv
"""

import argparse
import csv
import os
import re
import sys
from math import log2
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote

from bs4 import BeautifulSoup

# ------------------------------ SQL PARSER ------------------------------ #

INSERT_ROW_RE = re.compile(
    r"\(\s*(?P<rec_id>\d+)\s*,\s*'(?P<url>[^']*)'\s*,\s*'(?P<website>[^']*)'\s*,\s*(?P<result>[01])\s*,\s*'(?P<created>[^']*)'\s*\)\s*,?"
)

def parse_index_sql(sql_path: Path):
    site_by_filename = {}
    rows = []
    with open(sql_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if "(" not in line or ")" not in line:
                continue
            for m in INSERT_ROW_RE.finditer(line):
                d = m.groupdict()
                d["result"] = int(d["result"])
                rows.append(d)
                site_by_filename[d["website"]] = {
                    "url": d["url"],
                    "result": d["result"],
                    "rec_id": int(d["rec_id"]),
                    "created": d["created"],
                }
    return site_by_filename, rows

# ------------------------------ WINDOWS LONG-PATH SAFE READ ------------------------------ #

def _win_longpath(p: str) -> str:
    ap = os.path.abspath(p)
    if ap.startswith('\\\\?\\') or ap.startswith('\\\\.\\'):
        return ap
    if ap.startswith('\\\\'):
        return '\\\\?\\UNC' + ap[1:]
    return '\\\\?\\' + ap

def safe_read_bytes(path: Path) -> bytes:
    try:
        return path.read_bytes()
    except OSError:
        if sys.platform.startswith('win'):
            with open(_win_longpath(str(path)), 'rb') as f:
                return f.read()
        raise

# ------------------------------ UTILITIES ------------------------------ #

KEYWORD_RE = re.compile(r"\b(login|sign\s*in|verify|password|account|secure|update)\b", re.I)
SUSPICIOUS_TERMS = [
    "login", "signin", "verify", "update", "secure", "account", "bank",
    "confirm", "invoice", "wallet", "unlock", "password", "pay", "paypal",
    "appleid", "microsoft", "amazon", "delivery", "otp"
]

def soup_from_bytes(data: bytes):
    try:
        return BeautifulSoup(data, "lxml")
    except Exception:
        return BeautifulSoup(data, "html.parser")

def hostname(url: str) -> str:
    try:
        return urlparse(url).hostname or ""
    except Exception:
        return ""

def is_absolute(href: str) -> bool:
    return href.startswith(("http://", "https://", "//"))

def get_host(href: str) -> str:
    if not href:
        return ""
    if href.startswith("//"):
        href = "http:" + href
    try:
        return urlparse(href).hostname or ""
    except Exception:
        return ""

def domain_looks_like_ip(host: str) -> bool:
    return bool(re.fullmatch(r"(?:\d{1,3}\.){3}\d{1,3}", host))

def count_inline_events(tag) -> int:
    return sum(1 for a in tag.attrs.keys() if isinstance(a, str) and a.lower().startswith("on"))

def shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    counts = {}
    for ch in s:
        counts[ch] = counts.get(ch, 0) + 1
    n = len(s)
    return -sum((c / n) * log2(c / n) for c in counts.values())

def parse_int(x):
    try:
        return int(str(x).strip())
    except Exception:
        return None

# ------------------------------ URL FEATURE HELPERS ------------------------------ #

def _safe_urlparse(u: str):
    try:
        return urlparse(u)
    except Exception:
        return urlparse("")

def _count_pct_encoded(s: str) -> int:
    return s.count('%')

def _token_stats(segment: str):
    # tokens by /, -, _, ., ?, =, &, #
    toks = re.split(r"[\/\-\._\?\=&#]+", segment)
    toks = [t for t in toks if t]
    if not toks:
        return 0, 0, 0
    lengths = [len(t) for t in toks]
    return len(toks), max(lengths), sum(lengths)/len(lengths)

def _split_host_parts(host: str):
    """
    Best effort split: subdomain, sld (registered domain), tld.
    Uses tldextract if present; else fallback heuristic.
    """
    sub, sld, tld = "", "", ""
    if not host:
        return sub, sld, tld
    try:
        import tldextract  # optional
        ext = tldextract.extract(host)
        sub, sld, tld = ext.subdomain, ext.domain, ext.suffix
    except Exception:
        parts = host.split(".")
        if len(parts) >= 2:
            sld = parts[-2]
            tld = parts[-1]
            sub = ".".join(parts[:-2])
        else:
            sld = host
            tld = ""
            sub = ""
    return sub, sld, tld

def extract_url_features(orig_url: str) -> dict:
    if not orig_url:
        return {k: 0 if k.startswith(("num_", "url_", "path_", "query_", "frag_", "subdomain_", "domain_")) else "" 
                for k in [
                    "url_scheme","uses_https","has_port","port","url_length","url_length_no_scheme",
                    "num_dots","num_hyphens","num_digits","num_specials","num_at","num_pct",
                    "pct_encoded_ratio","has_ip_host","domain","domain_length","subdomain","subdomain_length",
                    "subdomain_depth","tld","tld_length","path","path_length","path_depth","path_token_count",
                    "path_longest_token","path_avg_token_len","query","query_length","query_param_count",
                    "fragment_length","contains_suspicious_terms","url_entropy"
                ]}
    u = _safe_urlparse(orig_url)
    full = orig_url
    host = u.hostname or ""
    path = u.path or ""
    query = u.query or ""
    fragment = u.fragment or ""
    scheme = (u.scheme or "").lower()
    port = u.port if u.port is not None else -1

    # base counts
    url_len = len(full)
    no_scheme = re.sub(r"^[a-zA-Z][a-zA-Z0-9+\-.]*://", "", full)
    url_len_no_scheme = len(no_scheme)

    # characters
    num_dots = full.count(".")
    num_hyphens = full.count("-")
    num_digits = sum(ch.isdigit() for ch in full)
    num_at = full.count("@")
    num_pct = _count_pct_encoded(full)
    num_specials = len(re.findall(r"[^A-Za-z0-9]", full))

    pct_encoded_ratio = round(num_pct / max(1, url_len), 6)
    url_entropy = round(shannon_entropy(full), 6)

    # host details
    ip_host = int(domain_looks_like_ip(host))
    sub, sld, tld = _split_host_parts(host)
    domain = (sld + ("." + tld if tld else "")) if sld else host
    sub_depth = 0 if not sub else len([p for p in sub.split(".") if p])

    # path/query stats
    path_token_count, path_longest_token, path_avg_token_len = _token_stats(path)
    query_params = parse_qs(query, keep_blank_values=True)
    query_param_count = sum(len(v) for v in query_params.values())

    # suspicious terms anywhere in URL (case-insensitive, check decoded too)
    full_lower = full.lower()
    full_unquoted = unquote(full_lower)
    contains_suspicious_terms = int(any(term in full_lower or term in full_unquoted for term in SUSPICIOUS_TERMS))

    return {
        "url_scheme": scheme,
        "uses_https": int(scheme == "https"),
        "has_port": int(u.port is not None),
        "port": port,
        "url_length": url_len,
        "url_length_no_scheme": url_len_no_scheme,
        "num_dots": num_dots,
        "num_hyphens": num_hyphens,
        "num_digits": num_digits,
        "num_specials": num_specials,
        "num_at": num_at,
        "num_pct": num_pct,
        "pct_encoded_ratio": pct_encoded_ratio,
        "url_entropy": url_entropy,
        "has_ip_host": ip_host,
        "domain": domain,
        "domain_length": len(domain),
        "subdomain": sub,
        "subdomain_length": len(sub),
        "subdomain_depth": sub_depth,
        "tld": tld,
        "tld_length": len(tld),
        "path": path,
        "path_length": len(path),
        "path_depth": len([p for p in path.split("/") if p]),
        "path_token_count": path_token_count,
        "path_longest_token": path_longest_token,
        "path_avg_token_len": round(path_avg_token_len, 6),
        "query": query,
        "query_length": len(query),
        "query_param_count": query_param_count,
        "fragment_length": len(fragment),
        "contains_suspicious_terms": contains_suspicious_terms,
    }

# ------------------------------ FEATURE EXTRACT (HTML + URL) ------------------------------ #

def extract_features_for(html_path: Path, mapped_url: str | None):
    data = safe_read_bytes(html_path)
    page_bytes = len(data)
    soup = soup_from_bytes(data)

    # Basic text & title
    title_text = (soup.title.string or "").strip() if soup.title and soup.title.string else ""
    text = soup.get_text(" ", strip=True)
    n_text_chars = len(text)

    # Meta / OG
    meta_tags = soup.find_all("meta")
    og_tags = [m for m in meta_tags if (m.get("property") or "").lower().startswith("og:")]
    has_og_url = any((m.get("property") or "").lower() == "og:url" for m in og_tags)
    has_og_image = any((m.get("property") or "").lower() == "og:image" for m in og_tags)
    has_og_title = any((m.get("property") or "").lower() == "og:title" for m in og_tags)
    og_tags_count = len(og_tags)

    # Links
    anchors = soup.find_all("a")
    hrefs = [a.get("href", "") for a in anchors if a.get("href")]
    abs_hrefs = [h for h in hrefs if is_absolute(h)]
    mailto_hrefs = [h for h in hrefs if h.lower().startswith("mailto:")]

    orig_host = hostname(mapped_url) if mapped_url else ""
    external_links = [h for h in abs_hrefs if (host := get_host(h)) and host != orig_host]

    # Scripts
    scripts = soup.find_all("script")
    script_srcs = [s.get("src", "") for s in scripts if s.get("src")]
    inline_scripts = [s for s in scripts if not s.get("src")]
    external_scripts = [s for s in scripts if (src := s.get("src")) and is_absolute(src)]
    script_text_concat = " ".join(s.get_text() or "" for s in inline_scripts)
    script_entropy = shannon_entropy(script_text_concat)

    # iframes, images
    iframes = soup.find_all("iframe")
    images = soup.find_all("img")
    img_srcs = [i.get("src", "") for i in images if i.get("src")]
    abs_imgs = [s for s in img_srcs if is_absolute(s)]
    external_imgs = [s for s in abs_imgs if (host := get_host(s)) and host != orig_host]

    # average image area (from width/height attributes if present)
    img_areas = []
    for i in images:
        w = parse_int(i.get("width"))
        h = parse_int(i.get("height"))
        if w and h and w > 0 and h > 0:
            img_areas.append(w * h)
    avg_image_area = (sum(img_areas) / len(img_areas)) if img_areas else 0.0

    # Stylesheets / CSS
    link_tags = soup.find_all("link")
    stylesheet_links = [l for l in link_tags if any((r or "").lower() == "stylesheet" for r in (l.get("rel") or []))]
    external_stylesheets = [l for l in stylesheet_links if is_absolute(l.get("href", ""))]
    css_external_ratio = round(len(external_stylesheets) / max(1, len(stylesheet_links)), 6)

    # Inline style attributes & <style> blocks
    inline_style_length = 0
    for t in soup.find_all(True):
        st = t.get("style")
        if st:
            inline_style_length += len(st)
    for st in soup.find_all("style"):
        inline_style_length += len(st.get_text() or "")

    # Favicon external?
    def _has_icon(rel_value):
        if isinstance(rel_value, list):
            return any("icon" in (r or "").lower() for r in rel_value)
        return "icon" in (rel_value or "").lower()

    favicon_links = [l for l in link_tags if _has_icon(l.get("rel"))]
    has_favicon_external = int(any(is_absolute(l.get("href", "")) for l in favicon_links))

    # Forms & inputs
    forms = soup.find_all("form")
    inputs = soup.find_all("input")
    pw_inputs = [i for i in inputs if (i.get("type", "") or "").lower() == "password"]
    hidden_inputs = [i for i in inputs if (i.get("type", "") or "").lower() == "hidden"]

    orig_host = hostname(mapped_url) if mapped_url else ""

    def is_external_form_action(action: str) -> bool:
        if not action:
            return False  # empty/relative -> not external
        if action.startswith("//"):
            action = "http:" + action
        if not is_absolute(action):
            return False  # relative path
        act_host = hostname(action)
        return bool(act_host) and act_host != orig_host
    
    def is_null_link(u: str) -> bool:
        if not u:
            return True
        u = u.strip().lower()
        return (
            u == "#" or
            u.startswith("javascript:") or
            u in ("javascript:void(0)", "javascript:;", "void(0)") or
            u.startswith("mailto:")
        )

    # Definition: "#", "about:blank", empty string, "javascript:true"
    def is_abnormal_action(u: str) -> bool:
        if u is None: return True # Treat missing action as empty/abnormal
        u = u.strip().lower()
        return (
            u == "" or
            u == "#" or
            u == "about:blank" or
            u.startswith("javascript:") or
            u.startswith("mailto:")
        )

    # Definition: Valid URL path that is NOT absolute and NOT abnormal
    def is_relative_action(u: str) -> bool:
        if is_abnormal_action(u): 
            return False # If it's abnormal (e.g. ""), we classify it as abnormal, not relative
        # It is relative if it is NOT absolute (implies it's a path like /login or login.php)
        return not is_absolute(u)
    
    # Collect all href/src similar to B's DOM buckets
    hrefs = [t.get("href") for t in soup.find_all(href=True)]
    srcs  = [t.get("src")  for t in soup.find_all(src=True)]
    all_links = hrefs + srcs

    n_total_links = len(all_links)
    n_null_links  = sum(is_null_link(u) for u in all_links)

    ratio_null_links = n_null_links / max(1, n_total_links)

    forms = soup.find_all("form")
    inputs = soup.find_all("input")
    pw_inputs = [i for i in inputs if (i.get("type", "") or "").lower() == "password"]
    hidden_inputs = [i for i in inputs if (i.get("type", "") or "").lower() == "hidden"]
    # Calculate features
    form_method_post_ratio = round(sum(1 for f in forms if (f.get("method", "") or "").lower() == "post") / max(1, len(forms)), 6)
    
    # Existing external check
    form_action_external = int(any(is_external_form_action(f.get("action", "") or "") for f in forms))
    
    # Abnormal check (Equivalent to SFH)
    abnormal_form_action = int(any(is_abnormal_action(f.get("action")) for f in forms))

    # Relative check (Now catches 'login.php' as well as '/login')
    relative_form_action = int(any(is_relative_action(f.get("action", "") or "") for f in forms))

    # Heuristics / flags
    text_lower = text.lower()
    has_login_keywords = int(bool(KEYWORD_RE.search(text_lower)))
    has_recaptcha = int("recaptcha" in text_lower or any("recaptcha" in (src or "").lower() for src in script_srcs))
    has_meta_refresh = int(any("refresh" in ((m.get("http-equiv") or "")).lower() for m in meta_tags))
    
    # --- Popup window heuristic  ---
    html_lower = str(soup).lower()
    popup_window = int(any(tok in html_lower for tok in [
    "prompt(", "alert(", "confirm(", "window.open("]))

    # Inline JS event attributes
    inline_event_attrs = 0
    for tag in soup.find_all(True):
        inline_event_attrs += count_inline_events(tag)

    # Ratios (guard divide-by-zero)
    n_links = len(hrefs)
    n_abs_links = len(abs_hrefs)
    n_ext_links = len(external_links)
    ratio_external_links = n_ext_links / max(1, n_links)
    ratio_abs_links = n_abs_links / max(1, n_links)

    n_tags_total = len(soup.find_all(True)) or 1
    script_tag_fraction = len(scripts) / n_tags_total

    # Domain shape (HTML-side)
    dom = orig_host
    domain_has_ip = int(domain_looks_like_ip(dom))
    domain_hyphen_count = dom.count("-") if dom else 0
    domain_digit_count = sum(ch.isdigit() for ch in dom) if dom else 0

    # ---------------- URL FEATURES (from mapped_url) ----------------
    url_feats = extract_url_features(mapped_url or "")

    return {
        "filename": html_path.name,
        "orig_url": mapped_url or "",
        "orig_host": dom,
        "page_bytes": page_bytes,
        "text_chars": n_text_chars,
        "title_len": len(title_text),

        # Meta / OG
        "n_meta": len(meta_tags),
        "n_og_meta": len(og_tags),
        "has_og_url": int(has_og_url),
        "has_og_image": int(has_og_image),
        "has_og_title": int(has_og_title),
        "og_tags_count": len(og_tags),
        "has_meta_refresh": has_meta_refresh,

        # Links
        "n_links": n_links,
        "n_abs_links": n_abs_links,
        "n_external_links": n_ext_links,
        "ratio_external_links": round(ratio_external_links, 6),
        "ratio_abs_links": round(ratio_abs_links, 6),
        "n_mailto_links": len(mailto_hrefs),
        "ratio_null_links": round(ratio_null_links, 6),

        # Scripts
        "n_scripts": len(scripts),
        "n_inline_scripts": len(inline_scripts),
        "n_external_scripts": len(external_scripts),
        "script_entropy": round(script_entropy, 6),
        "script_tag_fraction": round(script_tag_fraction, 6),

        # Frames & images
        "n_iframes": len(iframes),
        "n_images": len(images),
        "n_external_images": len(external_imgs),
        "avg_image_area": round(avg_image_area, 2),

        # CSS & styles
        "css_external_ratio": css_external_ratio,
        "inline_style_length": inline_style_length,
        "has_favicon_external": has_favicon_external,

        # Forms & inputs
        "n_forms": len(forms),
        "n_inputs": len(inputs),
        "n_pw_inputs": len(pw_inputs),
        "n_hidden_inputs": len(hidden_inputs),
        "form_action_external": form_action_external,
        "relative_form_action": relative_form_action, 
        "abnormal_form_action": abnormal_form_action,
        "form_method_post_ratio": form_method_post_ratio,

        # Heuristics
        "has_login_keywords": has_login_keywords,
        "has_recaptcha": has_recaptcha,
        "inline_event_attrs": inline_event_attrs,
        "popup_window": popup_window,

        # Domain shape (HTML-side)
        "domain_has_ip": domain_has_ip,
        "domain_hyphen_count": domain_hyphen_count,
        "domain_digit_count": domain_digit_count,

        # -------- URL features (from SQL url) --------
        **url_feats,
    }

# ------------------------------ PART SCANNER ------------------------------ #

def index_dataset_parts(dataset_root: Path):
    by_filename: dict[str, Path] = {}
    all_paths = set()

    if not dataset_root.exists():
        raise FileNotFoundError(f"Dataset root not found: {dataset_root}")

    part_dirs = sorted(p for p in dataset_root.iterdir() if p.is_dir() and p.name.startswith("dataset-part-"))
    if not part_dirs:
        part_dirs = [dataset_root]

    exts = {".html", ".htm", ".HTML", ".HTM"}
    for d in part_dirs:
        for p in d.rglob("*"):
            if p.is_file() and p.suffix in exts:
                all_paths.add(p)
                bn = p.name
                if bn not in by_filename:
                    by_filename[bn] = p
    return by_filename, all_paths, part_dirs

# ------------------------------ MAIN ------------------------------ #

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sql", required=True, help="Path to index.sql")
    ap.add_argument("--dataset-root", required=True, help="Root folder containing dataset-part-* subfolders")
    ap.add_argument("--out", default="DatasetC.csv", help="Output CSV path")
    args = ap.parse_args()

    mapping, _ = parse_index_sql(Path(args.sql))
    by_filename, all_paths, part_dirs = index_dataset_parts(Path(args.dataset_root))

    print(f"Found {len(part_dirs)} part folder(s); {len(all_paths)} HTML file(s).")
    print("Writing features…")

    fieldnames = [
        "rec_id", "created", "label",
        "filename", "orig_url", "orig_host",
        "page_bytes", "text_chars", "title_len",

        # Meta / OG
        "n_meta", "n_og_meta", "has_og_url", "has_og_image", "has_og_title",
        "og_tags_count", "has_meta_refresh",

        # Links
        "n_links", "n_abs_links", "n_external_links", "ratio_external_links", "ratio_abs_links",
        "n_mailto_links","ratio_null_links",

        # Scripts
        "n_scripts", "n_inline_scripts", "n_external_scripts", "script_entropy", "script_tag_fraction",

        # Frames & images
        "n_iframes", "n_images", "n_external_images", "avg_image_area",

        # CSS & styles
        "css_external_ratio", "inline_style_length", "has_favicon_external",

        # Forms & inputs
        "n_forms", "n_inputs", "n_pw_inputs", "n_hidden_inputs",
        "form_action_external", "form_method_post_ratio", "relative_form_action", "abnormal_form_action",

        # Heuristics
        "has_login_keywords", "has_recaptcha", "inline_event_attrs","popup_window",

        # Domain shape (HTML-side)
        "domain_has_ip", "domain_hyphen_count", "domain_digit_count",

        # ---------------- URL features (from SQL url) ----------------
        "url_scheme","uses_https","has_port","port",
        "url_length","url_length_no_scheme","num_dots","num_hyphens","num_digits",
        "num_specials","num_at","num_pct","pct_encoded_ratio","url_entropy",
        "has_ip_host","domain","domain_length","subdomain","subdomain_length",
        "subdomain_depth","tld","tld_length",
        "path","path_length","path_depth","path_token_count","path_longest_token","path_avg_token_len",
        "query","query_length","query_param_count","fragment_length",
        "contains_suspicious_terms",
    ]

    missing_files, skipped = [], []
    matched = 0

    out_path = Path(args.out)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()

        for website, meta in mapping.items():
            html_path = by_filename.get(website) or by_filename.get(Path(website).name)
            if html_path is None or not html_path.exists():
                missing_files.append(website)
                continue
            try:
                feats = extract_features_for(html_path, meta.get("url"))
            except Exception as e:
                skipped.append(f"{html_path}  ||  {type(e).__name__}: {e}")
                continue

            row = {
                "rec_id": meta.get("rec_id"),
                "created": meta.get("created"),
                "label": meta.get("result"),
                **feats,
            }
            w.writerow(row)
            matched += 1

    print(f"Matched {matched} / {len(mapping)} rows from SQL to HTML files.")
    if missing_files:
        miss_path = out_path.with_suffix(".missing.txt")
        with open(miss_path, "w", encoding="utf-8") as mf:
            mf.write("\n".join(missing_files))
        print(f"Missing list → {miss_path}")
    if skipped:
        skip_path = out_path.with_suffix(".skipped.txt")
        with open(skip_path, "w", encoding="utf-8") as sf:
            sf.write("\n".join(skipped))
        print(f"Skipped {len(skipped)} file(s). Details → {skip_path}")
    print(f"Wrote: {out_path}")

if __name__ == "__main__":
    main()
