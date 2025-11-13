#!/usr/bin/env python3
import argparse
import pandas as pd
import numpy as np
from pathlib import Path

TRANSFORMS = {
    "copy": lambda s: s,
    "to_bool": lambda s: pd.to_numeric(s, errors="coerce").fillna(0.0).apply(lambda x: 1 if x > 0 else 0),
    "invert_bool": lambda s: pd.to_numeric(s, errors="coerce").fillna(0.0).apply(lambda x: 0 if x > 0 else 1),
    "gt_zero": lambda s: pd.to_numeric(s, errors="coerce").fillna(0.0).apply(lambda x: 1 if x > 0 else 0),
    "eq_zero": lambda s: pd.to_numeric(s, errors="coerce").fillna(0.0).apply(lambda x: 1 if x == 0 else 0),
}

def read_csv_robust(path, delimiter=None, encoding="utf-8", on_bad_lines="error", ntry=4):
    kwargs = dict(encoding=encoding, on_bad_lines=on_bad_lines)
    if delimiter:
        kwargs["sep"] = delimiter
    try:
        return pd.read_csv(path, **kwargs)
    except Exception as e1:
        last_err = e1
    try:
        return pd.read_csv(path, engine="python", sep=delimiter or None, **kwargs)
    except Exception as e2:
        last_err = e2
    try:
        return pd.read_csv(path, engine="python", sep=delimiter or ",", quotechar='"', escapechar='\\', **kwargs)
    except Exception as e3:
        last_err = e3
    try:
        kwargs_l1 = dict(kwargs)
        kwargs_l1["encoding"] = "latin-1"
        return pd.read_csv(path, engine="python", sep=delimiter or None, **kwargs_l1)
    except Exception as e4:
        last_err = e4
    raise last_err

def load_mapping(mapping_path: Path, dataset: str) -> pd.DataFrame:
    m = pd.read_csv(mapping_path, comment="#").fillna("")
    m = m[m["dataset"].str.upper() == dataset.upper()]
    return m

def standardize(df: pd.DataFrame, mapping: pd.DataFrame) -> pd.DataFrame:
    df_cols_lower = {c.lower(): c for c in df.columns}
    out = pd.DataFrame(index=df.index)
    simple_rows = mapping[~mapping["transform"].eq("sum_or_max")]
    for _, row in simple_rows.iterrows():
        std = row["standard_name"]
        orig = row["original_name"]
        tr = row["transform"]
        src_col = df_cols_lower.get(orig.lower())
        if src_col is None or src_col not in df.columns:
            out[std] = out.get(std, pd.Series(index=df.index, dtype="float64"))
            continue
        series = df[src_col]
        if tr not in TRANSFORMS:
            raise ValueError(f"Unknown transform: {tr} for {orig} -> {std}")
        out[std] = TRANSFORMS[tr](series)
    combo = mapping[mapping["transform"].eq("sum_or_max")]
    for std in combo["standard_name"].unique():
        rows = combo[combo["standard_name"] == std]
        vals = []
        for _, r in rows.iterrows():
            orig = r["original_name"]
            src_col = df_cols_lower.get(orig.lower())
            if src_col is None or src_col not in df.columns:
                continue
            vals.append(pd.to_numeric(df[src_col], errors="coerce").fillna(0))
        if len(vals) == 0:
            out[std] = out.get(std, pd.Series(index=df.index, dtype="float64"))
        else:
            stacked = pd.concat(vals, axis=1)
            out[std] = stacked.max(axis=1)
    return out

def main():
    ap = argparse.ArgumentParser(description="Standardize phishing URL features across datasets A/B/C using a mapping file (robust CSV reader).")
    ap.add_argument("--input", required=True, help="Path to original CSV")
    ap.add_argument("--dataset", required=True, choices=["A","B","C"], help="Which dataset schema the input follows")
    ap.add_argument("--mapping", required=True, help="Path to mapping CSV")
    ap.add_argument("--output", required=True, help="Where to write the standardized CSV")
    ap.add_argument("--keep_original", action="store_true", help="Append original columns (debug)")
    ap.add_argument("--delimiter", default=None, help="Force delimiter (e.g., ',', ';', '\t')")
    ap.add_argument("--encoding", default="utf-8", help="File encoding (default utf-8; try latin-1 if needed)")
    ap.add_argument("--on_bad_lines", default="error", choices=["error","warn","skip"], help="How to handle malformed rows")
    args = ap.parse_args()

    inp = Path(args.input)
    outp = Path(args.output)
    mp = Path(args.mapping)

    df = read_csv_robust(inp, delimiter=args.delimiter, encoding=args.encoding, on_bad_lines=args.on_bad_lines)
    mapping = load_mapping(mp, args.dataset)
    std = standardize(df, mapping)

    final = pd.concat([std, df], axis=1) if args.keep_original else std

    outp.parent.mkdir(parents=True, exist_ok=True)
    final.to_csv(outp, index=False)
    print(f"Saved standardized file to {outp} with {final.shape[1]} columns and {final.shape[0]} rows.")

if __name__ == "__main__":
    main()
