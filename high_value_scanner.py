#!/usr/bin/env python3
"""
GitHub High-Value AI Key Scanner v2 — 定向扫描
目标: Claude Pro / OpenAI Pro / Gemini / NVIDIA / Groq
策略: fork 扫描 + 深度目录 + 多语言搜索
"""

import json, re, os, time, hashlib, sys, argparse
from urllib.request import Request, build_opener
from urllib.error import HTTPError, URLError
from datetime import datetime, timedelta
from collections import defaultdict

# ═══ 高价值密钥正则 ═══
HIGH_VALUE_PATTERNS = {
    'Claude (Anthropic)':         r'sk-ant-[A-Za-z0-9_-]{40,}',
    'OpenAI Pro':                 r'sk-proj-\w{60,}',
    'OpenAI Service':             r'sk-svcacct-\w{60,}',
    'OpenAI Admin':               r'sk-admin-\w{40,}',
    'Google Gemini (AIza)':       r'AIza[0-9A-Za-z_-]{35,}',
    'Google Gemini (Gemini)':     r'gemini-[0-9A-Za-z]{30,}',
    'NVIDIA NGC':                 r'nvapi-[0-9a-fA-F-]{30,}',
    'NVIDIA API':                 r'NVIDIA_API_KEY[\s=:]+["\']?[A-Za-z0-9_-]{20,}["\']?',
    'Groq':                       r'gsk_[A-Za-z0-9_-]{30,}',
    'HuggingFace':                r'hf_[A-Za-z0-9]{30,}',
    'xAI/Grok':                   r'xai-[A-Za-z0-9]{30,}',
    'Perplexity':                 r'pplx-[A-Za-z0-9]{30,}',
}

# ═══ 高价值搜索词 ═══
# 按优先级排列
HIGH_VALUE_QUERIES = [
    # --- Fork 定向搜索 (重点) ---
    'fork:true "nvapi-" filename:.env',
    'fork:true "AIza" filename:.env',
    'fork:true "sk-proj-" filename:.env',
    'fork:true "sk-ant-" filename:env',
    'fork:true "gsk_" filename:env',
    
    # --- 按框架搜索 ---
    '"diffusers" "AIza" NOT .md',
    '"langchain" "AIza" NOT .md',
    '"llama" "nvapi-" NOT .md',
    '"openai" "sk-proj-" path:config NOT .md',
    '"autogen" "gemini" NOT .md',
    '"crewai" "gemini" NOT .md',
    
    # --- 深度路径搜索 ---
    'filename:.env.local "gemini"',
    'filename:.env.production "gemini"',
    'filename:.env.development "gemini"',
    'filename:.env.staging "gemini"',
    'filename:docker-compose.yml "gemini" NOT example',
    'filename:docker-compose.yml "nvapi" NOT example',
    'filename:docker-compose.yml "sk-proj" NOT example',
    'filename:config.json "gemini" NOT example NOT sample',
    
    # --- 按语言搜索 (非 .md 文档) ---
    '"AIza" language:python NOT .md',
    '"AIza" language:javascript NOT .md',
    '"AIza" language:typescript NOT .md',
    '"nvapi-" language:python NOT .md',
    '"nvapi-" language:go NOT .md',
    '"sk-proj-" language:python NOT .md',
    '"sk-proj-" language:javascript NOT .md',
    
    # --- 大厂项目 fork 扫描 ---
    'fork:true "GOOGLE_API_KEY" path:.env',
    'fork:true "NVIDIA_API_KEY" NOT example',
    'fork:true "OPENAI_API_KEY" "sk-proj-"',
    'fork:true "ANTHROPIC_API_KEY" path:.env',
    
    # --- 实时泄露扫描 (最近推送) ---
    'pushed:>2026-06-28 "AIza" NOT example NOT test',
    'pushed:>2026-06-28 "nvapi" NOT example NOT test',
    'pushed:>2026-06-28 "sk-proj-" NOT example NOT test',
    'pushed:>2026-06-28 "gsk_" NOT example NOT test',
    'pushed:>2026-06-28 "sk-ant-" NOT example NOT test',
    
    # --- 特定文件名扫描 ---
    'filename:.env "GEMINI_API_KEY"',
    'filename:.env "GEMINI" "API"',
    'filename:.env "NVIDIA" "API"',
    'filename:.env "OPENROUTER_API_KEY"',
    'filename:secrets.yaml gemini nvapi sk-proj',
    'filename:secrets.yml gemini nvapi',
    
    # --- Gradio / 演示项目 (常泄露) ---
    '"gradio" "gemini" env NOT sample',
    '"streamlit" "gemini" env NOT sample',
    '"gradio" "nvapi" NOT example',
]

# Colors
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
CYAN = '\033[96m'
DIM = '\033[90m'
BOLD = '\033[1m'
RESET = '\033[0m'

def green(s): return f'{GREEN}{s}{RESET}'
def yellow(s): return f'{YELLOW}{s}{RESET}'
def red(s): return f'{RED}{s}{RESET}'
def cyan(s): return f'{CYAN}{s}{RESET}'
def dim(s): return f'{DIM}{s}{RESET}'
def bold(s): return f'{BOLD}{s}{RESET}'

