#!/usr/bin/env python3
#
# ╔══════════════════════════════════════════════════════════╗
# ║  r5hhhh2ssi;;iiiiiiiiii;r2hMMMMMMMMMMMMMhhhh5r;ii;;;;; ║
# ║  A233hhhh3Arrrrsiiiiiii2hMMMMhhMMMMMMMMMhhhhMMA;;;;;;; ║
# ║  A25555333552AXAsiiiir3MMhMMhhMMMMhhMMMMMMMMhhM5ii;;; ║
# ║  A22255555352AXXriiirhMhMMhhhMMMMMMhhMMhMMMMMMhM2iiii ║
# ║  ssssXsirsrrrrrrrrrsM3hMM3h3MhMMhMMM3hMh3MMMhhMMMhri ║
# ║  irrrrrrrrrrrrrrrriXh3MMhhh5M2hhh3MM53h53hMMhhhMMMXr ║
# ║  rrrrrrrrrrrrrrrrrrshhMH33h3hA52M5hH22hA33hhhhhhMM3h ║
# ║  rrrrrrrrrrrrrrrrrrA33HM253h53AXA32MAX223555Mhh3M3MS ║
# ║  rrrrrrrrrrrrrrrrrr3X3h33SSH3iH#9GhAhS9h;MHGM33hH3MM ║
# ║  rrrrrrrrrrrsssAAssssrr2hM3hG#99#9#H9####9SMh33523MG ║
# ║  srrsXXXXsXA553MhMHHHH2XAAAX2MS9###S##9#G5XsXsA5HSG ║
# ║  s222hG##MHSSSSSSGSSSGH2MAsAAX3S999999#G2XX2sAMHHHG ║
# ║  5HGGGS#9#SS##SS#####SSGGG5AMAs3MH##SHGG35Hh3MMMHHH ║
# ║  MHGSSS999##99#SSSSS#SGSSSSHMhh3M353HS9GH#9S#GhhMMH ║
# ║  GGSSSS##9####SSSSSSSSGGGGGGHHMh#SGS999SHSS###GMMHH ║
# ║  GGGGGGGGGGGGGGSSSSSSSSSSGGHGHM#9999#999GHSSGGSGGGH ║
# ║  HHHMHHHGGGGGGGGGHHHHMMMMS#99GMG#9999#SS9B&B9SHMhMM ║
# ║  hhhhhhhhhhhhhhh333hhHG3H9&&B&&#SG#9SS9B&&&&&GH9Gh3 ║
# ║  GitHub Crypto Leak Scanner       v2 ║
# ╚══════════════════════════════════════════════════════════╝
"""
GitHub Crypto Credential Leak Scanner
═══════════════════════════════════════
GitHub 公开仓库虚拟货币地址+私钥泄露扫描器 — 覆盖 BTC/ETH/SOL/TRX 等 20+ 链
支持完整私钥/地址/WIF/助记词提取

用法:
    python github_key_scanner.py                       # 无 token
    python github_key_scanner.py --token ghp_xxx       # 有 token 加速
    python github_key_scanner.py --token ghp_xxx --deep    # 深度扫描(46搜索词)

Token: https://github.com/settings/tokens -> classic -> public_repo
"""

import subprocess as _sp, sys as _sys, importlib as _il

try:
    import requests  # type: ignore
except ImportError:
    requests = None

import json, re, os, time, hashlib, argparse, sys, math
from urllib.parse import quote
from urllib.request import Request, build_opener
from urllib.error import HTTPError, URLError
from collections import defaultdict, Counter
from datetime import datetime

class _CompatResponse:
    def __init__(self, status_code, text='', headers=None):
        self.status_code = status_code
        self.text = text
        self.headers = headers or {}

    def json(self):
        return json.loads(self.text) if self.text else {}


class _CompatSession:
    def __init__(self):
        self.headers = {}
        self._opener = build_opener()

    def get(self, url, timeout=25):
        req = Request(url, headers=dict(self.headers), method='GET')
        try:
            with self._opener.open(req, timeout=timeout) as resp:
                data = resp.read()
                encoding = resp.headers.get_content_charset() or 'utf-8'
                text = data.decode(encoding, errors='replace')
                return _CompatResponse(resp.status, text, dict(resp.headers.items()))
        except HTTPError as e:
            data = e.read() if hasattr(e, 'read') else b''
            encoding = None
            try:
                encoding = e.headers.get_content_charset()
            except Exception:
                pass
            text = data.decode(encoding or 'utf-8', errors='replace') if data else ''
            return _CompatResponse(getattr(e, 'code', 0) or 0, text, dict(getattr(e, 'headers', {}).items()) if getattr(e, 'headers', None) else {})
        except URLError:
            return None
        except Exception:
            return None


if requests is None:
    class _RequestsCompat:
        Session = _CompatSession
    requests = _RequestsCompat()

import shutil

