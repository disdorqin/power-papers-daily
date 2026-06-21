<div align="center">

<img src="assets/banner.svg" width="100%" alt="power-papers-daily Banner" />

</div>

## AI Literature Radar for Power Systems

[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)](https://developer.mozilla.org/docs/Web/JavaScript)
[![Node.js](https://img.shields.io/badge/Node.js-339933?style=flat-square&logo=node.js&logoColor=white)](https://nodejs.org/)
[![License](https://img.shields.io/github/license/disdorqin/power-papers-daily?style=flat-square&color=A3E635&logo=opensourceinitiative)](LICENSE)
[![Stars](https://img.shields.io/github/stars/disdorqin/power-papers-daily?style=flat-square&color=A855F7&logo=github)](https://github.com/disdorqin/power-papers-daily/stargazers)
[![Status](https://img.shields.io/badge/STATUS-ACTIVE-A855F7?style=flat-square&logo=circle&logoColor=white)](https://github.com/disdorqin/power-papers-daily)
[![Power Systems](https://img.shields.io/badge/DOMAIN-Power%20Systems%20%26%20Energy-00F5FF?style=flat-square)](https://github.com/disdorqin/power-papers-daily)

---

> An AI-powered daily literature mining system for power systems and energy forecasting research. Automatically fetches, scores, and summarizes the latest papers from arXiv and other sources — delivering a daily research brief to your inbox or dashboard.

## Why This Exists

Keeping up with the energy systems literature is a full-time job. This tool automates it: every day, it scans for new papers in electricity forecasting, microgrids, and energy optimization — then uses AI to extract the key findings.

## Features

- **Daily arXiv Crawling** — automated fetch of latest preprints in power systems  
- **AI-Powered Summarization** — LLM-generated summaries of key contributions  
- **Relevance Scoring** — papers ranked by relevance to your research focus  
- **Web Dashboard** — browse daily papers with an interactive UI  
- **WeChat / Email Push** — daily digest delivered automatically  
- **SOTA Tracking** — track state-of-the-art results over time  

## Architecture

<div align="center">
  <img src="assets/architecture.svg" width="100%" alt="Architecture" />
</div>

## Quick Start

```bash
# Clone and install
git clone https://github.com/disdorqin/power-papers-daily.git
cd power-papers-daily
npm install

# Configure your research interests
cp .env.example .env
# Edit .env with your API keys and preferences

# Run the daily fetch
npm start

# Or set up auto-run with GitHub Actions (already configured)
```

## Example Output

See the [live dashboard](https://disdorqin.github.io/power-papers-daily) for today's papers.

Papers are scored on:
- **Time relevance** (how recent)
- **Journal impact** (where published)
- **Citation velocity** (how fast it's being cited)
- **Topic alignment** (match with your research)

## Roadmap

- [x] Daily arXiv ingestion
- [x] AI summary generation
- [x] Web dashboard
- [ ] Integration with DARIS for automated literature review
- [ ] Multi-source aggregation (IEEE Xplore, ScienceDirect)
- [ ] Personalized recommendation engine

## Tech Stack

JavaScript · Node.js · Python · OpenAlex API · LLM APIs · HTML/CSS

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=disdorqin/power-papers-daily&type=Date)](https://star-history.com/#disdorqin/power-papers-daily&Date)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT — see [LICENSE](LICENSE).