class Scanner:
    def __init__(self, token=''):
        self.s = self._make_session(token)
        self.seen = set()
        
    def _make_session(self, token):
        class Session:
            def __init__(self, t):
                self.headers = {}
                self._opener = build_opener()
                if t:
                    self.headers['Authorization'] = f'Bearer {t}'
                self.headers['Accept'] = 'application/vnd.github.v3+json'
                self.headers['User-Agent'] = 'HighValue-Key-Scanner/2.0'
            def get(self, url, timeout=30):
                req = Request(url, headers=dict(self.headers), method='GET')
                try:
                    with self._opener.open(req, timeout=timeout) as resp:
                        data = resp.read()
                        enc = resp.headers.get_content_charset() or 'utf-8'
                        text = data.decode(enc, errors='replace')
                        return type('R', (), {'status_code': resp.status, 'text': text, 'headers': dict(resp.headers.items())})()
                except HTTPError as e:
                    data = e.read() if hasattr(e, 'read') else b''
                    text = data.decode('utf-8', errors='replace') if data else ''
                    return type('R', (), {'status_code': getattr(e, 'code', 0), 'text': text, 'headers': dict(getattr(e, 'headers', {}).items()) if getattr(e, 'headers', None) else {}})()
                except Exception:
                    return None
        return Session(token)
    
    def _get(self, url):
        while True:
            r = self.s.get(url, timeout=30)
            if r is None:
                return None
            if r.status_code == 403 and 'rate limit' in r.text.lower():
                import math
                wt = max(int(r.headers.get('X-RateLimit-Reset', 0)) - time.time(), 60) + 5
                sys.stdout.write(f'\r    {yellow("⏳")} 限速,等{int(wt)}s...')
                sys.stdout.flush()
                time.sleep(wt)
                continue
            return r
    
    def search(self, q):
        url = f'https://api.github.com/search/code?q={self._quote(q)}&per_page=100&sort=indexed'
        r = self._get(url)
        if not r or r.status_code != 200:
            return []
        return r.json().get('items', []) if hasattr(r, 'json') else []
    
    def _quote(self, q):
        from urllib.parse import quote
        return quote(q, safe='":')
    
    def download(self, repo, path):
        for br in ('main', 'master'):
            try:
                r = self.s.get(f'https://raw.githubusercontent.com/{repo}/{br}/{path}', timeout=10)
                if r and r.status_code == 200:
                    return r.text
            except:
                continue
        return None
    
    def extract_high_value(self, content, filename=''):
        results = []
        for name, pattern in HIGH_VALUE_PATTERNS.items():
            for m in re.finditer(pattern, content):
                key = m.group(0)
                # 过滤测试/示例密钥
                if any(x in key.lower() for x in ['your-', 'example', 'test-', 'xxxx', 'sk-0000', 'sk-your']):
                    continue
                ln = content[:m.start()].count('\n') + 1
                cat = 'overseas'
                results.append({
                    'key': key,
                    'type': name,
                    'file': filename,
                    'line': ln,
                })
        return results
    
    def run(self, queries):
        print(f'\n  {bold("High-Value AI Key Scanner v2")}')
        print(f'  {dim("Target: Claude Pro / OpenAI Pro / Gemini / NVIDIA / Groq")}')
        print(f'  {bold("Queries")}: {len(queries)} | {bold("Strategy")}: Forks + Deep Path + Lang\n')
        
        all_keys = []
        total_files = 0
        
        for qi, q in enumerate(queries):
            items = self.search(q)
            nf = 0
            qkeys = 0
            
            short_q = q[:60]
            print(f'  {cyan("▶")} [{qi+1:2d}/{len(queries)}] {bold(short_q)}')
            
            for it in items:
                repo = it['repository']['full_name']
                path = it['path']
                fid = f'{repo}/{path}'
                if fid in self.seen:
                    continue
                self.seen.add(fid)
                nf += 1
                total_files += 1
                
                content = self.download(repo, path)
                if not content:
                    continue
                
                keys = self.extract_high_value(content, path)
                for k in keys:
                    k['repo'] = repo
                    k['url'] = it['repository']['html_url']
                    k['stars'] = it['repository'].get('stargazers_count', 0)
                    all_keys.append(k)
                    qkeys += 1
            
            status = f'{green("✓")} {bold(str(qkeys))} keys' if qkeys else f'{dim("✓")}'
            print(f'  {dim("└")} files:{nf}  keys:{qkeys}  total_files:{total_files}  total_keys:{bold(str(len(all_keys)))}  {status}')
            
            if qi < len(queries) - 1:
                sys.stdout.write(f'  {dim("wait 2s...")}')
                sys.stdout.flush()
                time.sleep(2)
                sys.stdout.write('\r' + ' ' * 20 + '\r')
                sys.stdout.flush()
        
        # 去重
        seen = set()
        dedup = []
        for k in all_keys:
            uid = f'{k["repo"]}{k["file"]}{k["line"]}{hashlib.sha256(k["key"].encode()).hexdigest()[:16]}'
            if uid not in seen:
                seen.add(uid)
                dedup.append(k)
        
        return all_keys, dedup


