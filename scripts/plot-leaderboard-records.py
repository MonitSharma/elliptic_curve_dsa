"""Validate a hashed public snapshot and regenerate the README figures offline.

Use --refresh to download new API data. Default: reproduce committed evidence.
"""
from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from collections import Counter
import argparse
import gzip
import hashlib
import json
import os
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR', str(ROOT / '.tools/matplotlib'))
os.environ.setdefault('XDG_CACHE_HOME', str(ROOT / '.tools/cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter, FixedLocator
import matplotlib.dates as mdates

TZ = ZoneInfo('Asia/Singapore')
API = 'https://api.ecdsa.fail/api/benchmarks/1ffb695a-309b-46b6-a728-2f97d8c7be74'
INK, MUTED, TEAL, GOLD = '#172c43', '#627184', '#087f78', '#b76b25'
GRID, CLOUD = '#e5eaf0', '#aebbc9'


def q(record):
    return record['officialMetrics']['qubits']


def t(record):
    return record['officialMetrics']['toffoli']


def when(record):
    return datetime.fromisoformat(record['createdAt'].replace('Z', '+00:00')).astimezone(TZ)


def eligible(record):
    metrics = record.get('officialMetrics') or {}
    return ((record['status'] == 'accepted' or
             (record['status'] == 'rejected' and
              record.get('rejectionReason') == 'score did not improve current best'))
            and record.get('officialScore') is not None
            and metrics.get('qubits', 0) > 0 and metrics.get('toffoli', 0) > 0)


def pareto(records):
    """One earliest representative for each nondominated resource pair."""
    frontier = []
    for record in sorted(records, key=lambda s: (q(s), t(s), s['createdAt'], s['id'])):
        if not frontier or t(record) < t(frontier[-1]):
            frontier.append(record)
    return frontier


def compact(record):
    keys = ['id', 'solverUsername', 'status', 'rejectionReason', 'officialScore',
            'officialMetrics', 'createdAt', 'submissionCommitSha']
    return {key: record.get(key) for key in keys}


def refresh(snapshot):
    payloads = {}
    for name, url in [('submissions.json.gz', API + '/submissions'), ('benchmark.json', API)]:
        with urlopen(url, timeout=60) as response:
            payloads[name] = (url, response.read())
    # Validate both responses before replacing the saved snapshot.
    if 'submissions' not in json.loads(payloads['submissions.json.gz'][1]):
        raise ValueError('Missing submissions in API response')
    if 'benchmark' not in json.loads(payloads['benchmark.json'][1]):
        raise ValueError('Missing benchmark in API response')
    manifest = {'retrieved_at': datetime.now(TZ).isoformat(), 'timezone': str(TZ),
                'site': 'https://ecdsa.fail/', 'files': {}}
    snapshot.mkdir(parents=True, exist_ok=True)
    for name, (url, data) in payloads.items():
        (snapshot / name).write_bytes(gzip.compress(data, mtime=0) if name.endswith('.gz') else data)
        manifest['files'][name] = {'source': url, 'uncompressed_sha256': hashlib.sha256(data).hexdigest()}
    (snapshot / 'snapshot.json').write_text(json.dumps(manifest, indent=2) + '\n')


def load(snapshot):
    manifest = json.loads((snapshot / 'snapshot.json').read_text())
    loaded = {}
    for name, provenance in manifest['files'].items():
        data = (snapshot / name).read_bytes()
        if name.endswith('.gz'):
            data = gzip.decompress(data)
        if hashlib.sha256(data).hexdigest() != provenance['uncompressed_sha256']:
            raise ValueError(f'Snapshot hash mismatch: {name}')
        loaded[name] = json.loads(data)
    return loaded['submissions.json.gz']['submissions'], loaded['benchmark.json']['benchmark'], manifest


def style():
    plt.rcParams.update({
        'font.family': 'DejaVu Sans', 'font.size': 10, 'text.color': INK,
        'axes.labelcolor': INK, 'axes.edgecolor': GRID, 'axes.titlecolor': INK,
        'axes.spines.top': False, 'axes.spines.right': False,
        'axes.titleweight': 'bold', 'axes.titlepad': 17,
        'xtick.color': MUTED, 'ytick.color': MUTED,
        'xtick.major.size': 0, 'ytick.major.size': 0,
        'xtick.major.pad': 8, 'ytick.major.pad': 8,
        'axes.labelpad': 12, 'figure.facecolor': 'white', 'axes.facecolor': 'white',
        'svg.fonttype': 'none', 'svg.hashsalt': 'ecdsa-leaderboard',
    })


def decorate(ax):
    ax.grid(axis='y', color=GRID, linewidth=.8)
    ax.set_axisbelow(True)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f'{value:,.0f}'))


