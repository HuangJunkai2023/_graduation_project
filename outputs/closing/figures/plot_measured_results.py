"""Export measured benchmark figures from the provenance-bound summary."""
from pathlib import Path
import json
import os
import sys

ROOT = Path(__file__).resolve().parents[3]
SUPPORT = ROOT / 'project/qa_system/runtime/tooling/python-support'
sys.path.insert(0, str(SUPPORT))
os.environ['MPLCONFIGDIR'] = str(ROOT / 'project/qa_system/runtime/tooling/matplotlib-cache')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

HERE = Path(__file__).resolve().parent
SOURCE = ROOT / 'project/qa_system/runtime/research/measured_results.json'
data = json.loads(SOURCE.read_text(encoding='utf-8'))
if data.get('status') != 'source_reviewed':
    raise ValueError('A completed source-reviewed measurement summary is required')
font_manager.fontManager.addfont('C:/Windows/Fonts/calibri.ttf')
plt.rcParams.update({'font.family': 'Calibri', 'font.size': 10, 'axes.spines.top': False,
                     'axes.spines.right': False, 'svg.fonttype': 'none', 'pdf.fonttype': 42})


def save(figure, stem):
    for extension in ['png', 'svg', 'pdf']:
        output = HERE / f'{stem}.{extension}'
        figure.savefig(output, dpi=300, bbox_inches='tight', facecolor='white')
        if extension == 'svg':
            output.write_text('\n'.join(line.rstrip() for line in output.read_text(encoding='utf-8').splitlines()) + '\n',
                              encoding='utf-8')
    plt.close(figure)


labels = ['B1', 'B2', 'B3', 'A1', 'A2']
names = ['BM25', 'Dense', 'Hybrid', 'Hybrid\nno edition check', 'Hybrid\nno Gate']
x = np.arange(len(labels))
figure, axes = plt.subplots(figsize=(8.0, 4.4), layout='constrained')
for offset, metric, title, colour, hatch in [
    (-.18, 'recall_at_5', 'Recall@5', '#194B8C', ''),
    (.18, 'answer_correctness', 'Complete answer correctness', '#16827F', '//'),
]:
    values = [100 * data['configurations'][label][metric]['value'] for label in labels]
    bars = axes.bar(x + offset, values, .34, label=title, color=colour,
                    edgecolor='white', linewidth=.7, hatch=hatch)
    axes.bar_label(bars, labels=[f'{v:.1f}' for v in values], padding=3, fontsize=9)
axes.set_xticks(x, names)
axes.set_ylim(0, 106)
axes.set_yticks([0,20,40,60,80,100])
axes.set_ylabel('Score (%)')
axes.set_title('Retrieval and complete answers on 64 answerable test questions', pad=30)
axes.legend(loc='upper center', bbox_to_anchor=(.5,1.105), ncol=2, frameon=False)
axes.grid(axis='y', alpha=.2)
axes.set_axisbelow(True)
figure.supxlabel('Assistant source review; first attempts retained', fontsize=9)
save(figure, 'measured_retrieval_and_correctness')

comparisons = ['B3_minus_B1','B3_minus_B2','B3_minus_A1','B3_minus_A2']
display = ['Hybrid - BM25', 'Hybrid - Dense', 'Hybrid - no edition check', 'Hybrid - no Gate']
figure, panels = plt.subplots(1, 2, figsize=(9.2, 3.5), layout='constrained', sharey=True)
for axes, metric, title in zip(panels, ['recall_at_5','answer_correctness'],
                             ['Recall@5 difference','Correctness difference']):
    rows = [data['analysis']['paired_comparisons'][comparison][metric] for comparison in comparisons]
    points = np.asarray([row['absolute_difference'] * 100 for row in rows])
    low = np.asarray([row['ci_95'][0] * 100 for row in rows])
    high = np.asarray([row['ci_95'][1] * 100 for row in rows])
    y = np.arange(len(rows))
    axes.errorbar(points, y, xerr=np.vstack([points-low, high-points]),
                  fmt='o', color='#194B8C', capsize=4, markersize=5)
    axes.axvline(0, color='#6B7280', linestyle='--', linewidth=1)
    axes.set_yticks(y, display)
    axes.set_xlim(-10,40)
    axes.set_xlabel('Absolute difference (percentage points)')
    axes.set_title(title)
    axes.grid(axis='x', alpha=.2)
panels[0].invert_yaxis()
figure.supxlabel('Paired group bootstrap 95% intervals; seed 3801; 2000 resamples; 50 groups', fontsize=9)
save(figure, 'paired_differences_with_uncertainty')
print('Exported two measured figures as PNG, SVG and PDF.')