STARTUP_ANIMATION_SECONDS = 4.0
STARTUP_FRAME_DELAY = 0.12
STARTUP_FRAMES = [
    r"""s3hhhAXi;iriiiii;iAhMMMMMMMMMMhhh3s;ii;;;;;;;;;issriii
A5333h32XsXsiii;XhMMMhhMMMhMMMMMhMM2;;;;;iirssXA2Xrrii
A25555535AXXriiAMhMMhhMMMMhhMhMMMMMM2iiiirsA5555Ariiii
AAAAXsA2ArririsMhMMhhMhMMMMhMhhMMhMMMXiirXA5222Xsiiiii
rrrsrrrrrrrrri2hhMh3hhhMhMM3hh3MMhhMMhirsXA2AAXAsriiii
rrrrrrrrrrrrriAhMM3h3323h3H2353hhhhhMM5532XXAsrrriiiii
rrrrrrrrrrrrrr23Mh23h32s22hXA23553hhh3GGHM32Arrrrrrrii
rrrrrrrrrrrrrs52M5hHMA5MM2X2h3s33333M3HHHHhXrrrrrrrrsX
rrrrrrrrrrrrrs2Ah3h##MMB99HS9#3##Hh3MhMMH3Xrrrrrrrs3MH
rrrrrsssssAXsssrAhhhS99##G#9##9Gh3355MGHMAXXXAAAXsAhhM
srrsrrrrsA23h335Xs225M#9#HS###S3AXsX3SSGMMGGHHGHMh2553
sAX5hM5hHHGGHGSGM22sXAh#99#99S3sXsAMHGGGHHHHHGSSGGh225
5HGG#9####S####SSGS353X3HGSGGG33M3MMHHHHHMMHGGSSSSGGH3
HGSS#99#99#SSSSSGGSSHMh3H3hG9SH###GhhMHS#GHGSGHGGGSSSM
GSGGGSSSSSSSSSSSSSGGHHMG9#999#HGSS#GHGHGSSGGGGMMMHGGGG
HHHHHGHHGGGGHHHMMMG###HG#99####BB9GHMMMMMMMMMMMMMMMMMM
h33hhhhhhh333hhGShG&&&&B9##9B&&&&BM##Hh33333333333hhhh
333333555535553hhHhG##B9SH2MH#BShHhhhh5255355555555553
5555555555AAA22AAGHAAMGA;iX;;sMG5G5AAAAAAA533555555555
5533333335H9hA22AhG5AS3;hA#sh53HHhA222AAM9h3h3h333h333
AAAAAAAAAA9&&#3sA5G3h5M9h5@A2MhSGA22AX5#&&GXAAAAAA2222
rrrrrrrrrXBBB&92A2SHh3M9sH@5X3H9hA22AhB&BB#srrrrrrrrrr""",
    r"""s3hhhAXi;iiiiiii;iAhMMMMMMMMMMhhM3s;;i;;;;;;;;;issriii
A533hhh2XsXsiii;XhMMMhhMMMhMMMMMhMM2;;;;;iirsssA2Xrrii
A22555535AXXriiXMhMMhhMMMMhhMhMMMMMH2iiiirsA5555Ariiii
AAAAXsA2ArrrrisMhMMhhhhMMMMhMhhMMhMMMXiirsA5222Xsiiiii
rrrsrrrrrrrrriAhhMh33hhMhMM3hh3MMhhMMhiisXA2AAXAsriiii
irrirrrrrrrrriAhMM3h3323h3H2355hhhhhMM5532XXXsrrriiiii
rrrrrrrrrrrrrr23Mh23h32s22hXA23253hhh3HGHM32Arrrrrrrii
rrrrrrrrrrrrrs52M5hHMA2MM2X2h3s33333M3HHHHhXrrrrrrrrsX
rrrrrrrrrrrrrs2Ah3h##MM999HS9#3##Hh3MhMMH3Xrrrrrrrs5MH
rrrrrsssssAXsssrAhhhS99##G#9##9Gh3355MGHMAXXXAAXXsAhhM
srrsrrrrXA23h355XX222M#9#HS###S3AXsX3SSGMMGGHHGHMh2553
sXX5hM53HHGGHGSGM22sXAh#99#99S3sXsAhHGGGHHHHHGSSGGh225
5HGG#9####S####SSGS353X3HGSGGG53M3MHHHHHHMMHGGSSSSGGH3
HGSS##9#99#SSSSSGSSSHMh3H3hG9SH###GhMMHS#GHGSGHGGGSSSh
GGGGSSSSSSSSSSSSSGGGHHHG9##99#HGSS#GHGHGSSGGGGMMMHGGGG
HHHHHGHHGGGGHHHMMHG#9#HG9#MH###BB#GHMMMMMMMMMMMMMMMMMM
h3hhhhhhhhh333hG#B&@&&&BShhMGB&&&@@&#Hh333333333hhhhhh
333333555535555hMHGS#9&9GMGGS#&9GHHMhh5255555555555553
5555555553AAA22AAAAAAHHXHHMGGM3hXAAAAAA2AA535555555555
5533333335M9hAA222222XisHSMMSM22222222AAM9h3h3h33hh333
AAAAAAAAAX#&&#3s2222A5GGh3GG#9HA22A2AX5S&&HXAAAAAA2225
rrrrrrrrrs9&B&BAA2222AH9M35H99HA2222AMB&BB9srrrrrrrrrr""",
    r"""s3hh3AXi;iiiiiii;iAhMMMMMMMMMMMhh3s;;i;;;;;;;;;issriii
A5533h32XsXsiii;XhMMMhhMMMhMMMMMhMM2;;;;;iirXsXA2Xriii
A25555535AXXriiAMhMMhhMMMMhMMhMMMMhM2iiiirsA5555Ariiii
AAAAXXA2ArrrrisMhMMhhhMMMMMhMhhMMhMMMXiirX25222Xsiiiii
rrrsrrrrrrrrri2hhMh33hhMhMM3hh3MMhhMMhirsXA2AAXXsriiii
rrrrrrrrrrrrriAhMM3h3323h3H2353hhhhhMM5532XXAsrrriiiii
rrrrrrrrrrrrrr23Mh23h32s22hXA23253hhh3GGHM32Arrrrrrrii
rrrrrrrrrrrrrs52M5hHMA5MM2X2h3s33333M3HHHHhXrrrrrrrrsX
rrrrrrrrrrrrrs2Ah3h##MM999HS9#3##Hh3MhMMH3Xrrrrrrrs3MH
rrrrrsssssAXsssrAhhhS99##G#9##9Gh3325MGHMAXXXAAXXsAhhM
srrsrrrrXA23h355Xs225M#9#HS###S3AXsX3SSGMMGGHHGHMh2553
sXX5hM53HHGGHGSGM22sXAh#99#99S3sXsAMHGGGHHHHHGSSGGh225
5HGG#9####S####SSGG353X3HGSGGG53M3MMHHHHHMMHGGSSSSGGH3
HGSS#99#99#SSSSSGGSSHMh3H3hG9SH9##GhhMHS#GHGSGHGGGSSSM
GSGGSSSSSSSSSSSSSSGGHHMG9#999#HGS##GHGHGSSGGGGMMMHGGGG
HHHHHGHHGGGGHHHMMMH#9#HG#99####B&SMHMMMMMMMMMMMMMMMMMM
h3hhhhhhhh3333hG#MHB@&&B###9BB&BGGH&#Hh33333333333hhhh
333333555535553hMMGH##B9SM2MGSGHMGMMhh5255355555555553
5555555553AAA22AA3S3M3MX;iX;;sG5GG5XAAAAA2533555555555
5533333335H9hA2223G2GH;rhA#sMshGHHA222AAHBh3hh3333h333
AAAAAAAAXAB&&#5s2Ghh33MB32@sH9AMGG22AX3#&&HsAAAAAA2225
rrrrrrrriXBBB&#22#Ghh3H&rH@2AM2h#SAA2hB&BB#srrrrrrrrrr"""
]


