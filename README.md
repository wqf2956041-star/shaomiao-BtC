# GitHub Crypto Leak Scanner

扫描 GitHub 公开仓库中泄露的 **虚拟货币地址 + 私钥**，覆盖 Bitcoin / Ethereum / Solana / TRON / BNB Chain 等 20+ 条链。输出统计报告，供安全研究和资产审计使用。

## 背景

GitHub 上大量公开仓库意外提交了加密货币钱包文件、私钥文件、助记词和配置文件。本项目自动化扫描这些泄露，帮助用户及时发现暴露的链上凭证。

## 快速开始

```bash
pip install -r requirements.txt
python github_key_scanner.py
```

零配置，无需 Token。

## 扫描范围

| 私钥类型 | 地址类型 |
|---------|---------|
| BTC WIF (5H/5J/5K/L/K) | Bitcoin P2PKH (1...) |
| ETH/BSC EVM (0x + 64 hex) | Bitcoin P2SH (3...) |
| 通用 Hex-64 私钥 | Bitcoin Bech32 (bc1...) |
| BIP32 扩展私钥 (xprv) | Ethereum (0x...) |
| BIP32 扩展公钥 (xpub) | TRON TRC20 (T...) |
| Solana 私钥 (base58) | Solana |
| | XRP (r...) |
| | Cosmos (cosmos1...) |
| | Polkadot |
| | Avalanche C-Chain |

## 原理

GitHub Search API 对纯密钥模式做了隐性屏蔽。本项目改用**文件名 + 关键词**策略绕过：

| 策略 | 示例搜索词 |
|------|-----------|
| 搜钱包文件 | `filename:wallet.dat` |
| 搜 keystore | `filename:keystore "address"` |
| 搜助记词/私钥 | `"mnemonic" "phrase" path:.env` |
| 搜 keys 文件 | `filename:keys.txt "0x"` |

下载匹配文件后用正则提取全部加密货币私钥和地址格式。

## 使用

```bash
python github_key_scanner.py                    # 无 token，~3 分钟
python github_key_scanner.py --token ghp_xxx    # 有 token 加速
python github_key_scanner.py --deep             # 深度扫描（46 搜索词）
```

也可通过环境变量：

```bash
export GITHUB_TOKEN=ghp_xxx
python github_key_scanner.py
```

## 输出

```
scan_summary.txt   — 可读报告
scan_result.json   — 结构化数据（私钥仅存 SHA256 hash，不存明文）
report.md          — Markdown 格式报告
```

## 速率

| 模式 | 搜索频率 | 预计 |
|------|---------|------|
| 无 Token | 10 次/分钟 | ~3 分钟 |
| 有 Token | 30 次/分钟 | ~1 分钟 |

遇限速自动等待恢复。

## 安全

- 仅读取公开仓库，不执行任何写操作
- 私钥仅存 SHA256 hash，报告中使用脱敏格式
- Token 通过命令行参数或环境变量传入，**不硬编码**
- 仅供安全研究，请勿滥用

## License

MIT
