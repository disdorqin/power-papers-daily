# ⚡ SOTA Papers Daily - 顶会前沿论文聚合

> 全自动收集 CVPR/ICCV/ECCV/NeurIPS/ICML/ICLR 等顶会最新 SOTA 论文，仅收录有开源代码的前沿研究

## 🎯 项目简介

本项目专为**计算机视觉/机器学习/时序预测/电力预测**方向的研究人员设计，聚合全球顶会最新 SOTA 论文：

- 🔥 **SOTA 模型论文** (必须有开源代码)
- 📈 **时序预测前沿** (Time Series Forecasting)
- ⚡ **电力预测应用** (Power/Energy Prediction)
- 🤖 **新型 AI 模型** (Transformer、Diffusion、LLM 等)

## ✨ 核心特性

🎯 **智能 SOTA 过滤**
- 仅收录有 GitHub 开源代码的论文
- 自动识别 SOTA/benchmark/state-of-the-art 关键词
- 聚焦时序预测和电力预测领域

🌐 **多数据源聚合**
- CVPR/ICCV/ECCV/NeurIPS/ICML/ICLR 等顶会
- arXiv 最新论文实时抓取
- Semantic Scholar 学术搜索

🤖 **AI 智能摘要**
- 自动生成中文结构化摘要
- 提取 GitHub Stars 和代码信息
- 领域标签自动分类

💫 **智能阅读体验**
- 按时间顺序展示，每页 20 篇
- 领域过滤 (CV/ML/时序/电力)
- 跨设备兼容 (桌面 & 移动端)

👉 **[访问 SOTA 论文站](https://disdorqin.github.io/power-papers-daily/sota.html)** - 无需安装

## 📊 数据源

| 数据源 | 说明 | 更新频率 |
|--------|------|----------|
| CVPR2026-Papers-with-Code | CVPR 2026 官方论文列表 | 每日 |
| arXiv API | 最新预印本论文 | 每日 |
| Semantic Scholar | 学术论文搜索引擎 | 每日 |

## 📋 快速部署

### 第一步: Fork 仓库

点击页面右上角的 **Fork** 按钮,将此仓库复制到你自己的 GitHub 账户。

### 第二步: 配置 Secrets

进入仓库 → Settings → Secrets and variables → Actions → Secrets

添加以下 Secrets:

| Secret 名称 | 值 | 说明 |
|-----------|-----|------|
| `OPENAI_API_KEY` | (你的 API Key) | Xiavier API Key |
| `OPENAI_BASE_URL` | `https://api.xiavier.com/v1` | Xiavier API 地址 |
| `TOKEN_GITHUB` | (可选) | GitHub Token (获取 Stars) |
| `ACCESS_PASSWORD` | (可选) | 访问密码保护 |

### 第三步: 配置 Variables

进入仓库 → Settings → Secrets and variables → Actions → Variables

添加以下 Variables:

| Variable 名称 | 值 | 说明 |
|--------------|-----|------|
| `LANGUAGE` | `Chinese` | 摘要语言 |
| `MODEL_NAME` | `gpt-4o-mini` | AI 模型 |
| `EMAIL` | (你的邮箱) | Git 提交邮箱 |
| `NAME` | (你的名字) | Git 提交名称 |

### 第四步: 启用 GitHub Pages

Settings → Pages → Source 选择 **GitHub Actions**

### 第五步: 手动触发工作流

Actions → SOTA Papers Daily → Run workflow

首次运行可能需要约 1 小时。

## 💰 成本估算

| 项目 | 费用 |
|------|------|
| API 费用 | 约 0.5 元/天 |
| GitHub Actions | 免费额度足够 |
| GitHub Pages | 完全免费 |
| **总计** | **约 15 元/月** |

## 🔧 自定义配置

### 修改 SOTA 过滤关键词

编辑 `collect_sota_papers.py`:

```python
SOTA_KEYWORDS = [
    "state-of-the-art",
    "sota",
    "benchmark",
    # ... 添加更多关键词
]

DOMAIN_KEYWORDS = [
    "time series",
    "power",
    "electricity",
    # ... 添加更多领域关键词
]
```

### 修改 AI 模型

编辑 `daily_arxiv/config.yaml`:

```yaml
llm:
  model_name: 'claude-haiku'  # 最便宜的模型
```

## 📚 常用 arXiv 分类

| 分类代码 | 领域 |
|---------|------|
| cs.LG | 机器学习 |
| cs.AI | 人工智能 |
| cs.CV | 计算机视觉 |
| cs.CL | 计算语言学 |
| eess.SP | 信号处理 |
| stat.ML | 统计机器学习 |
| eess.SY | 系统与控制 |

## ⚠️ 重要提醒

- 🔒 **保护你的 API Key**: 永远不要将 API Key 提交到代码中
- 🔄 **定期更新**: 建议每月检查一次配置
- 📊 **监控使用量**: 定期检查 API 使用情况和费用

## 🤝 贡献

欢迎提交 Issue 和 Pull Request!

## 📄 许可证

MIT License

## 🙏 致谢

本项目基于 [daily-arXiv-ai-enhanced](https://github.com/dw-dengwei/daily-arXiv-ai-enhanced) 定制开发,感谢原作者的贡献!
