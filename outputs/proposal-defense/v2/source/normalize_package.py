"""Remove redundant content-type entries for absent parts from PptxGenJS 4.0.1.

No slide text, styles, relationships or existing parts are changed.
Usage: python normalize_package.py raw.pptx candidate.pptx
"""
from pathlib import Path
import sys,zipfile,json
from lxml import etree as E

src,dst=map(Path,sys.argv[1:3])
assert src.resolve()!=dst.resolve()
with zipfile.ZipFile(src) as z:
    names=set(z.namelist())
    ct=E.fromstring(z.read('[Content_Types].xml'))
    removed=[]
    for e in list(ct):
        if e.tag.endswith('}Override') and e.get('PartName','').lstrip('/') not in names:
            removed.append(e.get('PartName'));ct.remove(e)
    with zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED) as out:
        for n in z.namelist():
            out.writestr(n,E.tostring(ct,xml_declaration=True,encoding='UTF-8',standalone=True) if n=='[Content_Types].xml' else z.read(n))
print(json.dumps({'removed_dangling_content_type_entries':len(removed),'output':str(dst)}))
