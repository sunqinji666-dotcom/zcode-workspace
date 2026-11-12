# Jev（TypeSafe）快速上手包

前 OpenAI 研究员 Diogo Almeida 团队的 "System One 模型"：不聊天、不写文字，只回结构化判断
（Noul 是否 / Choice 选项 / Score 打分），官方定位是给软件调用的判断层。

## 当前状态：✅ 已配好，直接可用

- [x] 2026-09-27 已排 waitlist + 提交插队问卷（等官方邀请，备用）
- [x] **OpenRouter 渠道已配好**：key（jev-mac）已写入 `.env`，1 年有效、限额 $50
- [x] 已跑通：`./run.sh quickstart.py` 实测正常，单次成本约 $0.00002
- [ ] 建议充值：OpenRouter 余额目前 $0（宽限期可小额调用，充 $5~10 一劳永逸）

## 怎么用（三步）

```bash
cd ~/Documents/zcode/jev
./run.sh quickstart.py                    # 跑示例
./run.sh 你的脚本.py                       # 跑你自己的脚本
```

任何 Python 脚本里：读环境变量 `OPENROUTER_API_KEY`，调
`POST https://openrouter.ai/api/alpha/decisions`，模型名 `typesafe/jev-1.13`。

## 文件说明

| 文件 | 作用 |
|---|---|
| `.venv/` | 独立 Python 3.14 环境（示例脚本用标准库，装它为了以后加依赖） |
| `quickstart.py` | 示例：一次调用混问 Noul/Choice/Score |
| `run.sh` | 读 `.env` 后跑脚本（key 不进 git） |
| `.env` | OpenRouter API key（600 权限，已在 .gitignore） |

## 充值与官方渠道

- 充值：https://openrouter.ai/settings/credits（信用卡 / 加密货币）
- 官方控制台（等邀请后用）：https://console.typesafe.ai/
- 文档：https://docs.typesafe.ai/ ｜ OpenRouter 教程：https://openrouter.ai/docs/guides/community/jev-tutorial

## ⚠️ 仿冒站提醒

搜索时会遇到 `jevtypesafeai.com`、`jev-ai-typesafe.com`、`typesafeai.org` 等蹭流量/仿冒域名，
**只认 typesafe.ai / docs.typesafe.ai / console.typesafe.ai / openrouter.ai**，别在任何其他站输入 key。

## 想装到全局时（可选）

```bash
export OPENROUTER_API_KEY="你的key"
```
