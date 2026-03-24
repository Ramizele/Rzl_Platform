from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


DEFAULT_EXCLUDED_DIRS = {
    ".git",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "node_modules",
}

DEFAULT_TEXT_EXTENSIONS = {
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".py",
    ".ps1",
    ".sh",
    ".bat",
    ".cfg",
    ".conf",
}

TEXT_BASENAMES = {
    "dockerfile",
    "makefile",
    ".env",
    "readme",
    "license",
    "copying",
    ".gitignore",
    ".gitattributes",
}

DEFAULT_MAX_TEXT_BYTES = 2_000_000
DEFAULT_MAX_EDGE_EXAMPLES = 8


@dataclass(frozen=True)
class SweepProfile:
    excluded_dirs: frozenset[str]
    text_extensions: frozenset[str]
    bucket_aliases: dict[str, str]
    primary_buckets: tuple[str, ...]


def _normalize_path_token(value: str) -> str:
    return value.strip().replace("\\", "/").strip("/")


def _normalize_bucket_name(value: str) -> str:
    cleaned = _normalize_path_token(value)
    if not cleaned:
        return "_root"
    return cleaned.split("/", 1)[0]


def _to_rel_posix(path: Path, root: Path) -> str:
    return Path(os.path.relpath(path, root)).as_posix()


def _load_profile(path: Path | None) -> SweepProfile:
    excluded_dirs = set(DEFAULT_EXCLUDED_DIRS)
    text_extensions = set(DEFAULT_TEXT_EXTENSIONS)
    bucket_aliases: dict[str, str] = {}
    primary_buckets: list[str] = []

    if path and path.exists():
        payload = json.loads(path.read_text(encoding="utf-8-sig", errors="replace"))

        for raw in payload.get("excluded_dirs", []):
            value = str(raw).strip()
            if value:
                excluded_dirs.add(value)

        for raw in payload.get("text_extensions", []):
            value = str(raw).strip().lower()
            if value and not value.startswith("."):
                value = f".{value}"
            if value:
                text_extensions.add(value)

        for alias_raw, canonical_raw in dict(payload.get("bucket_aliases", {})).items():
            alias = _normalize_bucket_name(str(alias_raw))
            canonical = _normalize_bucket_name(str(canonical_raw))
            if alias and canonical:
                bucket_aliases[alias] = canonical

        for raw in payload.get("primary_buckets", []):
            bucket = _normalize_bucket_name(str(raw))
            if bucket and bucket not in primary_buckets:
                primary_buckets.append(bucket)

    return SweepProfile(
        excluded_dirs=frozenset(excluded_dirs),
        text_extensions=frozenset(text_extensions),
        bucket_aliases=bucket_aliases,
        primary_buckets=tuple(primary_buckets),
    )


def _is_excluded(path: Path, root: Path, excluded_dirs: frozenset[str]) -> bool:
    try:
        rel = path.relative_to(root)
    except ValueError:
        return True
    return any(part in excluded_dirs for part in rel.parts)


def _collect_files(root: Path, excluded_dirs: frozenset[str]) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if _is_excluded(path, root, excluded_dirs):
            continue
        files.append(path)
    return sorted(files, key=lambda p: p.as_posix())


def _bucket_of_rel(rel: str, aliases: dict[str, str]) -> str:
    parts = rel.split("/")
    if len(parts) <= 1:
        return "_root"
    top = parts[0]
    return aliases.get(top, top)


def _asset_category(rel: str) -> str:
    p = Path(rel)
    name = p.name.lower()
    lower = rel.lower()
    suffix = p.suffix.lower()

    if name.startswith("agents") and suffix == ".md":
        return "agent_doc"
    if name.startswith("readme") and suffix == ".md":
        return "readme"
    if "ruleset" in lower or "/rulesets/" in lower or "/ruleset/" in lower:
        return "ruleset"
    if name.startswith("wf_") or "/workflows/" in lower or "/workflow/" in lower:
        return "workflow"
    if name.startswith("pipeline") or "/pipeline/" in lower:
        return "pipeline"
    if suffix in {".py", ".ps1", ".sh", ".bat"}:
        return "script"
    if suffix in {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf"}:
        return "config"
    if suffix in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".pdf", ".mp3", ".mp4", ".mov", ".wav"}:
        return "media"
    if suffix == ".md":
        return "markdown_doc"
    if not suffix:
        return "no_extension"
    return f"ext:{suffix}"


