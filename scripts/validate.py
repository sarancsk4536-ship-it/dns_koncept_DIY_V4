"""Validate the shared catalogue data without additional dependencies."""
import json
from pathlib import Path
from collections import Counter

root=Path(__file__).resolve().parents[1]
d=json.loads((root/'data/catalog.json').read_text(encoding='utf-8'))
nodes={}
def walk(n):
    assert n['id'] not in nodes,'Duplicate node ID'
    nodes[n['id']]=n
    assert len(n['path'])<=6,'Depth greater than six'
    for child in n['children']:
        assert child['path'][:-1]==n['path'],'Invalid parent path'
        walk(child)
walk(d['tree'])
cats={c['id']:c for c in d['categories']}
assert len(cats)==len(d['categories'])
assert len({c['name'] for c in d['categories']})==len(cats)
for c in cats.values():
    if c['hasMaster']:
        assert c['primaryNodeId'] in nodes,'Unresolved primary link'
        assert nodes[c['primaryNodeId']].get('categoryId')==c['id']
    else:
        assert not c['primaryPath'] and c['primaryNodeId'] is None
    assert sum(not p['virtual'] for p in c['placements'])==int(c['hasMaster'])
    for p in c['placements']:
        assert p['nodeId'] in nodes and nodes[p['nodeId']].get('categoryId')==c['id']
for n in nodes.values():
    if 'categoryId' in n:assert n['categoryId'] in cats
rules=json.loads((root/'data/navigation-rules.json').read_text(encoding='utf-8'))
allowed=set(rules['originalNames'])|set(rules['approvedRenames'])
for n in nodes.values():
    if n['children']:assert n['name'] in allowed,'Unapproved navigation group: '+n['name']
for forbidden in ['Садовый ручной инструмент','Монтаж натяжных потолков','Насосное оборудование','Садовая техника','Оснастка для садовой техники','Освещение рабочего места']:
    assert not any(n['name']==forbidden for n in nodes.values())
stages=next(n for n in d['tree']['children'] if n['name']=='Подбор по этапам работ')
assert len(stages['children'])==13
paths=[r['path'] for r in d['records']]
assert len(paths)==len({tuple(p) for p in paths})
assert not any('Диски отрезные, обдирочные' in p for p in paths)
assert not any('???' in p[-1] or '...' in p[-1] for p in paths)
for p in paths:
    if p[1]=='Подбор по этапам работ':
        if p[2]!='Подготовка и оснащение рабочего места':
            assert p[-1] not in ['Ящики для хранения инструмента','Аккумуляторы для электроинструмента','Наборы аккумуляторов с зарядным устройством','Адаптеры для аккумуляторов']
        if p[3:4]==['Сделать стяжку пола']:
            assert p[-1] not in ['Затирочные машины по бетону','Диски для затирочных машин','Игольчатые валики']
        if p[3:4]==['Собрать арматурный каркас']:assert p[-1]!='Ножницы электрические'
assert sum(p['status']=='Закуплено' for p in d['plans'])==11
assert (root/'downloads/DIY_catalog_updated.xlsx').is_file()
embedded=(root/'data.js').read_text(encoding='utf-8')
assert json.loads(embedded.removeprefix('window.DIY_CATALOG = ').rstrip(';\n'))==d
for file in ['index.html','styles.css','catalog.css','app.js','data.js','.nojekyll','README.md']:
    assert (root/file).is_file(),file
print(json.dumps({'result':'ok','categories':len(cats),'nodes':len(nodes),'stages':13,'max_depth':max(len(n['path']) for n in nodes.values()),'purchased':11},ensure_ascii=False))