def heading(fig, eyebrow, title, subtitle):
    fig.text(.065, .965, eyebrow, color=TEAL, fontsize=10, weight='bold')
    fig.text(.065, .915, title, fontsize=23, weight='bold')
    fig.text(.065, .875, subtitle, fontsize=10.5, color=MUTED)


def footer(fig, date, text):
    fig.text(.065, .055, f'ECDSA.fail  /  {date} · SGT', fontsize=9, weight='bold', color=MUTED)
    fig.text(.065, .027, text, fontsize=8.3, color=MUTED)


def label(ax, record, text, xytext, color=INK):
    ax.annotate(text, (q(record), t(record) / 1e6), xytext=xytext,
                textcoords='axes fraction', fontsize=9.5, color=color,
                va='top', linespacing=1.5,
                arrowprops={'arrowstyle': '-', 'color': color, 'lw': .8,
                            'connectionstyle': 'angle3,angleA=0,angleB=90'},
                bbox={'boxstyle': 'round,pad=.35', 'fc': 'white', 'ec': 'none', 'alpha': .94})


def save(fig, output, name):
    for extension in ('png', 'svg'):
        path = output / f'{name}.{extension}'
        fig.savefig(path, dpi=200,
                    metadata={'Date': None} if extension == 'svg' else None)
        if extension == 'svg':
            path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines()) + '\n')
    plt.close(fig)