def _detect_git_tracked(root: Path) -> set[str]:
    if not (root / ".git").exists():
        return set()
    try:
        output = subprocess.check_output(
            ["git", "-c", "safe.directory=*", "-C", str(root), "ls-files"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return set()
    tracked: set[str] = set()
    for line in output.splitlines():
        value = line.strip().replace("\\", "/")
        if value:
            tracked.add(value)
    return tracked


def _is_text_file_candidate(path: Path, rel: str, profile: SweepProfile, max_text_bytes: int) -> bool:
    if path.stat().st_size > max_text_bytes:
        return False

    suffix = path.suffix.lower()
    if suffix in profile.text_extensions:
        return True

    name = Path(rel).name.lower()
    return name in TEXT_BASENAMES


def _safe_read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return None


def _build_orchestration_graph(
    *,
    root: Path,
    files: list[Path],
    rel_paths: list[str],
    bucket_by_rel: dict[str, str],
    profile: SweepProfile,
    max_text_bytes: int,
    max_edge_examples: int,
) -> tuple[list[dict[str, object]], list[dict[str, object]], int]:
    discovered_buckets = {bucket for bucket in bucket_by_rel.values() if bucket != "_root"}
    token_to_bucket: dict[str, str] = {bucket: bucket for bucket in discovered_buckets}

    for alias, canonical in profile.bucket_aliases.items():
        if canonical in discovered_buckets:
            token_to_bucket[alias] = canonical

    compiled = {
        token: re.compile(rf"(?<![A-Za-z0-9_]){re.escape(token)}/")
        for token in sorted(token_to_bucket)
    }

    edge_hits: Counter[tuple[str, str]] = Counter()
    edge_files: defaultdict[tuple[str, str], set[str]] = defaultdict(set)
    edge_examples: defaultdict[tuple[str, str], list[str]] = defaultdict(list)
    top_file_rows: list[dict[str, object]] = []

    for path, rel in zip(files, rel_paths):
        if not _is_text_file_candidate(path, rel, profile, max_text_bytes):
            continue
        text = _safe_read_text(path)
        if text is None:
            continue

        source_bucket = bucket_by_rel[rel]
        file_hits = 0
        target_buckets: set[str] = set()

        for token, regex in compiled.items():
            match_count = len(regex.findall(text))
            if match_count <= 0:
                continue

            target_bucket = token_to_bucket[token]
            if target_bucket == source_bucket:
                continue

            edge = (source_bucket, target_bucket)
            edge_hits[edge] += match_count
            edge_files[edge].add(rel)
            if len(edge_examples[edge]) < max_edge_examples and rel not in edge_examples[edge]:
                edge_examples[edge].append(rel)

            file_hits += match_count
            target_buckets.add(target_bucket)

        if target_buckets:
            top_file_rows.append(
                {
                    "path": rel,
                    "source_bucket": source_bucket,
                    "cross_bucket_refs": file_hits,
                    "target_bucket_count": len(target_buckets),
                    "targets": sorted(target_buckets),
                }
            )

    edges_payload: list[dict[str, object]] = []
    for source, target in sorted(edge_hits, key=lambda k: (-edge_hits[k], k[0], k[1])):
        edges_payload.append(
            {
                "source": source,
                "target": target,
                "ref_hits": edge_hits[(source, target)],
                "files_count": len(edge_files[(source, target)]),
                "examples": edge_examples[(source, target)],
            }
        )

    top_file_rows.sort(
        key=lambda row: (
            -int(row["cross_bucket_refs"]),
            -int(row["target_bucket_count"]),
            str(row["path"]),
        )
    )

    total_cross_refs = sum(edge_hits.values())
    return edges_payload, top_file_rows, total_cross_refs


def _render_report(
    *,
    generated_at: str,
    source_root: Path,
    report_rel: str,
    snapshot_rel: str,
    tag: str,
    totals: dict[str, object],
    bucket_rows: list[dict[str, object]],
    primary_bucket_presence: list[dict[str, object]],
    categories_global: dict[str, int],
    extensions_global: dict[str, int],
    edges: list[dict[str, object]],
    top_files: list[dict[str, object]],
) -> str:
    lines: list[str] = []
    lines.append("# Bucket / Asset / Orchestration Sweep")
    lines.append("")
    lines.append(f"- generated_at: `{generated_at}`")
    lines.append(f"- source_root: `{source_root.as_posix()}`")
    lines.append(f"- tag: `{tag}`")
    lines.append(f"- report: `{report_rel}`")
    lines.append(f"- snapshot: `{snapshot_rel}`")
    lines.append("")

    lines.append("## Global totals")
    lines.append("| Metric | Value |")
    lines.append("| --- | ---: |")
    for key, value in totals.items():
        lines.append(f"| `{key}` | {value} |")
    lines.append("")

    lines.append("## Buckets")
    lines.append("| Bucket | Files | Tracked | Local-only | Size MB |")
    lines.append("| --- | ---: | ---: | ---: | ---: |")
    for row in bucket_rows:
        size_mb = float(row["size_bytes"]) / (1024 * 1024)
        lines.append(
            f"| `{row['bucket']}` | {row['files']} | {row['tracked_files']} | {row['local_only_files']} | {size_mb:.2f} |"
        )
    lines.append("")

    if primary_bucket_presence:
        lines.append("## Primary bucket coverage")
        lines.append("| Bucket | Present | Files |")
        lines.append("| --- | --- | ---: |")
        for row in primary_bucket_presence:
            lines.append(f"| `{row['bucket']}` | {row['present']} | {row['files']} |")
        lines.append("")

    lines.append("## Asset categories (global)")
    lines.append("| Category | Count |")
    lines.append("| --- | ---: |")
    for category, count in sorted(categories_global.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"| `{category}` | {count} |")
    lines.append("")

    lines.append("## Extensions (global)")
    lines.append("| Extension | Count |")
    lines.append("| --- | ---: |")
    for ext, count in sorted(extensions_global.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"| `{ext}` | {count} |")
    lines.append("")

    lines.append("## Orchestration edges")
    if not edges:
        lines.append("- No cross-bucket references detected.")
    else:
        lines.append("| Source | Target | Ref hits | Files |")
        lines.append("| --- | --- | ---: | ---: |")
        for row in edges:
            lines.append(
                f"| `{row['source']}` | `{row['target']}` | {row['ref_hits']} | {row['files_count']} |"
            )
    lines.append("")

    lines.append("## Top orchestration files")
    if not top_files:
        lines.append("- No orchestration files detected.")
    else:
        lines.append("| File | Source bucket | Cross refs | Target buckets |")
        lines.append("| --- | --- | ---: | ---: |")
        for row in top_files[:30]:
            lines.append(
                f"| `{row['path']}` | `{row['source_bucket']}` | {row['cross_bucket_refs']} | {row['target_bucket_count']} |"
            )
    lines.append("")

    lines.append("## Next run")
    lines.append(
        "- `python platform/tools/bucket_asset_orchestration_sweep.py --root <path_repo> --output-dir <report_dir> --tag <id>`"
    )
    lines.append("")
    return "\n".join(lines)


def run() -> int:
    parser = argparse.ArgumentParser(description="Sweep buckets, assets and cross-bucket orchestration references.")
    parser.add_argument("--root", default=".", help="Filesystem root to scan.")
    parser.add_argument("--output-dir", default="platform/reports/sweeps", help="Directory where report+snapshot are written.")
    parser.add_argument(
        "--profile",
        default="platform/config/sweep_profile_template.json",
        help="Optional JSON profile with aliases, exclusions and primary buckets.",
    )
    parser.add_argument("--tag", default="", help="Output tag. Defaults to scanned root folder name.")
    parser.add_argument("--max-text-bytes", type=int, default=DEFAULT_MAX_TEXT_BYTES, help="Max text file size to parse.")
    parser.add_argument("--max-edge-examples", type=int, default=DEFAULT_MAX_EDGE_EXAMPLES, help="Max example paths per edge.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Invalid --root: {root.as_posix()}")

    profile_path = Path(args.profile).resolve() if args.profile else None
    profile = _load_profile(profile_path if profile_path and profile_path.exists() else None)

    files = _collect_files(root, profile.excluded_dirs)
    rel_paths = [_to_rel_posix(path, root) for path in files]
    tracked = _detect_git_tracked(root)

    bucket_by_rel: dict[str, str] = {}
    bucket_file_count: Counter[str] = Counter()
    bucket_size_bytes: Counter[str] = Counter()
    bucket_tracked_count: Counter[str] = Counter()
    category_global: Counter[str] = Counter()
    category_by_bucket: defaultdict[str, Counter[str]] = defaultdict(Counter)
    ext_global: Counter[str] = Counter()
    ext_by_bucket: defaultdict[str, Counter[str]] = defaultdict(Counter)

    for path, rel in zip(files, rel_paths):
        bucket = _bucket_of_rel(rel, profile.bucket_aliases)
        bucket_by_rel[rel] = bucket

        size_bytes = path.stat().st_size
        bucket_file_count[bucket] += 1
        bucket_size_bytes[bucket] += size_bytes

        if rel in tracked:
            bucket_tracked_count[bucket] += 1

        category = _asset_category(rel)
        category_global[category] += 1
        category_by_bucket[bucket][category] += 1

        ext = path.suffix.lower() if path.suffix else "(no_ext)"
        ext_global[ext] += 1
        ext_by_bucket[bucket][ext] += 1

    edges, top_files, total_cross_refs = _build_orchestration_graph(
        root=root,
        files=files,
        rel_paths=rel_paths,
        bucket_by_rel=bucket_by_rel,
        profile=profile,
        max_text_bytes=args.max_text_bytes,
        max_edge_examples=args.max_edge_examples,
    )

    bucket_rows: list[dict[str, object]] = []
    for bucket in sorted(bucket_file_count, key=lambda b: (-bucket_file_count[b], b)):
        files_total = bucket_file_count[bucket]
        tracked_files = bucket_tracked_count.get(bucket, 0)
        bucket_rows.append(
            {
                "bucket": bucket,
                "files": files_total,
                "tracked_files": tracked_files,
                "local_only_files": files_total - tracked_files,
                "size_bytes": bucket_size_bytes[bucket],
                "asset_categories": dict(
                    sorted(category_by_bucket[bucket].items(), key=lambda kv: (-kv[1], kv[0]))
                ),
                "extensions": dict(
                    sorted(ext_by_bucket[bucket].items(), key=lambda kv: (-kv[1], kv[0]))
                ),
            }
        )

    primary_bucket_presence: list[dict[str, object]] = []
    for bucket in profile.primary_buckets:
        files_total = int(bucket_file_count.get(bucket, 0))
        primary_bucket_presence.append(
            {
                "bucket": bucket,
                "present": "yes" if files_total > 0 else "no",
                "files": files_total,
            }
        )

    totals = {
        "files_total": len(files),
        "buckets_total": len(bucket_rows),
        "tracked_files": int(sum(bucket_tracked_count.values())),
        "cross_bucket_edges": len(edges),
        "cross_bucket_ref_hits": total_cross_refs,
        "top_orchestration_files": len(top_files),
    }

    now = dt.datetime.now()
    stamp = now.strftime("%Y-%m-%d_%H%M%S")
    tag = re.sub(r"[^A-Za-z0-9_.-]+", "_", args.tag.strip() or root.name)
    out_dir = Path(args.output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    report_name = f"REPORT_bucket_asset_orchestration_{tag}_{stamp}.md"
    report_latest_name = f"REPORT_bucket_asset_orchestration_{tag}_latest.md"
    snapshot_name = f"SNAPSHOT_bucket_asset_orchestration_{tag}_{stamp}.json"
    snapshot_latest_name = f"SNAPSHOT_bucket_asset_orchestration_{tag}_latest.json"

    report_path = out_dir / report_name
    report_latest = out_dir / report_latest_name
    snapshot_path = out_dir / snapshot_name
    snapshot_latest = out_dir / snapshot_latest_name

    snapshot_payload = {
        "generated_at": now.strftime("%Y-%m-%dT%H:%M:%S"),
        "source_root": root.as_posix(),
        "tag": tag,
        "profile": {
            "path": profile_path.as_posix() if profile_path and profile_path.exists() else "",
            "excluded_dirs": sorted(profile.excluded_dirs),
            "text_extensions": sorted(profile.text_extensions),
            "bucket_aliases": dict(sorted(profile.bucket_aliases.items())),
            "primary_buckets": list(profile.primary_buckets),
        },
        "totals": totals,
        "buckets": bucket_rows,
        "assets": {
            "categories_global": dict(sorted(category_global.items(), key=lambda kv: (-kv[1], kv[0]))),
            "extensions_global": dict(sorted(ext_global.items(), key=lambda kv: (-kv[1], kv[0]))),
        },
        "orchestration": {
            "edges": edges,
            "top_files": top_files[:100],
        },
    }

    snapshot_path.write_text(json.dumps(snapshot_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    shutil.copyfile(snapshot_path, snapshot_latest)

    report_text = _render_report(
        generated_at=now.strftime("%Y-%m-%d %H:%M:%S"),
        source_root=root,
        report_rel=report_path.as_posix(),
        snapshot_rel=snapshot_path.as_posix(),
        tag=tag,
        totals=totals,
        bucket_rows=bucket_rows,
        primary_bucket_presence=primary_bucket_presence,
        categories_global=dict(sorted(category_global.items(), key=lambda kv: (-kv[1], kv[0]))),
        extensions_global=dict(sorted(ext_global.items(), key=lambda kv: (-kv[1], kv[0]))),
        edges=edges,
        top_files=top_files,
    )
    report_path.write_text(report_text, encoding="utf-8")
    report_latest.write_text(report_text, encoding="utf-8")

    print(
        "Sweep complete: files={files} buckets={buckets} edges={edges} report={report}".format(
            files=len(files),
            buckets=len(bucket_rows),
            edges=len(edges),
            report=report_latest.as_posix(),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