def autoplay_startup_gif():
    try:
        if not STARTUP_FRAMES:
            return
        loops = max(1, int(STARTUP_ANIMATION_SECONDS / STARTUP_FRAME_DELAY / len(STARTUP_FRAMES)))
        _sys.stdout.write('\x1b[2J\x1b[H\x1b[?25l')
        _sys.stdout.flush()
        try:
            for _ in range(loops):
                for frame in STARTUP_FRAMES:
                    _sys.stdout.write('\x1b[H')
                    _sys.stdout.write(frame)
                    _sys.stdout.write('\n')
                    _sys.stdout.flush()
                    time.sleep(STARTUP_FRAME_DELAY)
        finally:
            _sys.stdout.write('\x1b[2J\x1b[H\x1b[?25h')
            _sys.stdout.flush()
    except Exception:
        pass

# ═══════ ANSI ═══════
class C:
    R='\033[91m';G='\033[92m';Y='\033[93m';B='\033[94m';M='\033[95m';C='\033[96m';W='\033[97m';D='\033[90m'
    BOLD='\033[1m';RESET='\033[0m'
def dim(s):return f'{C.D}{s}{C.RESET}'
def bold(s):return f'{C.BOLD}{s}{C.RESET}'
def red(s):return f'{C.R}{s}{C.RESET}'
def green(s):return f'{C.G}{s}{C.RESET}'
def cyan(s):return f'{C.C}{s}{C.RESET}'
def yellow(s):return f'{C.Y}{s}{C.RESET}'

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ═══════ 搜索词 ═══════
SEARCH_DEEP = [
    'filename:wallet.dat',
    'filename:keystore "address"',
    'filename:keystore "crypto"',
    'filename:UTC-- "address"',
    'filename:exported_account',
    '"mnemonic" "phrase" path:.env',
    '"seed" "phrase" path:.env',
    '"private" "key" path:.env',
    '"private" "key" path:.txt',
    '"private" "key" path:.json',
    '"wallet" "private" path:.txt',
    '"wallet" "seed" path:.json',
    '"0x" "private" "key" path:.txt',
    '"0x" "private" "key" path:.json',
    'filename:keys.txt "0x"',
    'filename:keys.txt "private"',
    'filename:keys.json "address"',
    'filename:account.json "private"',
    '"bitcoin" "private" "key" language:python',
    '"ethereum" "private" "key" language:javascript',
    '"solana" "private" "key" language:typescript',
    '"bip39" "mnemonic" language:python',
    '"bip32" "xprv" language:python',
    '"bip44" "path" path:.py',
    '"btc" "private" "key" path:.txt',
    '"eth" "private" "key" path:.txt',
    '"sol" "secret" "key" path:.json',
    '"trc20" "private" path:.txt',
    '"erc20" "private" path:.txt',
    '"bech32" "private" path:.txt',
    'filename:secret.txt "wallet"',
    'filename:backup.txt "wallet"',
    'filename:recovery.txt "seed"',
    'filename:metamask "password" path:.json',
    'filename:trustwallet "password" path:.txt',
    '"xpriv" path:.txt',
    '"xprv" path:.txt',
    '"tron" "private" "key" path:.txt',
    '"bnb" "private" "key" path:.txt',
    '"polkadot" "seed" path:.txt',
    '"aptos" "private" path:.txt',
    '"sui" "private" path:.txt',
    '"near" "private" path:.txt',
    '"ton" "private" path:.txt',
    '"cosmos" "mnemonic" path:.txt',
    '"avax" "private" path:.txt',
]
SEARCH_FAST = SEARCH_DEEP[:12]

