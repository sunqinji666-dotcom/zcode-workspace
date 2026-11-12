# Gemini 3.8 Flash TTS 试听样本包（2026-09-27 实测）

全部样本由 **OpenRouter → Google AI Studio** 实际调用生成，模型 `google/gemini-3.8-flash-tts` /
`google/gemini-3.8-flash-lite-tts`。凭证复用 `~/Documents/zcode/jev/.env` 里的 `OPENROUTER_API_KEY`。

## 先听什么

| 文件 | 内容 | 用途 |
|---|---|---|
| `voices/*.mp3` | 官方 30 个预建音色，各读同一句「拾响，让散落在硬盘里的声音，都能被听见。」 | **挑音色**：连着听一遍，记下喜欢的名字 |
| `shixiang_full_zephyr.mp3` / `.wav` | 拾响宣传片全篇旁白，Zephyr 音色，55.3 秒 | 长文本效果；与现用千问版直接 A/B |
| `shixiang_full_charon.mp3` / `.wav` | 同文案，Charon 音色，49.4 秒（本批最快） | 偏沉稳、语速快的男声候选 |
| `shixiang_full_lite.mp3` | 同文案，Flash-Lite 档，55.5 秒 | 便宜 1/3 的档位够不够用 |
| `compare_qwen_ethan.mp3` | 同文案，千问 qwen3-tts-flash + Ethan（拾响现用方案），53.4 秒 | A/B 对照基准 |
| `dialog_test.mp3` | 双人对话实验（`speakers` 参数） | 证据：OpenRouter 路径**未**分角色，双人对话要走官方 API |
| `sample_A/B/C.mp3` | 早期三音色短样本（Zephyr / Puck / Kore） | 可忽略 |
| `transcripts/` | 上述长样本的阿里云 paraformer-v2 转写回读 | 中文准确度的客观校验 |

## 实测成本（OpenRouter 实付，账单可查）

- 标价：Flash TTS **$0.50 输入文本 / $9 音频输出**（每 100 万 token）；Flash-Lite **$0.50 / $6**
- 音频 token 换算：25 token = 1 秒音频（官方口径）
- **每分钟音频 ≈ $0.0135 ≈ ¥0.10**；上面 55 秒长样本一条 ≈ ¥0.09
- 拾响 90 秒宣传片全篇（不用切分，一次成）≈ ¥0.14
- 30 音色样本包总计 ≈ ¥0.22；本次调研全部实测花费合计不到 ¥1

## 中文质检（转写回读，非同音差异才算真错）

同一段 235 字文案，两个引擎分别听写回来比对：

- **Gemini Zephyr**：同音字差异为主（「拾响」→「实想/石响」，读音正确）；真实瑕疵 2 处——
  句号处停顿不足导致「翻。拾响」连读成「翻实想」；「macOS」读成「maos」。
- **千问 Ethan（对照）**：真实瑕疵 3 处——「索引」读成「所以」、「AI」读成近似「哎呀」、
  「该在」听成「该塞」。
- 结论：两者中文可懂度同档，都能用；Gemini 的差异集中在停顿/英文混读，千问在字词清晰度上
  偶发失误。Gemini 的强项是**长文本一次成**（55 秒无需按 180 字切分拼接）和表达控制。

## 调用方式（已验证，可直接复用）

```bash
# 端点不是 chat/completions，是 audio/speech；Gemini TTS 只接受 pcm
curl -sS https://openrouter.ai/api/v1/audio/speech \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" -H "Content-Type: application/json" \
  -d '{"model":"google/gemini-3.8-flash-tts","input":"要读的文本","voice":"Zephyr","response_format":"pcm"}' \
  -o out.pcm
# 24kHz 单声道 16bit，用 ffmpeg 封装：
ffmpeg -y -f s16le -ar 24000 -ac 1 -i out.pcm -c:a libmp3lame -b:a 160k out.mp3
```

坑与边界（实测）：

- `response_format` 只接受 `pcm`（mp3 会 400：「Gemini TTS only supports response_format="pcm"」）
- `voice` 只认 30 个预建音色名；`voice_xxx` 自定义音色 ID → 404（语音设计/复刻只在官方 Gemini API / AI Studio 有）
- `speakers` 双人对话参数不报错但**不生效**（转写验证 speaker_id 全为 0）
- 返回头 `x-generation-id` 可用于 `GET /api/v1/generation?id=...` 查真实用量与花费