def save_results(all_keys, dedup, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    
    # 按类型分组
    by_type = defaultdict(list)
    for k in dedup:
        by_type[k['type']].append(k)
    
    # 1. 完整 TXT
    lines = []
    lines.append('=' * 66)
    lines.append('  GitHub High-Value AI Key Scan Report')
    lines.append(f'  {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    lines.append(f'  Raw: {len(all_keys):,}  Unique: {len(dedup):,}  Repos: {len(set(k["repo"] for k in dedup)):,}')
    lines.append('=' * 66)
    lines.append('')
    
    for type_name in sorted(by_type.keys()):
        entries = by_type[type_name]
        lines.append(f'')
        lines.append(f'  {"─" * 50}')
        lines.append(f'  🔑 {type_name}  ({len(entries)} 条)')
        lines.append(f'  {"─" * 50}')
        for i, k in enumerate(entries, 1):
            key_display = k['key']
            if len(key_display) > 80:
                key_display = key_display[:40] + '...' + key_display[-30:]
            lines.append(f'  [{i}] {key_display}')
            lines.append(f'       Repo: {k["repo"]}  |  Stars: {k.get("stars", 0)}')
            lines.append(f'       File: {k["file"]}:{k["line"]}')
            lines.append(f'       URL: {k.get("url", "")}')
            lines.append('')
    
    with open(os.path.join(out_dir, 'high_value_keys.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    # 2. JSON
    json_out = {
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'raw': len(all_keys),
        'unique': len(dedup),
        'repos': len(set(k['repo'] for k in dedup)),
        'keys': [{'key': k['key'], 'type': k['type'], 'repo': k['repo'], 
                   'file': k['file'], 'line': k['line'], 'url': k.get('url',''),
                   'stars': k.get('stars',0)} for k in dedup]
    }
    with open(os.path.join(out_dir, 'high_value_keys.json'), 'w', encoding='utf-8') as f:
        json.dump(json_out, f, ensure_ascii=False, indent=2)
    
    # 3. 简易 TXT (只有 key 和类型,方便直接复制)
    simple = []
    simple.append('# 高价值密钥 — 快速复制版')
    simple.append(f'# 时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    simple.append(f'# 总数: {len(dedup)} 条')
    simple.append('')
    for type_name in sorted(by_type.keys()):
        entries = by_type[type_name]
        simple.append(f'## {type_name}')
        for k in entries:
            simple.append(f'{k["key"]}  # {k["repo"]}')
        simple.append('')
    
    with open(os.path.join(out_dir, 'high_value_keys_quick.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(simple))
    
    print(f'\n  {green("✓")} {bold("高价值密钥报告")}')
    print(f'  {green("✓")} TXT: {os.path.join(out_dir, "high_value_keys.txt")}')
    print(f'  {green("✓")} JSON: {os.path.join(out_dir, "high_value_keys.json")}')
    print(f'  {green("✓")} QUICK: {os.path.join(out_dir, "high_value_keys_quick.txt")}')
    
    # 分类汇总
    print(f'\n  {bold("分类汇总")}:')
    for type_name in sorted(by_type.keys()):
        print(f'    {type_name:<30s} {len(by_type[type_name]):>4} 条')
    
    return dedup


def main():
    p = argparse.ArgumentParser(description='GitHub High-Value AI Key Scanner v2')
    p.add_argument('--token', '-t', default='', help='GitHub PAT (推荐)')
    p.add_argument('--output', '-o', default=os.path.expanduser('~/Desktop/HighValue_Scan'), help='Output dir')
    p.add_argument('--days', '-D', type=int, default=0, help='只扫最近 N 天 (0=全部)')
    
    args = p.parse_args()
    token = args.token or os.environ.get('GITHUB_TOKEN', '')
    out_dir = args.output
    
    queries = HIGH_VALUE_QUERIES
    
    # 如果指定了天数，给所有查询加上日期过滤
    if args.days > 0:
        cutoff = (datetime.now() - timedelta(days=args.days)).strftime('%Y-%m-%d')
        date_filter = f' pushed:>{cutoff}'
        queries = [q + date_filter for q in queries]
        print(f'  {dim(f"Date filter: pushed:>{cutoff} (last {args.days} days)")}')
    
    if not token:
        print(f'  {yellow("⚠ 无 Token 会严重影响扫描结果")}')
        print(f'  {dim("建议: https://github.com/settings/tokens -> classic -> public_repo")}')
    
    scanner = Scanner(token)
    all_keys, dedup = scanner.run(queries)
    
    if all_keys:
        save_results(all_keys, dedup, out_dir)
    else:
        print(f'\n  {yellow("⚠ 未找到任何高价值密钥")}')
        print('    1. 可能被限速 -> 等待或使用 Token')
        print('    2. Token 无效 -> https://github.com/settings/tokens')

if __name__ == '__main__':
    main()
