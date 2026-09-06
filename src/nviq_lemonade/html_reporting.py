from __future__ import annotations

import json
from html import escape


_STYLE = """
:root{color-scheme:dark;--bg:#090b10;--panel:#11151d;--panel2:#171c26;--text:#f3f6fb;--muted:#9ba8ba;--line:#2a3342;--accent:#f4c542;--good:#6ee7a8;--bad:#ff7b86;--info:#82b7ff}
*{box-sizing:border-box}body{margin:0;background:linear-gradient(180deg,#080a0f,#0d1118);color:var(--text);font:15px/1.55 ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
main{max-width:1180px;margin:0 auto;padding:36px 22px 64px}.eyebrow{color:var(--accent);font-weight:800;letter-spacing:.12em;text-transform:uppercase;font-size:12px}h1{font-size:clamp(30px,5vw,54px);line-height:1.02;margin:8px 0 10px}h2{margin:34px 0 14px}.sub{color:var(--muted);max-width:780px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin:24px 0}.card{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px}.metric{font-size:26px;font-weight:800;margin-top:4px}.label{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.08em}.good{color:var(--good)}.bad{color:var(--bad)}.info{color:var(--info)}
table{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);border-radius:14px;overflow:hidden}th,td{text-align:left;padding:12px 14px;border-bottom:1px solid var(--line);vertical-align:top}th{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.07em;background:var(--panel2)}tr:last-child td{border-bottom:0}.pill{display:inline-block;padding:3px 8px;border-radius:999px;font-size:12px;font-weight:800;background:var(--panel2)}.bar{height:8px;background:#252c38;border-radius:99px;overflow:hidden;margin-top:7px}.fill{height:100%;background:var(--accent)}code{color:#dfe8f7}.note{border-left:3px solid var(--accent);padding:10px 14px;background:var(--panel);color:var(--muted);margin:20px 0}pre{white-space:pre-wrap;word-break:break-word;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px;color:#d8e2f0}@media(max-width:720px){main{padding:24px 14px 48px}th,td{padding:10px 8px;font-size:13px}.hide-mobile{display:none}}
""".strip()


def _page(title: str, body: str) -> str:
    return (
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        f"<title>{escape(title)}</title><style>{_STYLE}</style></head><body><main>{body}</main></body></html>"
    )


def _num(value, digits: int = 1, suffix: str = "") -> str:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return f"{float(value):.{digits}f}{suffix}"
    return "—"


def _card(label: str, value: str, css_class: str = "") -> str:
    return f'<div class="card"><div class="label">{escape(label)}</div><div class="metric {css_class}">{escape(value)}</div></div>'


def single_report_html(report: dict) -> str:
    model = report.get("model", {})
    summary = report.get("summary", {})
    perf = report.get("performance", {})
    health = report.get("lemonade", {}).get("health") or {}
    model_id = str(model.get("id", "unknown"))
    pass_rate = float(summary.get("pass_rate", 0.0)) * 100.0
    pass_class = "good" if pass_rate >= 100.0 else ("bad" if pass_rate < 50.0 else "info")

    cards = "".join([
        _card("Public-suite pass rate", f"{pass_rate:.1f}%", pass_class),
        _card("Mean tokens / sec", _num(perf.get("mean_tokens_per_second"))),
        _card("Mean TTFT", _num(perf.get("mean_time_to_first_token_s"), 3, " s")),
        _card("Mean wall time", _num(perf.get("mean_wall_time_ms"), 1, " ms")),
        _card("Peak GPU", _num(perf.get("peak_gpu_percent"), 1, "%")),
        _card("Peak VRAM", _num(perf.get("peak_vram_gb"), 2, " GiB")),
        _card("Peak NPU", _num(perf.get("peak_npu_percent"), 1, "%")),
    ])

    rows = []
    for row in report.get("results", []):
        evaluation = row.get("evaluation", {})
        passed = bool(evaluation.get("pass"))
        status = "PASS" if passed else "FAIL"
        css = "good" if passed else "bad"
        rows.append(
            "<tr>"
            f"<td><code>{escape(str(row.get('case_id', '')))}</code></td>"
            f"<td>{escape(str(row.get('family', '')))}</td>"
            f"<td><span class=\"pill {css}\">{status}</span></td>"
            f"<td>{_num(row.get('wall_time_ms'), 1, ' ms')}</td>"
            f"<td>{escape(str(evaluation.get('evidence', '')))}</td>"
            "</tr>"
        )

    system_info = report.get("lemonade", {}).get("system_info")
    system_block = ""
    if system_info:
        system_block = "<h2>Local system</h2><pre>" + escape(json.dumps(system_info, indent=2, sort_keys=True)) + "</pre>"

    body = (
        '<div class="eyebrow">Noct-Tech · NVIQ × Lemonade</div>'
        f"<h1>{escape(model_id)}</h1>"
        f'<div class="sub">{escape(str(report.get("suite", "")))} · Lemonade {escape(str(health.get("version", "unknown")))} · {escape(str(model.get("recipe", "unknown")))}</div>'
        f'<div class="grid">{cards}</div>'
        '<div class="note">Behavioral results and runtime telemetry are shown together. This open report is not a full NVIQ certification or Noct-Tech Reliability Audit.</div>'
        "<h2>Case evidence</h2>"
        '<table><thead><tr><th>Case</th><th>Family</th><th>Result</th><th>Wall time</th><th>Evidence</th></tr></thead><tbody>'
        + "".join(rows)
        + "</tbody></table>"
        + system_block
    )
    return _page(f"NVIQ × Lemonade — {model_id}", body)