# ═══════ 密钥正则 — 精确匹配(无变宽look-behind) ═══════
# 分两步: 1) 宽正则全量提取  2) classify_key 精确归类
# 注意：这是扫描虚拟货币地址+私钥+助记词
KEY_REGEX = re.compile(
    # === 私钥 ===
    # 比特币 WIF 私钥（5H/5J/5K/L/K/L开头, 51或52 base58字符）
    r'[5KL][1-9A-HJ-NP-Za-km-z]{50,51}'
    # 以太坊/通用 64位hex私钥（不含0x前缀，32字节）
    r'|(?<![a-fA-F0-9])[a-fA-F0-9]{64}(?![a-fA-F0-9])'
    # 16进制私钥（含0x前缀，64 hex字符）
    r'|0x[a-fA-F0-9]{64}'
    # Solana base58 私钥（88字符左右）
    r'|[1-9A-HJ-NP-Za-km-z]{86,90}'
    # === 地址 ===
    # 比特币 P2PKH 地址（1开头）
    r'|1[a-km-zA-HJ-NP-Z1-9]{25,34}'
    # 比特币 P2SH 地址（3开头）
    r'|3[a-km-zA-HJ-NP-Z1-9]{25,34}'
    # 比特币 Bech32 地址（bc1开头）
    r'|bc1[a-z0-9]{39,59}'
    # 比特币 Bech32 测试网
    r'|tb1[a-z0-9]{39,59}'
    # 以太坊/BNB/ERC20 地址（42位含0x）
    r'|0x[a-fA-F0-9]{40}'
    # 波场 TRC20 地址（T开头）
    r'|T[a-zA-HJ-NP-Z0-9]{33}'
    # Solana 地址（32-44 base58字符）
    r'|[1-9A-HJ-NP-Za-km-z]{32,44}'
    # XRP 地址（r开头）
    r'|r[1-9A-HJ-NP-Za-km-z]{25,35}'
    # Cosmos 地址（cosmos1开头）
    r'|cosmos1[a-z0-9]{38}'
    # Polkadot 地址
    r'|1[a-km-zA-HJ-NP-Z1-9]{47}'
    # Avalanche C链地址（0x开头42位）
    r'|0x[a-fA-F0-9]{40}'
    # === 扩展公钥 ===
    r'|xprv[1-9A-HJ-NP-Za-km-z]{106,108}'
    r'|xpub[1-9A-HJ-NP-Za-km-z]{106,108}'
)

