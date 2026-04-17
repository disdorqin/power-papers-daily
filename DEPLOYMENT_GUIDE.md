# 电力预测每日文献 - 部署指南

## 第一步:配置 GitHub Secrets

进入仓库 → Settings → Secrets and variables → Actions → Secrets

添加以下 Secrets:

| Secret 名称 | 值 | 说明 |
|-----------|-----|------|
| `OPENAI_API_KEY` | (你的 API Key) | Xiavier API Key |
| `OPENAI_BASE_URL` | `https://api.xiavier.com/v1` | Xiavier API 地址 |

## 第二步:启用 GitHub Pages

Settings → Pages → Source 选择 **GitHub Actions**

## 第三步:手动触发工作流

Actions → arXiv-daily-ai-enhanced → Run workflow

## 第四步:访问网站

https://disdorqin.github.io/power-papers-daily/

## 成本估算

- API 费用:约 0.2 元/天
- GitHub Actions:免费额度足够
- GitHub Pages:完全免费
