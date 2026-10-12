"""Validate published navigation, bilingual cases, downloads and JS syntax."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import hashlib
import json
import os
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.ids, self.refs, self.scripts, self.downloads = [], [], [], []
        self.stack, self.errors, self.script = [], [], None
        self.language = None
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if tag == 'html':
            self.language = data.get('lang')
        if 'id' in data:
            self.ids.append(data['id'])
        self.refs.extend(data[attr] for attr in ('src', 'href') if attr in data)
        if tag == 'a' and 'download' in data:
            self.downloads.append(data.get('href'))
        if tag not in VOID:
            self.stack.append(tag)
        if tag == 'script' and data.get('type') != 'application/ld+json' and not data.get('src'):
            self.script = []

    def handle_endtag(self, tag):
        if tag == 'script' and self.script is not None:
            self.scripts.append(''.join(self.script))
            self.script = None
        if tag in VOID:
            return
        if not self.stack or self.stack.pop() != tag:
            self.errors.append(f'unexpected closing {tag} at {self.getpos()}')

    def handle_data(self, data):
        if self.script is not None:
            self.script.append(data)


def check():
    paths = [ROOT / 'index.html', ROOT / 'en.html', ROOT / 'resumes/index.html', *sorted((ROOT / 'cases').glob('*.html'))]
    pages = {path: Page(path.read_text(encoding='utf-8')) for path in paths}
    contract = json.loads((ROOT / 'scripts/site_contract.json').read_text(encoding='utf-8'))
    node = os.environ.get('SITE_NODE') or shutil.which('node')
    if not node:
        raise SystemExit('Node is required for JavaScript syntax validation (or set SITE_NODE).')
    script_count = 0
    with tempfile.TemporaryDirectory() as scratch:
        for path, page in pages.items():
            assert not page.errors and not page.stack, (str(path.relative_to(ROOT)), page.errors, page.stack)
            assert len(page.ids) == len(set(page.ids)), f'duplicate id in {path}'
            for ref in page.refs:
                parsed = urlsplit(ref)
                if parsed.scheme or parsed.netloc:
                    continue
                target = ROOT / unquote(parsed.path.lstrip('/')) if parsed.path.startswith('/') else path.parent / unquote(parsed.path)
                if not parsed.path:
                    target = path
                if target.is_dir():
                    target /= 'index.html'
                assert target.is_file(), (str(path.relative_to(ROOT)), 'missing local target', ref)
                assert target.resolve().is_relative_to(ROOT), 'local link escapes site'
                if parsed.fragment:
                    linked = pages.get(target)
                    if linked is None:
                        linked = Page(target.read_text(encoding='utf-8'))
                    assert unquote(parsed.fragment) in linked.ids, (str(path.relative_to(ROOT)), 'missing fragment', ref)
            for script in page.scripts:
                target = Path(scratch) / f'{script_count}.js'
                target.write_text(script, encoding='utf-8')
                subprocess.run([node, '--check', str(target)], check=True, capture_output=True)
                script_count += 1
        subprocess.run([node, '--check', str(ROOT / 'cases/case.js')], check=True, capture_output=True)
        script_count += 1
    projects = []
    for name in ('index.html', 'en.html'):
        ids = set(pages[ROOT / name].ids)
        assert set(contract['project_ids']) <= ids, f'removed project anchor in {name}'
        projects.append({value for value in ids if value.startswith('proj-')})
        assert 'cases' in ids
    assert projects[0] == projects[1], 'project anchor language mismatch'
    cv = pages[ROOT / 'resumes/index.html']
    assert len(cv.downloads) == 14 and len([value for value in cv.ids if value.startswith('role-')]) == 7
    for name, digest in contract['pdf_sha256'].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, f'changed archived PDF: {name}'
    for slug in ('manufacturing', 'ifc-review', 'driving'):
        en = pages[ROOT / f'cases/{slug}.html']
        zh = pages[ROOT / f'cases/{slug}-zh.html']
        assert en.language == 'en' and zh.language == 'zh-CN'
        assert f'{slug}-zh.html' in en.refs and f'{slug}.html' in zh.refs
        assert set(en.ids) == set(zh.ids), f'case section mismatch: {slug}'
    print(json.dumps({'html_pages': len(pages), 'javascript_syntax_checks': script_count,
                      'preserved_project_anchors_per_language': len(contract['project_ids']),
                      'unchanged_pdf_files': len(contract['pdf_sha256']), 'cv_roles': 7,
                      'case_language_pairs': 3, 'local_links_and_fragments': 'valid'}, indent=2))


if __name__ == '__main__':
    check()