def plot_frontier(scored, frontier, best, own, output, date):
    width, gates = frontier[0], frontier[-1]
    fig, axes = plt.subplots(1, 2, figsize=(15, 8.6), gridspec_kw={'width_ratios': [1.13, 1]})
    lead_count = sum(s.get('solverUsername') == 'MonitSharma' for s in (best, gates, width))
    heading(fig, 'RESOURCE FRONTIER', f'{len(own)} Pareto points. {lead_count} leading objectives.',
            f'{len(scored):,} officially scored submissions · {len(frontier)} nondominated pairs · lower and left are better')
    cards = [('LOWEST PRODUCT', f"{best['officialScore']:,}", f"{q(best):,} Q × {t(best):,} T · {best['solverUsername']}", TEAL),
             ('FEWEST TOFFOLIS', f'{t(gates):,}', f"{q(gates):,} qubits · {gates['solverUsername']}", GOLD),
             ('FEWEST QUBITS', f'{q(width):,}', f"{t(width):,} Toffolis · {width['solverUsername']}", INK)]
    for x, (name, value, detail, color) in zip((.065, .38, .695), cards):
        fig.text(x, .808, name, fontsize=8.5, weight='bold', color=MUTED)
        fig.text(x, .762, value, fontsize=22, weight='bold', color=color)
        fig.text(x, .731, detail, fontsize=9, color=MUTED)
    for ax in axes:
        decorate(ax)
        ax.scatter([q(s) for s in scored], [t(s) / 1e6 for s in scored],
                   color=CLOUD, alpha=.27, s=15, linewidths=0, rasterized=True, zorder=1)
        ax.step([q(s) for s in frontier], [t(s) / 1e6 for s in frontier],
                where='post', color=TEAL, linewidth=1.7, zorder=3)
        ax.scatter([q(s) for s in frontier], [t(s) / 1e6 for s in frontier],
                   color=TEAL, s=14, linewidths=0, zorder=4)
        ax.scatter([q(s) for s in own], [t(s) / 1e6 for s in own],
                   color=GOLD, edgecolors='white', linewidths=1.2, s=70, zorder=5)
        ax.scatter([q(best)], [t(best) / 1e6], marker='*', s=260,
                   color=TEAL, edgecolors='white', linewidths=1, zorder=6)
        ax.set_xlabel('Peak logical qubits')
    ax = axes[0]
    ax.set_title('01   The full resource landscape', loc='left', fontsize=12)
    ax.set_yscale('log')
    ax.set_ylabel('Rounded mean executed Toffolis · log scale')
    ax.set_xlim(q(width) - 65, max(q(s) for s in scored) + 100)
    ax.set_ylim(min(t(s) for s in frontier) / 1e6 * .68, max(t(s) for s in scored) / 1e6 * 1.6)
    ax.yaxis.set_major_locator(FixedLocator([1, 10, 100, 1000]))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{v:,.0f}M'))
    ax.minorticks_off()
    label(ax, width, f'Minimum width\n{q(width):,} Q · {t(width)/1e6:,.2f}M T', (.22, .94))
    label(ax, best, f"{best['solverUsername']} · product leader\n{q(best):,} Q · {t(best):,} T", (.43, .31), TEAL)
    legend = [Line2D([], [], marker='o', ls='', color=CLOUD, markersize=5, label='Scored submissions'),
              Line2D([], [], color=TEAL, lw=1.7, label='Current Pareto frontier'),
              Line2D([], [], marker='o', ls='', color=GOLD, markersize=6, label='MonitSharma frontier points')]
    ax.legend(handles=legend, loc='upper right', frameon=False, fontsize=8.5, labelcolor=MUTED)
    ax = axes[1]
    ax.set_title('02   Gate-efficient frontier · enlarged', loc='left', fontsize=12)
    highlighted = own or [best, gates]
    low, high = min(t(s) for s in highlighted) / 1e6, max(t(s) for s in highlighted) / 1e6
    span = max(high - low, .001)
    ax.set_xlim(min(q(s) for s in highlighted) - 70, max(q(s) for s in highlighted) + 45)
    ax.set_ylim(low - span * .25, high + span * .75)
    ax.set_ylabel('Rounded mean executed Toffolis')
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{v*1000:,.0f}K'))
    positions = [(.04, .91), (.12, .52), (.53, .37), (.66, .25)]
    for s, pos in zip(sorted(own, key=q), positions):
        color = TEAL if s['id'] == best['id'] else GOLD
        name = 'Best product' if s['id'] == best['id'] else ('Fewest Toffolis' if s['id'] == gates['id'] else 'Pareto point')
        label(ax, s, f'{name}\n{q(s):,} Q · {t(s):,} T', pos, color)
    ax.text(.03, .04, 'Enlarged axes reveal small gate-count differences.', transform=ax.transAxes, fontsize=8, color=MUTED)
    footer(fig, date, 'Source: saved official API snapshot. Includes score-only rejections; excludes failures and claimed-only results. Finite benchmark evidence.')
    fig.subplots_adjust(left=.085, right=.975, bottom=.18, top=.65, wspace=.27)
    save(fig, output, 'leaderboard-frontier')