def classify_key(key, context='', filename=''):
    """精确归类密钥到服务商"""
    k = key
    ctx = (context + filename).lower()

    # === 私钥检测 ===
    # 比特币 WIF 私钥
    if re.match(r'^[5KL][1-9A-HJ-NP-Za-km-z]{50,51}$', k):
        chain = 'btc' if ('btc' in ctx or 'bitcoin' in ctx) else 'BTC'
        return 'private_key', chain + '-WIF', 'critical'
    # 带0x的64位hex私钥
    if re.match(r'^0x[a-fA-F0-9]{64}$', k):
        if 'sol' in ctx or 'solana' in ctx:
            return 'private_key', 'Solana', 'critical'
        return 'private_key', 'ETH/BSC-EVM', 'critical'
    # 纯64位hex私钥（不含0x）
    if re.match(r'^[a-fA-F0-9]{64}$', k):
        return 'private_key', 'Hex-64', 'critical'
    # xprv 扩展私钥
    if k.startswith('xprv'):
        return 'private_key', 'BIP32-Extended', 'critical'
    # xpub 扩展公钥
    if k.startswith('xpub'):
        return 'public_key', 'BIP32-Extended-Pub', 'high'

    # === 地址检测 ===
    # 以太坊类地址（0x+40 hex）
    if re.match(r'^0x[a-fA-F0-9]{40}$', k):
        if 'bsc' in ctx or 'bnb' in ctx:
            return 'address', 'BNB-Chain', 'medium'
        if 'polygon' in ctx or 'matic' in ctx:
            return 'address', 'Polygon', 'medium'
        if 'avax' in ctx or 'avalanche' in ctx:
            return 'address', 'Avalanche-C', 'medium'
        if 'arbi' in ctx or 'arbitrum' in ctx:
            return 'address', 'Arbitrum', 'medium'
        if 'op' in ctx or 'optimism' in ctx:
            return 'address', 'Optimism', 'medium'
        return 'address', 'Ethereum', 'medium'

    # 比特币 P2PKH（1开头）
    if re.match(r'^1[a-km-zA-HJ-NP-Z1-9]{25,34}$', k):
        return 'address', 'Bitcoin-P2PKH', 'medium'
    # 比特币 P2SH（3开头）
    if re.match(r'^3[a-km-zA-HJ-NP-Z1-9]{25,34}$', k):
        return 'address', 'Bitcoin-P2SH', 'medium'
    # 比特币 Bech32（bc1开头）
    if k.startswith('bc1'):
        return 'address', 'Bitcoin-Bech32', 'medium'
    # 比特币测试网
    if k.startswith('tb1'):
        return 'address', 'Bitcoin-Testnet', 'low'

    # 波场 TRC20（T开头）
    if re.match(r'^T[a-zA-HJ-NP-Z0-9]{33}$', k):
        return 'address', 'TRON-TRC20', 'medium'

    # Cosmos
    if k.startswith('cosmos1'):
        return 'address', 'Cosmos', 'medium'

    # Solana 地址（base58 32-44位）
    if re.match(r'^[1-9A-HJ-NP-Za-km-z]{32,44}$', k):
        if 'sol' in ctx or 'solana' in ctx:
            return 'address', 'Solana', 'medium'
        return 'address', 'Solana-style', 'medium'

    # XRP
    if 25 <= len(k) <= 36 and k[0] in 'rR':
        return 'address', 'XRP', 'medium'
    # Polkadot
    if len(k) == 48 and k[0] == '1':
        return 'address', 'Polkadot', 'medium'

    return 'other', 'Unknown', 'low'

CAT_LABEL = {'private_key':'私钥','address':'地址','public_key':'扩展公钥','other':'其他'}
SEV_COLOR = {'critical':red,'high':yellow,'medium':cyan}

# ═══════ 高熵检测 ═══════
def shannon_entropy(s):
    if not s:return 0
    f=Counter(s);n=len(s)
    return -sum(c/n*math.log2(c/n) for c in f.values())

def detect_high_entropy(content, min_len=32, min_entropy=4.0):
    found=[]
    for m in re.finditer(r'''["'`]?([A-Za-z0-9+/=_-]{'''+str(min_len)+r''',})["'`]?''', content):
        c=m.group(1)
        if c.isdigit() or c.isalpha():continue
        if shannon_entropy(c)>=min_entropy:
            ln=content[:m.start()].count('\n')+1
            found.append((c,ln))
    return found

def mask_key(k):
    return k

def key_hash(k):
    return hashlib.sha256(k.encode()).hexdigest()[:16]

