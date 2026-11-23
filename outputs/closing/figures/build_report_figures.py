"""Draw column-width figures for the ELEC3801 final report."""
from argparse import ArgumentParser
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

BLUE = '#174977'
GRAY = '#20354A'


def architecture(output):
    fig, ax = plt.subplots(figsize=(3.42, 3.14))
    ax.set(xlim=(0, 1), ylim=(0, 1))
    ax.axis('off')
    fig.subplots_adjust(0, 0, 1, 1)
    steps = [
        'PDF and DOCX sources\nFile hash, standard number, edition, page or paragraph',
        'Indexing\nText chunks, BM25 index and BGE-M3 vectors',
        'Question and edition constraints\nResolve follow-ups and filter eligible sources',
        'BM25, Dense or Hybrid → Evidence Gate\nRank candidates, then screen evidence',
        'DeepSeek → citation verification\nCheck source IDs and continuous excerpts',
        'Streamlit response\nShow evidence, original location or a refusal status',
    ]
    for i, label in enumerate(steps):
        y = .877 - .166 * i
        ax.add_patch(FancyBboxPatch((.02, y), .96, .109, boxstyle='round,pad=.004,rounding_size=.018',
                                   facecolor='#EAF2F9', edgecolor='#8BAAC6', linewidth=.55))
        head, detail = label.split('\n')
        ax.text(.5, y+.075, head, color=BLUE, fontsize=9, ha='center', va='center', weight='bold')
        ax.text(.5, y+.031, detail, color=GRAY, fontsize=7.4, ha='center', va='center')
        if i < len(steps) - 1:
            ax.annotate('', xy=(.5, y-.052), xytext=(.5, y-.004),
                        arrowprops={'arrowstyle': '-|>', 'color': BLUE, 'lw': .85})
    fig.savefig(output / 'report_architecture.png', dpi=400, facecolor='white')
    plt.close(fig)


def recall_differences(data, output):
    fig, ax = plt.subplots(figsize=(3.42, 1.7))
    fig.subplots_adjust(left=.35, right=.96, top=.93, bottom=.31)
    comparisons = data['analysis']['paired_comparisons']
    for y, stem in enumerate(['B1', 'B2']):
        value = comparisons[f'B3_minus_{stem}']['recall_at_5']
        point = 100 * value['absolute_difference']
        low, high = [100 * edge for edge in value['ci_95']]
        ax.errorbar(point, y, xerr=[[point-low], [high-point]], fmt='o', color=BLUE, capsize=3, lw=1.4)
    ax.axvline(0, color='#65778A', linestyle='--', lw=.8, zorder=0)
    ax.set(yticks=[0, 1], yticklabels=['Hybrid − BM25', 'Hybrid − Dense'], ylim=(1.55, -.55),
           xlim=(-8, 35), xticks=[-5, 0, 10, 20, 30], xlabel='Recall@5 difference (percentage points)')
    ax.tick_params(axis='both', labelsize=8, length=2)
    ax.xaxis.label.set_size(8)
    ax.spines[['top', 'left', 'right']].set_visible(False)
    fig.savefig(output / 'report_paired_recall.png', dpi=400, facecolor='white')
    plt.close(fig)


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('summary', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'text.color': GRAY})
    architecture(args.output)
    recall_differences(json.loads(args.summary.read_text(encoding='utf-8')), args.output)