def plot_history(scored, benchmark, best, output, date):
    history, incumbent = [], float('inf')
    for record in sorted(scored, key=lambda s: (s['createdAt'], s['id'])):
        if record['officialScore'] < incumbent:
            incumbent = record['officialScore']
            history.append(record)
    previous = history[-2] if len(history) > 1 else best
    reduction = 100 * (1 - best['officialScore'] / benchmark['baselineScore'])
    delta = previous['officialScore'] - best['officialScore']
    recent = history[-8:]
    fig, axes = plt.subplots(1, 2, figsize=(15, 6.8))
    heading(fig, 'PRODUCT RECORD', f"{best['officialScore']:,} qubit–Toffolis",
            f"{best['solverUsername']} · {reduction:.2f}% below the challenge baseline · {delta:,} below the preceding product record")
    for ax, entries, factor in [(axes[0], history, 1e9), (axes[1], recent, 1e6)]:
        decorate(ax)
        dates = [when(s) for s in entries]
        values = [s['officialScore'] / factor for s in entries]
        ax.step(dates, values, where='post', color=TEAL, lw=2)
        ax.scatter(dates, values, color=TEAL, s=14, zorder=4, linewidths=0)
        ax.scatter([when(best)], [best['officialScore'] / factor], color=GOLD,
                   marker='*', s=240, edgecolors='white', linewidths=1, zorder=5)
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _, scale=factor: f'{v:,.2f}' if scale == 1e6 else f'{v:,.0f}'))
        ax.set_xlabel('Submission date · Singapore time')
        ax.spines['left'].set_visible(False)
    ax = axes[0]
    ax.set_title('01   From challenge launch to today', loc='left', fontsize=12)
    ax.set_ylabel('Best product · billions of qubit–Toffolis')
    ax.set_ylim(0, benchmark['baselineScore'] / 1e9 * 1.12)
    ax.xaxis.set_major_locator(mdates.MonthLocator(tz=TZ))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b', tz=TZ))
    ax.axhline(benchmark['baselineScore'] / 1e9, color=CLOUD, ls=(0, (3, 3)), lw=1)
    ax.text(.97, .92, f"Baseline  {benchmark['baselineScore']/1e9:.2f}B", ha='right', transform=ax.transAxes, color=MUTED, fontsize=9)
    ax.annotate(f"Current record\n{best['officialScore']/1e9:.6f}B", (when(best), best['officialScore'] / 1e9),
                xytext=(.53, .38), textcoords='axes fraction', fontsize=10, color=TEAL,
                arrowprops={'arrowstyle': '-', 'color': TEAL}, linespacing=1.6)
    ax = axes[1]
    ax.set_title('02   The latest eight product records', loc='left', fontsize=12)
    ax.set_ylabel('Best product · millions of qubit–Toffolis')
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1, tz=TZ))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b', tz=TZ))
    ax.tick_params(axis='x', labelsize=9)
    span = max(s['officialScore'] for s in recent) - best['officialScore']
    ax.set_ylim((best['officialScore'] - span * .15) / 1e6, (recent[0]['officialScore'] + span * .18) / 1e6)
    ax.set_xlim(when(recent[0]) - timedelta(hours=5), when(best) + timedelta(hours=12))
    ax.annotate(f"{best['solverUsername']}\n{best['officialScore']:,}", (when(best), best['officialScore'] / 1e6),
                xytext=(.48, .40), textcoords='axes fraction', fontsize=10, color=TEAL,
                arrowprops={'arrowstyle': '-', 'color': TEAL}, linespacing=1.6)
    ax.text(.03, .93, 'Detail view · vertical axis starts above zero', transform=ax.transAxes, fontsize=8, color=MUTED)
    footer(fig, date, 'Source: saved official API snapshot. Running minimum ordered by submission creation time; the detail panel uses an enlarged vertical scale.')
    fig.subplots_adjust(left=.085, right=.975, bottom=.20, top=.74, wspace=.28)
    save(fig, output, 'product-progress')
    return history, previous


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh', action='store_true', help='download fresh public API data before analysis')
    parser.add_argument('--snapshot-dir', type=Path, default=ROOT / 'docs/data/leaderboard')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'docs/figures')
    args = parser.parse_args()
    if args.refresh:
        refresh(args.snapshot_dir)
    records, benchmark, manifest = load(args.snapshot_dir)
    scored = [s for s in records if eligible(s)]
    if not scored:
        raise ValueError('No eligible official scores in snapshot')
    for s in scored:
        if s['officialScore'] != q(s) * t(s):
            raise ValueError(f"Official product mismatch: {s['id']}")
    frontier = pareto(scored)
    best = min(scored, key=lambda s: (s['officialScore'], s['createdAt']))
    if best['officialScore'] != benchmark['currentBestScore'] or best['officialMetrics'] != benchmark['currentBestMetrics']:
        raise ValueError('Benchmark metadata and submissions disagree; refresh the snapshot together')
    own = [s for s in frontier if s.get('solverUsername') == 'MonitSharma']
    stamp = datetime.fromisoformat(manifest['retrieved_at'])
    date = stamp.strftime('%d %B %Y').lstrip('0')
    args.output_dir.mkdir(parents=True, exist_ok=True)
    style()
    plot_frontier(scored, frontier, best, own, args.output_dir, date)
    history, previous = plot_history(scored, benchmark, best, args.output_dir, date)
    summary = {
        'snapshot_at': manifest['retrieved_at'], 'source': API + '/submissions',
        'record_count': len(records), 'status_counts': dict(Counter(s['status'] for s in records)),
        'officially_scored_count': len(scored), 'frontier_count': len(frontier),
        'benchmark_mode': benchmark['mode'], 'best': compact(best),
        'minimum_qubits': compact(frontier[0]), 'minimum_toffolis': compact(frontier[-1]),
        'highlighted_frontier': [compact(s) for s in own],
        'previous_product_record': compact(previous), 'product_record_count': len(history),
        'strict_gate_by_qubits': {str(width): (best['officialScore'] - 1) // width for width in sorted({q(s) for s in frontier})},
        'eligibility': 'accepted or score-only rejected; positive official metrics; verified Q*T equality; failures and claimed-only scores excluded',
    }
    (args.snapshot_dir / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    (args.snapshot_dir / 'frontier.json').write_text(json.dumps([compact(s) for s in frontier], indent=2) + '\n')
    titles = [name for name, record in [('minimum product', best), ('minimum Toffoli count', frontier[-1])]
              if record.get('solverUsername') == 'MonitSharma']
    ownership = (' including the ' + ' and '.join(titles)) if titles else ''
    lines = ['# Current Pareto frontier', '', f"Public snapshot: **{date}**, retrieved {stamp.strftime('%H:%M')} Singapore time.", '',
             f'{len(records):,} submissions · {len(scored):,} eligible official scores · **{len(frontier)} nondominated resource pairs**.', '',
             f"**MonitSharma holds {len(own)} current Pareto points{ownership}.** Minimum width is {q(frontier[0]):,} qubits ({frontier[0]['solverUsername']}).", '',
             'Includes accepted submissions and rejections solely for failing to improve the scalar product. All included products equal peak qubits × rounded mean executed Toffolis. Benchmark failures, other rejection categories and claimed-only results are excluded. A passing finite packet does not prove correctness for all inputs.', '',
             '![Current resource frontier](figures/leaderboard-frontier.png)', '',
             '[Result details and provenance](leaderboard-results.md) · [Official source](' + API + '/submissions) · [Saved data](data/leaderboard/README.md)', '',
             '| Qubits | Rounded Toffolis | Product | Solver | Submission |', '|---:|---:|---:|---|---|']
    for s in frontier:
        solver = f"**{s['solverUsername']}**" if s in own else s['solverUsername']
        lines.append(f"| {q(s):,} | {t(s):,} | {s['officialScore']:,} | {solver} | [{s['id'][:8]}](https://api.ecdsa.fail/api/submissions/{s['id']}) |")
    (ROOT / 'docs/frontier-results.md').write_text('\n'.join(lines) + '\n')
    # Keep the original local paths current for existing analysis notebooks.
    legacy = ROOT / 'research-output'
    legacy.mkdir(exist_ok=True)
    (legacy / 'leaderboard-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    (legacy / 'derived-frontier.json').write_text(json.dumps(frontier, indent=2) + '\n')
    for name in ('leaderboard-frontier', 'product-progress'):
        for ext in ('png', 'svg'):
            (legacy / f'{name}.{ext}').write_bytes((args.output_dir / f'{name}.{ext}').read_bytes())
    print(json.dumps({k: summary[k] for k in ('snapshot_at', 'record_count', 'officially_scored_count', 'frontier_count', 'best', 'minimum_toffolis')}, indent=2))


if __name__ == '__main__':
    main()