# ═══════ 扫描引擎 ═══════
class Scanner:
    def __init__(self,token=''):
        self.s=requests.Session()
        h={'Accept':'application/vnd.github.v3+json','User-Agent':'Crypto-Scanner/1.0'}
        if token:h['Authorization']=f'Bearer {token}'
        self.s.headers.update(h)
        self.rpm=30 if token else 10
        self.delay=60/self.rpm+1
        self.seen=set()

    def _get(self,url):
        while True:
            try:r=self.s.get(url,timeout=25)
            except:return None
            if r.status_code==403 and 'rate limit' in r.text.lower():
                wt=max(int(r.headers.get('X-RateLimit-Reset',0))-time.time(),60)+5
                sys.stdout.write(f'\r    {yellow(chr(0x231B))} 限速,等{int(wt)}s...');sys.stdout.flush()
                time.sleep(wt);continue
            return r

    def search(self,q):
        url=f'https://api.github.com/search/code?q={quote(q,safe=":")}&per_page=100&sort=indexed'
        r=self._get(url)
        if not r or r.status_code!=200:return[]
        return r.json().get('items',[])

    def download(self,repo,path):
        for br in('main','master'):
            try:
                r=self.s.get(f'https://raw.githubusercontent.com/{repo}/{br}/{path}',timeout=10)
                if r.status_code==200:return r.text
            except:continue
        return None

    def extract(self,content,filename=''):
        keys=[]
        for m in KEY_REGEX.finditer(content):
            key=m.group(0)
            ln=content[:m.start()].count('\n')+1
            sp=content.split('\n')
            ctx=sp[ln-1].strip()[:150] if 0<ln<=len(sp) else ''
            cat,prov,sev=classify_key(key,ctx,filename)
            keys.append({'key':key,'cat':cat,'provider':prov,'severity':sev,'line':ln,'context':ctx})
        return keys

    def run(self,queries,entropy=False):
        print(f'\n  {bold("Queries")}:{len(queries)} | {bold("RPM")}:{self.rpm} | '
              f'{bold("Entropy")}:{green("ON") if entropy else dim("OFF")}')
        print(f'  {dim(chr(0x2500)*60)}\n')
        all_keys=[];tf=0
        for qi,q in enumerate(queries):
            items=self.search(q);nf=0;qkeys=0
            print(f'  {cyan(chr(0x25B6))} [{qi+1:2d}/{len(queries)}] {bold(q[:62])}')
            for it in items:
                repo=it['repository']['full_name'];path=it['path']
                fid=f'{repo}/{path}'
                if fid in self.seen:continue
                self.seen.add(fid);nf+=1;tf+=1
                stars=it['repository'].get('stargazers_count',0)
                lang=it['repository'].get('language','?')
                print(f'     {dim(chr(0x2514))} {dim(repo)}/{dim(path)}  {yellow(chr(0x2B50)+str(stars)) if stars>10 else dim(chr(0x2B50)+str(stars))}  {dim(lang)}',end=' ')
                content=self.download(repo,path)
                if not content:
                    print(f'{red(chr(0x2717))}')
                    continue
                fkeys=0
                for ek in self.extract(content,path):
                    sev_sym=SEV_COLOR.get(ek['severity'],dim)('*')
                    all_keys.append({'repo':repo,'file':path,'line':ek['line'],'key':ek['key'],
                        'cat':ek['cat'],'provider':ek['provider'],'severity':ek['severity'],
                        'context':ek['context'],'stars':stars,'repo_url':it['repository']['html_url'],
                        'repo_lang':lang,'source':'regex'})
                    fkeys+=1;qkeys+=1
                if entropy:
                    for estr,ln in detect_high_entropy(content):
                        all_keys.append({'repo':repo,'file':path,'line':ln,'key':estr,
                            'cat':'other','provider':'HighEntropy','severity':'medium',
                            'context':'','stars':stars,'repo_url':it['repository']['html_url'],
                            'repo_lang':lang,'source':'entropy'})
                        fkeys+=1;qkeys+=1
                if fkeys:
                    print(f'{green(chr(0x2713))} {bold(str(fkeys))} keys')
                else:
                    print(f'{dim(chr(0x2713))}')
            print(f'  {dim(chr(0x2514))} {bold(f"files:{nf}")}  keys:{bold(str(qkeys))}  total_files:{tf}  total_keys:{bold(str(len(all_keys)))}')
            if qi<len(queries)-1:
                sys.stdout.write(f'  {dim(f"wait {self.delay:.0f}s...")}')
                sys.stdout.flush()
                time.sleep(self.delay)
                sys.stdout.write('\r'+' '*30+'\r')
                sys.stdout.flush()
        print()
        seen_u=set();dedup=[]
        for k in all_keys:
            uid=f'{k["repo"]}{k["file"]}{k["line"]}{key_hash(k["key"])}'
            if uid not in seen_u:seen_u.add(uid);dedup.append(k)
        return all_keys,dedup