def comparison_html(comparison: dict) -> str:
    ranking = [str(item) for item in comparison.get("ranking", [])]
    best = str(comparison.get("best_behavioral_model") or "—")
    rows = []
    cards = []
    ordered = sorted(
        comparison.get("models", []),
        key=lambda item: ranking.index(str(item.get("model_id"))) if str(item.get("model_id")) in ranking else 10_000,
    )
    for index, row in enumerate(ordered, start=1):
        model_id = str(row.get("model_id", "unknown"))
        pass_rate = float(row.get("pass_rate", 0.0)) * 100.0
        width = max(0.0, min(100.0, pass_rate))
        cards.append(
            '<div class="card">'
            f'<div class="label">Rank {index}</div><div class="metric">{escape(model_id)}</div>'
            f'<div class="sub">{pass_rate:.1f}% behavioral pass · {_num(row.get("mean_tokens_per_second"))} tok/s</div>'
            f'<div class="bar"><div class="fill" style="width:{width:.1f}%"></div></div></div>'
        )
        rows.append(
            "<tr>"
            f"<td><strong>#{index}</strong></td>"
            f"<td>{escape(model_id)}<br><span class=\"label\">{escape(str(row.get('recipe') or 'unknown'))}</span></td>"
            f"<td><strong>{pass_rate:.1f}%</strong><br>{int(row.get('passed', 0))}/{int(row.get('cases', 0))} cases</td>"
            f"<td>{_num(row.get('mean_tokens_per_second'))}</td>"
            f"<td>{_num(row.get('mean_time_to_first_token_s'), 3, ' s')}</td>"
            f"<td>{_num(row.get('mean_wall_time_ms'), 1, ' ms')}</td>"
            f"<td>{_num(row.get('peak_gpu_percent'), 1, '%')} / {_num(row.get('peak_npu_percent'), 1, '%')}</td>"
            "</tr>"
        )

    body = (
        '<div class="eyebrow">Noct-Tech · NVIQ × Lemonade</div>'
        '<h1>Local AI comparison</h1>'
        '<div class="sub">Behavior first · speed second. The ranking prioritizes public-suite behavioral pass rate before throughput and wall-clock latency.</div>'
        f'<div class="note"><strong>Behavioral leader:</strong> {escape(best)}. A faster model does not outrank a more reliable model solely on generation speed.</div>'
        f'<div class="grid">{"".join(cards)}</div>'
        '<h2>Behavior + runtime matrix</h2>'
        '<table><thead><tr><th>Rank</th><th>Model</th><th>Behavior</th><th>Tok/s</th><th>TTFT</th><th>Wall</th><th>Peak GPU / NPU</th></tr></thead><tbody>'
        + "".join(rows)
        + "</tbody></table>"
        '<div class="note">Missing hardware metrics are shown as — because unsupported or unavailable telemetry is never guessed.</div>'
    )
    return _page("NVIQ × Lemonade — Model Comparison", body)
