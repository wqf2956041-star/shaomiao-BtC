# 多合一 GitHub 密钥扫描器

## 扫描模式

### 1. AI 密钥扫描 (原始)
```bash
python3 github_key_scanner.py --token ghp_xxx --deep --entropy
```

### 2. 高价值 AI 定向扫描
```bash
python3 high_value_scanner.py --token ghp_xxx
# 只扫最近 7 天
python3 high_value_scanner.py --token ghp_xxx --days 7
# 指定输出目录
python3 high_value_scanner.py --token ghp_xxx -o ~/Desktop/HighValue_Scan
```

### 3. 加密货币扫描 (新增)
扫描 ETH 私钥 / BTC WIF / BIP39 助记词 / SOL 私钥 / Keystore

```bash
python3 github_key_scanner.py --token ghp_xxx --crypto
```

## 高价值目标

| 类型 | Key 特征 | 免费额度 |
|------|---------|---------|
| Claude (Anthropic) | `sk-ant-*` | 无免费 |
| OpenAI Pro | `sk-proj-*` | $18 免费 |
| Google Gemini | `AIza*` | 免费额度 |
| NVIDIA | `nvapi-*` | 免费额度 |
| Groq | `gsk_*` | 免费额度 |
| HuggingFace | `hf_*` | 免费 |

## 加密货币检测

| 类型 | 格式 | 价值 |
|------|------|------|
| ETH 私钥 | `0x` + 64 hex | ⭐⭐⭐⭐⭐ |
| BTC WIF | `5`/`K`/`L` 开头 | ⭐⭐⭐⭐⭐ |
| BIP39 助记词 | 12/18/24 英文单词 | ⭐⭐⭐⭐⭐ |
| SOL 私钥 | JSON 数组 | ⭐⭐⭐⭐ |
| ETH Keystore | JSON 加密文件 | ⭐⭐⭐ |

## 提取资金

详见 `CRYPTO_KNOWLEDGE.md`

## 策略

1. **Fork 扫描** — 定向扫知名 AI 项目的 fork
2. **深度路径** — 扫 .env.local / .env.production 等深层文件
3. **语言限定** — 按 Python/JS/TS/Go 语言分别扫
4. **最近推送** — 只扫最近 N 天的推送
5. **区域切换** — 不同语言区域的不同扫描策略