# ═══════ 报告引擎 ═══════
class Report:
    def __init__(self,all_keys,dedup,out):
        self.all=all_keys;self.dedup=dedup;self.out=out
        os.makedirs(out,exist_ok=True)

    def stats(self):
        d=self.dedup;a=self.all
        cats=defaultdict(lambda:{'raw':0,'uniq':0,'repos':set(),'files':set(),'prov':Counter()})
        for k in a:cats[k['cat']]['raw']+=1
        for k in d:
            c=cats[k['cat']];c['uniq']+=1;c['repos'].add(k['repo'])
            c['files'].add(f"{k['repo']}/{k['file']}");c['prov'][k['provider']]+=1
        for c in cats.values():c['repos']=len(c['repos']);c['files']=len(c['files'])
        return cats

    def generate(self):
        ts=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cats=self.stats()
        tr=len(self.all);tu=len(self.dedup)
        trepos=len(set(k['repo'] for k in self.dedup))
        tfiles=len(set(f"{k['repo']}/{k['file']}" for k in self.dedup))

        # TXT
        L=[]
        def h(s):L.append(bold(s))
        def p(s):L.append(s)
        p(chr(0x2550)*66)
        p('  GitHub Crypto Leak Scan Report')
        p(chr(0x2550)*66)
        p(f'  {ts}')
        p(f'  Raw:{bold(f"{tr:,}")}  Unique:{bold(f"{tu:,}")}  Repos:{bold(f"{trepos:,}")}  Files:{bold(f"{tfiles:,}")}')
        p('')
        for ck in('overseas','domestic','proxy'):
            c=cats[ck]
            if c['uniq']==0:continue
            p(f'  {bold(CAT_LABEL[ck])}: {c["raw"]:,}/{c["uniq"]:,}  repos{c["repos"]:,}  files{c["files"]:,}')
            for prov,cnt in c['prov'].most_common():
                p(f'     {prov:<20s} {cnt:>6,}')
        p('')
        p(chr(0x2500)*66)
        p('  Top 30 (by Stars)')
        p(chr(0x2500)*66)
        for i,k in enumerate(sorted(self.dedup,key=lambda x:-x['stars'])[:30],1):
            sev_sym=SEV_COLOR.get(k.get('severity','medium'),dim)
            stars_str = dim(chr(0x2B50) + str(k['stars']))
            p(f'  [{i:2d}] {sev_sym("*")} {bold(k["repo"])}  {stars_str}')
            p(f'       {dim(k["file"])}:{k["line"]}  [{k["provider"]}]  {dim(k.get("source","?"))}')
            p(f'       {mask_key(k["key"])}')
            if k.get('context'):p(f'       {dim(k["context"][:100])}')
            p('')
        langs=Counter(k.get('repo_lang','?') for k in self.dedup)
        p(chr(0x2500)*66)
        p('  Languages')
        p(chr(0x2500)*66)
        for lang,cnt in langs.most_common(10):p(f'  {lang:<18s} {cnt:>6,}')
        report='\n'.join(L)
        with open(os.path.join(self.out,'scan_summary.txt'),'w',encoding='utf-8')as f:
            f.write(re.sub(r'\033\[\d+m','',report))

        # MD
        md=[]
        md.append('# GitHub Crypto Leak Scan Report\n')
        md.append(f'> {ts}\n')
        md.append('## Core Data\n')
        md.append('| Metric | Value |');md.append('|--------|-------|')
        md.append(f'| Raw | {tr:,} |');md.append(f'| Unique | {tu:,} |')
        md.append(f'| Repos | {trepos:,} |');md.append(f'| Files | {tfiles:,} |')
        md.append('')
        md.append('## By Category\n')
        md.append('| Category | Raw | Unique | Repos | Files |');md.append('|----------|-----|--------|-------|-------|')
        for ck in('overseas','domestic'):
            c=cats[ck]
            if c['uniq']==0:continue
            md.append(f'| {CAT_LABEL[ck]} | {c["raw"]:,} | {c["uniq"]:,} | {c["repos"]:,} | {c["files"]:,} |')
        md.append('')
        md.append('## By Provider\n')
        for ck in('overseas','domestic'):
            md.append(f'### {CAT_LABEL[ck]}\n')
            for prov,cnt in cats[ck]['prov'].most_common():
                md.append(f'- {prov}: {cnt:,}')
        md.append('')
        md.append('## Top 20\n')
        for i,k in enumerate(sorted(self.dedup,key=lambda x:-x['stars'])[:20],1):
            md.append(f'{i}. **{k["repo"]}** {chr(0x2B50)}{k["stars"]:,}')
            md.append(f'   `{k["file"]}:{k["line"]}` [{k["provider"]}] `{mask_key(k["key"])}`')
            md.append('')
        with open(os.path.join(self.out,'report.md'),'w',encoding='utf-8')as f:
            f.write('\n'.join(md))

        # JSON
        json_out={
            'time':ts,'raw':tr,'unique':tu,'repos':trepos,'files':tfiles,
            'categories':{ck:{'label':CAT_LABEL[ck],'raw':c['raw'],'unique':c['uniq'],
                'repos':c['repos'],'files':c['files'],
                'providers':dict(c['prov'].most_common())} for ck,c in cats.items() if c['uniq']>0},
            'top100':[{'repo':k['repo'],'file':k['file'],'line':k['line'],
                'provider':k['provider'],'severity':k['severity'],
                'key':k['key'],'key_masked':mask_key(k['key']),'key_hash':key_hash(k['key']),
                'stars':k['stars'],'language':k.get('repo_lang','?'),
                'source':k.get('source','?'),'context':k.get('context','')}
                for k in sorted(self.dedup,key=lambda x:-x['stars'])[:100]],
        }
        with open(os.path.join(self.out,'scan_result.json'),'w',encoding='utf-8')as f:
            json.dump(json_out,f,ensure_ascii=False,indent=2)

        return os.path.join(self.out,'scan_summary.txt'),os.path.join(self.out,'report.md'),os.path.join(self.out,'scan_result.json')


