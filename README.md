# ⚡ 电力预测每日文献系统

> 全自动获取电力预测领域最新 arXiv 论文的 AI 增强摘要工具

## 🎯 项目简介

本项目专为**电力系统/电力预测**方向的本科生和研究人员设计,每天自动获取并 AI 总结以下领域的最新文献:

- 🔋 **机器学习在电力预测中的应用** (时间序列预测、深度学习)
- 🌐 **微电网与能源系统优化**
- ⚙️ **电力系统控制与稳定性**
- 🤖 **新型 AI 模型** (Transformer、GNN 等) 在能源领域的应用

## ✨ 核心特性

🎯 **零基础设施需求**
- 基于 GitHub Actions 和 Pages - 无需服务器
- 完全免费部署和使用

🤖 **AI 智能摘要**
- 每日自动爬取 arXiv 论文
- Claude Haiku 模型生成中文摘要
- 成本低廉:每天仅约 0.2 元

💫 **智能阅读体验**
- 个性化论文高亮显示
- 跨设备兼容 (桌面 & 移动端)
- 本地偏好存储保护隐私
- 灵活日期范围筛选

👉 **[立即访问](https://disdorqin.github.io/power-papers-daily/)** - 无需安装

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
| `ACCESS_PASSWORD` | (可选) | 访问密码保护 |

### 第三步: 配置 Variables

进入仓库 → Settings → Secrets and variables → Actions → Variables

添加以下 Variables:

| Variable 名称 | 值 | 说明 |
|--------------|-----|------|
| `CATEGORIES` | `cs.LG,cs.AI,eess.SP,stat.ML` | arXiv 分类 |
| `LANGUAGE` | `Chinese` | 摘要语言 |
| `MODEL_NAME` | `claude-haiku` | AI 模型 |
| `EMAIL` | (你的邮箱) | Git 提交邮箱 |
| `NAME` | (你的名字) | Git 提交名称 |

### 第四步: 启用 GitHub Pages

Settings → Pages → Source 选择 **GitHub Actions**

### 第五步: 手动触发工作流

Actions → arXiv-daily-ai-enhanced → Run workflow

首次运行可能需要约 1 小时。

## 💰 成本估算

| 项目 | 费用 |
|------|------|
| API 费用 | 约 0.2 元/天 |
| GitHub Actions | 免费额度足够 |
| GitHub Pages | 完全免费 |
| **总计** | **约 6 元/月** |

## 🔧 自定义配置

### 修改 arXiv 分类

编辑 `daily_arxiv/config.yaml`:

```yaml
arxiv:
  categories:
    - cs.LG  # 机器学习
    - cs.AI  # 人工智能
    - eess.SP  # 信号处理
    - stat.ML  # 统计机器学习
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
