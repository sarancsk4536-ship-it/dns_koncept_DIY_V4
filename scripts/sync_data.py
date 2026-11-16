"""Refresh the file:// compatible copy after editing data/catalog.json."""
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
data=json.loads((root/'data/catalog.json').read_text(encoding='utf-8'))
(root/'data.js').write_text('window.DIY_CATALOG = '+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
print('data.js обновлён')
