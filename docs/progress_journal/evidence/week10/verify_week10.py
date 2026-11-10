"""Read-only presentation evidence audit; no model requests or corpus processing."""
from pathlib import Path
from datetime import date
import hashlib,json,re,subprocess,zipfile
from xml.etree import ElementTree as E

root=Path(__file__).resolve().parents[4]
out=Path(__file__).resolve().parent
deck=root/'outputs/proposal-defense/v7-5min-visual'
files=[deck/'OCS_Proposal_Defense_EN_5min_SWJTU_Visual.pptx',deck/'OCS_Proposal_Defense_EN_5min_SWJTU_Visual.pdf',deck/'OCS_Proposal_Defense_CN_EN_Script_5min.md',deck/'source/content_5min.json',deck/'validation/final-checks.json',deck/'validation/powerpoint-layout.json']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
z=zipfile.ZipFile(files[0]);ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
slide_names=[n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)]
note_names=[n for n in z.namelist() if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml',n)]
rows=json.loads(files[3].read_text(encoding='utf-8'))
clean=lambda s:re.sub(r'\s+','',s)
notes=[''.join(n.text or '' for n in E.fromstring(z.read(f'ppt/notesSlides/notesSlide{i}.xml')).findall('.//a:t',ns)) for i in range(1,21)]
retained=json.loads(files[4].read_text(encoding='utf-8'))
layout=json.loads(files[5].read_text(encoding='utf-8-sig'))
snapshot={
 'recorded_on':'2026-11-10','activity_date_of_retained_deck':'2026-11-09',
 'method':'Read-only ZIP/XML and JSON inspection; hashes; Git commit metadata. No rerender or QA-system test.',
 'artifact_commit':subprocess.check_output(['git','show','-s','--format=%H %aI %s','f1ebd28'],cwd=root,text=True).strip(),
 'observations':{'pptx_slides':len(slide_names),'notes_parts':len(note_names),'main_slides':sum(r['seconds']>0 for r in rows),'backup_slides':sum(r['seconds']==0 for r in rows),'allocated_seconds':sum(r['seconds'] for r in rows),'bilingual_note_matches':sum(clean(r['chinese']) in clean(n) and clean(r['english']) in clean(n) for r,n in zip(rows,notes)),'retained_delivery_checks_passed':sum(retained['checks'].values()),'retained_delivery_checks_total':len(retained['checks']),'retained_PowerPoint_overflow_flags':layout['overflowCount']},
 'exact_note_mismatch_pages':[r['page'] for r,n in zip(rows,notes) if not (clean(r['chinese']) in clean(n) and clean(r['english']) in clean(n))],
 'readback_finding':'Slide 5 English note abbreviates the opening sentence relative to the JSON/script. All 20 note parts are present; 19 are exact bilingual matches. Deck left unchanged during journal preparation.',
 'files':{str(p.relative_to(root)).replace('\\','/'):{'sha256':sha(p),'bytes':p.stat().st_size} for p in files},
 'limits':['Not an application test or formal RQ evaluation.','300 seconds is allocated timing, not a measured rehearsal.','No new live API request, extraction audit, corpus acceptance, expense or actual working-hour measurement.','The untracked speech DOCX is excluded; its authorship and completion were not inspected.'],
}
(out/'artifact_audit.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(snapshot['observations']))

from urllib.parse import unquote
journal=root/'docs/progress_journal/WEEK_10.md'
s=journal.read_text(encoding='utf-8')
body=s[s.index('# Progress – Week 10'):]
plain=re.sub(r'[|#*`]+',' ',body)
plain=re.sub(r'^\s*-{3,}.*$','',plain,flags=re.M)
count=len(plain.split())
s=re.sub(r'^word_count_rendered_whitespace:.*\n','',s,flags=re.M)
s=s.replace('published_at: null','published_at: null\nword_count_rendered_whitespace: '+str(count))
journal.write_text(s,encoding='utf-8')
missing=[]
for f in [journal,out/'README.md']:
 for link in re.findall(r'\]\(([^)]+)\)',f.read_text(encoding='utf-8')):
  if not link.startswith(('http:','https:','#')) and not (f.parent/unquote(link.split('#')[0])).exists():missing.append(link)
checks={'seven_sections':len(re.findall(r'^## ',body,re.M))==7,'300_to_500_words':300<=count<=500,'Draft':'status: "Draft"' in s,'no_missing_links':not missing,'three_evidence_ids':all(v in s for v in ['E10-01','E10-04','E10-05']),'recorded_through_today':'recorded_through: "2026-11-10"' in s,'note_difference_recorded':snapshot['exact_note_mismatch_pages']==[5]}
result={'checks':checks,'word_count':count,'all_pass':all(checks.values()),'missing_links':missing}
(out/'journal_checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result))
assert all(checks.values())
