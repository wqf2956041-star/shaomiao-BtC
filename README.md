# GitHub Crypto Leak Scanner v2

**扫描 GitHub 公开仓库 + Gist + Pastebin 中泄露的虚拟货币私钥、助记词、Keystore 文件和地址。**

## 快速开始

```bash
pip install -r requirements.txt
python github_key_scanner.py
```

## 扫描能力

| 目标类型 | 检测方式 | 价值 |
|---------|---------|------|
| **私钥 (0x + 64 hex)** | 正则 + secp256k1 曲线验证 | ✅ 可直接控制钱包 |
| **比特币 WIF 私钥** | 正则匹配 base58 | ✅ 可直接控制钱包 |
| **BIP32 扩展私钥 (xprv)** | 正则匹配 | ✅ 可派生所有子地址 |
| **BIP39 助记词** | BIP39 词库匹配 (2048 词) | ✅ 可恢复完整钱包 |
| **Ethereum Keystore** | JSON 结构解析 | ✅ 加密钱包（需破解密码） |
| **扩展公钥 (xpub)** | 正则匹配 | ⚠️ 可监控所有子地址 |
| **ETH/BTC/SOL/TRX 地址** | 正则匹配 | 链上公开信息 |

## 多源扫描

```bash
# GitHub 仓库（默认）
python github_key_scanner.py --token ghp_xxx

# GitHub Gist
python github_key_scanner.py --sources gist --token ghp_xxx

# Pastebin 最新公开粘贴
python github_key_scanner.py --sources pastebin

# 全源扫描（推荐）
python github_key_scanner.py --sources all --token ghp_xxx --deep
```

## 智能验证

- ✅ **secp256k1 曲线验证** — 排除 SHA256 哈希、txid、无效 hex
- ✅ **测试密钥过滤** — 自动排除 Hardhat/Anvil/Ganache 默认密钥
- ✅ **BIP39 词库验证** — 检测真正的助记词，排除随机英文词组
- ✅ **Keystore 结构解析** — 识别加密钱包文件

## 输出

```
scan_summary.txt   — 分类统计报告
scan_result.json   — 结构化数据（私钥仅存 SHA256 hash）
report.md          — Markdown 报告
```

## License

MIT