# ═══════ CLI ═══════
def main():
    autoplay_startup_gif()

    BANNER = [
        r'????????????????????????????????????????????????????????????????',
        r'?  r5hhhh2ssi;;iiiiiiiiii;r2hMMMMMMMMMMMMMhhhh5r;ii;;;;;    ?',
        r'?  A233hhhh3Arrrrsiiiiiii2hMMMMhhMMMMMMMMMhhhhMMA;;;;;;;    ?',
        r'?  A25555333552AXAsiiiir3MMhMMhhMMMMhhMMMMMMMMhhM5ii;;;     ?',
        r'?  A22255555352AXXriiirhMhMMhhhMMMMMMhhMMhMMMMMMhM2iiii     ?',
        r'?  ssssXsirsrrrrrrrrrsM3hMM3h3MhMMhMMM3hMh3MMMhhMMMhri      ?',
        r'?  irrrrrrrrrrrrrrrriXh3MMhhh5M2hhh3MM53h53hMMhhhMMMXr      ?',
        r'?  rrrrrrrrrrrrrrrrrrshhMH33h3hA52M5hH22hA33hhhhhhMM3h      ?',
        r'?  rrrrrrrrrrrrrrrrrrA33HM253h53AXA32MAX223555Mhh3M3MS      ?',
        r'?  rrrrrrrrrrrrrrrrrr3X3h33SSH3iH#9GhAhS9h;MHGM33hH3MM      ?',
        r'?  rrrrrrrrrrrsssAAssssrr2hM3hG#99#9#H9####9SMh33523MG      ?',
        r'?  srrsXXXXsXA553MhMHHHH2XAAAX2MS9###S##9#G5XsXsA5HSG       ?',
        r'?  s222hG##MHSSSSSSGSSSGH2MAsAAX3S999999#G2XX2sAMHHHG       ?',
        r'?  5HGGGS#9#SS##SS#####SSGGG5AMAs3MH##SHGG35Hh3MMMHHH       ?',
        r'?  MHGSSS999##99#SSSSS#SGSSSSHMhh3M353HS9GH#9S#GhhMMH       ?',
        r'?  GGSSSS##9####SSSSSSSSGGGGGGHHMh#SGS999SHSS###GMMHH       ?',
        r'?  GGGGGGGGGGGGGGSSSSSSSSSSGGHGHM#9999#999GHSSGGSGGGH       ?',
        r'?  HHHMHHHGGGGGGGGGHHHHMMMMS#99GMG#9999#SS9B&B9SHMhMM       ?',
        r'?  hhhhhhhhhhhhhhh333hhHG3H9&&B&&#SG#9SS9B&&&&&GH9Gh3       ?',
        r'?  GitHub Crypto Leak Scanner           v2                     ?',
        r'????????????????????????????????????????????????????????????????',
    ]
    for line in BANNER:
        print(dim(line))

    p = argparse.ArgumentParser(description='GitHub Crypto Credential Leak Scanner v2')
    p.add_argument('--token', '-t', default='', help='GitHub PAT (optional)')
    p.add_argument('--deep', '-d', action='store_true', help='Deep scan (46 search terms)')
    p.add_argument('--entropy', '-e', action='store_true', help='High-entropy detection')
    p.add_argument('--output', '-o', default=None, help='Output dir')
    args = p.parse_args()

    token = args.token.strip() or os.environ.get('GITHUB_TOKEN', '')
    deep = args.deep
    entropy = args.entropy
    out_dir = args.output or OUTPUT_DIR

    if not token and not deep and not entropy and not args.token and not os.environ.get('GITHUB_TOKEN'):
        print(f'\n  {bold(">>> Interactive Mode <<<")}\n')
        choice = input('  Use GitHub Token? (y/n) [n]: ').strip().lower()
        if choice == 'y':
            token = input('  Paste your GitHub Token: ').strip()
            if not token:
                print(f'  {red("No token entered, running without token.")}')
        elif choice not in ('', 'n'):
            print(f'  {yellow("Invalid choice, running without token.")}')

        print(f'\n  {bold("Select scan mode:")}')
        print(f'    {cyan("[1]")} Fast         (12 queries, ~2 min)')
        print(f'    {cyan("[2]")} Deep         (46 search terms, ~8 min)')
        print(f'    {cyan("[3]")} Fast+Entropy (12 queries + entropy)')
        print(f'    {cyan("[4]")} Deep+Entropy (46 search terms + entropy)')
        mode = input('  Choice [2]: ').strip() or '2'
        if mode == '1':
            deep, entropy = False, False
        elif mode == '2':
            deep, entropy = True, False
        elif mode == '3':
            deep, entropy = False, True
        elif mode == '4':
            deep, entropy = True, True
        else:
            deep, entropy = True, False

    queries = SEARCH_DEEP if deep else SEARCH_FAST

    print(f'\n  {bold("GitHub Crypto Leak Scanner v2")}')
    print(f'  {"Token" if token else "No-Token"} | {len(queries)} queries | {"entropy" if entropy else "no-entropy"}')
    print(f'  {dim(f"Output: {out_dir}")}')

    scanner = Scanner(token)
    all_keys, dedup = scanner.run(queries, entropy=entropy)

    if all_keys:
        r = Report(all_keys, dedup, out_dir)
        txt, md, js = r.generate()
        print(f'\n  {green(chr(0x2713))} TXT : {txt}')
        print(f'  {green(chr(0x2713))} MD  : {md}')
        print(f'  {green(chr(0x2713))} JSON: {js}')
    else:
        print(f'\n  {yellow(chr(0x26A0))} No keys found.')
        print('    1. Rate limited -> wait or use token')
        print('    2. Invalid token -> https://github.com/settings/tokens (classic)')

if __name__ == '__main__':
    main()

