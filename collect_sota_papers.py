"""SOTA 论文收集器 - 从多个顶会数据源聚合最新 SOTA 论文

数据源：
1. CVPR2026-Papers-with-Code (GitHub)
2. ICCV/ECCV/NeurIPS/ICML/ICLR 等顶会
3. arXiv 最新论文（电力预测/时序相关）

SOTA 过滤标准：
- 必须有 GitHub 开源代码
- 标题或摘要包含 SOTA/benchmark/state-of-the-art 等关键词
- 或者是时序预测/电力预测领域的前沿论文
"""

import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import requests
from tqdm import tqdm


# ============================================================
# 配置
# ============================================================

# 顶会列表
TOP_CONFERENCES = [
    "CVPR",
    "ICCV",
    "ECCV",
    "NeurIPS",
    "ICML",
    "ICLR",
    "AAAI",
    "ACL",
]

# SOTA 关键词（标题或摘要中包含这些词的论文优先）
SOTA_KEYWORDS = [
    "state-of-the-art",
    "state of the art",
    "sota",
    "benchmark",
    "new record",
    "outperforms",
    "superior",
    "best performance",
    "achieves the best",
    "leading",
    "cutting-edge",
    "frontier",
    "breakthrough",
    "novel",
    "advanced",
    "improved",
    "enhanced",
]

# 领域关键词（时序预测/电力预测相关）
DOMAIN_KEYWORDS = [
    # 时序预测
    "time series",
    "time-series",
    "temporal",
    "forecasting",
    "prediction",
    "sequence",
    "long-term",
    "short-term",
    # 电力预测
    "power",
    "electricity",
    "energy",
    "load",
    "demand",
    "grid",
    "renewable",
    "solar",
    "wind",
    # 通用 ML
    "transformer",
    "diffusion",
    "large language model",
    "llm",
    "foundation model",
    "multimodal",
    "vision",
    "generation",
]

# GitHub Stars 阈值（可选，用于进一步过滤）
GITHUB_STARS_THRESHOLD = 0  # 0 表示不限制


# ============================================================
# 数据源采集器
# ============================================================

class CVPRPapersCollector:
    """从 CVPR2026-Papers-with-Code 等 GitHub 仓库收集论文"""

    def __init__(self, repo_url: str = "https://github.com/amusi/CVPR2026-Papers-with-Code"):
        self.repo_url = repo_url
        self.raw_base_url = "https://raw.githubusercontent.com/amusi/CVPR2026-Papers-with-Code/main"

    def collect(self) -> list[dict[str, Any]]:
        """从 GitHub README 解析论文列表"""
        papers = []
        try:
            # 获取 README 内容
            response = requests.get(
                f"{self.raw_base_url}/README.md",
                timeout=30,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            response.raise_for_status()
            readme_text = response.text

            # 解析论文条目
            papers = self._parse_readme(readme_text)
            print(f"[CVPR] 收集到 {len(papers)} 篇论文")
        except Exception as e:
            print(f"[CVPR] 收集失败：{e}", file=sys.stderr)

        return papers

    def _parse_readme(self, text: str) -> list[dict[str, Any]]:
        """从 README Markdown 解析论文信息"""
        papers = []
        lines = text.split("\n")

        current_section = ""
        for line in lines:
            # 检测章节标题
            if line.startswith("###") or line.startswith("##"):
                current_section = line.strip("# ").strip()
                continue

            # 检测论文行（包含 Paper: 链接）
            if "Paper:" in line and "arxiv.org" in line:
                paper = self._parse_paper_line(line, current_section)
                if paper:
                    papers.append(paper)

        return papers

    def _parse_paper_line(self, line: str, section: str) -> dict[str, Any] | None:
        """解析单篇论文行"""
        # 提取标题
        title_match = re.match(r"^\s*[-*]\s*(.+?)\s*$", line)
        if not title_match:
            return None

        title = title_match.group(1).strip()

        # 提取 arXiv 链接
        arxiv_match = re.search(r"https://arxiv\.org/abs/([^\s\)]+)", line)
        arxiv_id = arxiv_match.group(1) if arxiv_match else ""

        # 提取 GitHub 链接
        github_match = re.search(r"https://github\.com/[^\s\)]+", line)
        github_url = github_match.group(0) if github_match else ""

        if not arxiv_id:
            return None

        return {
            "title": title,
            "arxiv_id": arxiv_id,
            "arxiv_url": f"https://arxiv.org/abs/{arxiv_id}",
            "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}",
            "github_url": github_url,
            "conference": "CVPR 2026",
            "section": section,
            "source": "CVPR2026-Papers-with-Code",
            "collected_at": datetime.utcnow().isoformat(),
        }


class ArxivCollector:
    """从 arXiv API 收集最新论文"""

    def __init__(self, categories: list[str] | None = None):
        self.categories = categories or [
            "cs.CV",  # 计算机视觉
            "cs.LG",  # 机器学习
            "cs.AI",  # 人工智能
            "eess.SP",  # 信号处理（电力相关）
        ]

    def collect(self, max_results: int = 200) -> list[dict[str, Any]]:
        """从 arXiv 收集最新论文"""
        papers = []
        try:
            import arxiv

            # 构建搜索查询
            query = " AND ".join([f"cat:{cat}" for cat in self.categories])

            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate,
            )

            for result in arxiv.Client().results(search):
                paper = {
                    "title": result.title,
                    "arxiv_id": result.entry_id.split("/")[-1],
                    "arxiv_url": result.entry_id,
                    "pdf_url": result.pdf_url,
                    "github_url": self._extract_github_url(result.summary),
                    "authors": [author.name for author in result.authors[:5]],
                    "summary": result.summary,
                    "published": result.published.isoformat(),
                    "categories": result.categories,
                    "conference": "arXiv",
                    "source": "arxiv_api",
                    "collected_at": datetime.utcnow().isoformat(),
                }
                papers.append(paper)

            print(f"[arXiv] 收集到 {len(papers)} 篇论文")
        except ImportError:
            print("[arXiv] arxiv 库未安装，跳过", file=sys.stderr)
        except Exception as e:
            print(f"[arXiv] 收集失败：{e}", file=sys.stderr)

        return papers

    def _extract_github_url(self, summary: str) -> str:
        """从摘要中提取 GitHub 链接"""
        match = re.search(r"https://github\.com/[^\s\)]+", summary)
        return match.group(0) if match else ""


class SemanticScholarCollector:
    """从 Semantic Scholar API 收集论文"""

    def __init__(self):
        self.base_url = "https://api.semanticscholar.org/graph/v1/paper/search"

    def collect(self, query: str = "SOTA benchmark", limit: int = 50) -> list[dict[str, Any]]:
        """从 Semantic Scholar 收集论文"""
        papers = []
        try:
            params = {
                "query": query,
                "limit": limit,
                "fields": "title,authors,year,abstract,externalIds,url,tldr,venue",
                "sort": "date:desc",
            }

            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            for item in data.get("data", []):
                github_url = self._extract_github_url(item.get("abstract", ""))

                paper = {
                    "title": item.get("title", ""),
                    "arxiv_id": item.get("externalIds", {}).get("ArXiv", ""),
                    "arxiv_url": f"https://arxiv.org/abs/{item.get('externalIds', {}).get('ArXiv', '')}",
                    "pdf_url": "",
                    "github_url": github_url,
                    "authors": [a.get("name", "") for a in item.get("authors", [])[:5]],
                    "summary": item.get("abstract", ""),
                    "published": f"{item.get('year', '')}-01-01",
                    "categories": [],
                    "conference": item.get("venue", ""),
                    "source": "semantic_scholar",
                    "collected_at": datetime.utcnow().isoformat(),
                }
                papers.append(paper)

            print(f"[Semantic Scholar] 收集到 {len(papers)} 篇论文")
        except Exception as e:
            print(f"[Semantic Scholar] 收集失败：{e}", file=sys.stderr)

        return papers

    def _extract_github_url(self, abstract: str) -> str:
        """从摘要中提取 GitHub 链接"""
        if not abstract:
            return ""
        match = re.search(r"https://github\.com/[^\s\)]+", abstract)
        return match.group(0) if match else ""


# ============================================================
# SOTA 过滤器
# ============================================================

class SOTAFiler:
    """SOTA 论文过滤器"""

    def __init__(
        self,
        require_github: bool = True,
        min_stars: int = GITHUB_STARS_THRESHOLD,
        keywords: list[str] | None = None,
        domain_keywords: list[str] | None = None,
    ):
        self.require_github = require_github
        self.min_stars = min_stars
        self.keywords = keywords or SOTA_KEYWORDS
        self.domain_keywords = domain_keywords or DOMAIN_KEYWORDS

    def filter(self, papers: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """过滤出 SOTA 论文"""
        filtered = []
        for paper in papers:
            if self._is_sota(paper):
                filtered.append(paper)

        print(f"[Filter] {len(papers)} 篇论文 → {len(filtered)} 篇 SOTA 论文")
        return filtered

    def _is_sota(self, paper: dict[str, Any]) -> bool:
        """判断一篇论文是否是 SOTA"""
        # 必须有 GitHub 链接
        if self.require_github and not paper.get("github_url"):
            return False

        # 检查 GitHub Stars（如果设置了阈值）
        if self.min_stars > 0:
            stars = self._get_github_stars(paper.get("github_url", ""))
            if stars < self.min_stars:
                return False

        # 检查标题或摘要是否包含 SOTA 关键词或领域关键词
        title = paper.get("title", "").lower()
        summary = paper.get("summary", "").lower()
        text = f"{title} {summary}"

        # 匹配 SOTA 关键词
        has_sota_keyword = any(kw in text for kw in self.keywords)

        # 匹配领域关键词（时序/电力预测）
        has_domain_keyword = any(kw in text for kw in self.domain_keywords)

        # 满足任一条件即可
        return has_sota_keyword or has_domain_keyword

    def _get_github_stars(self, github_url: str) -> int:
        """获取 GitHub 仓库的 Stars 数量"""
        if not github_url:
            return 0

        try:
            # 提取 owner/repo
            match = re.search(r"github\.com/([^/]+/[^/]+)", github_url)
            if not match:
                return 0

            repo_path = match.group(1)
            # 移除末尾的斜杠或其他字符
            repo_path = repo_path.rstrip("/)")

            response = requests.get(
                f"https://api.github.com/repos/{repo_path}",
                timeout=10,
                headers={
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": "SOTA-Paper-Collector",
                },
            )

            if response.status_code == 200:
                return response.json().get("stargazers_count", 0)
            else:
                return 0
        except Exception:
            return 0


# ============================================================
# 主流程
# ============================================================

def collect_all_papers() -> list[dict[str, Any]]:
    """从所有数据源收集论文"""
    all_papers = []

    # 1. CVPR2026-Papers-with-Code
    print("\n=== 收集 CVPR 2026 论文 ===")
    cvpr_collector = CVPRPapersCollector()
    all_papers.extend(cvpr_collector.collect())

    # 2. arXiv 最新论文
    print("\n=== 收集 arXiv 最新论文 ===")
    arxiv_collector = ArxivCollector()
    all_papers.extend(arxiv_collector.collect(max_results=200))

    # 3. Semantic Scholar
    print("\n=== 收集 Semantic Scholar 论文 ===")
    s2_collector = SemanticScholarCollector()
    all_papers.extend(s2_collector.collect(query="SOTA time series forecasting", limit=50))
    all_papers.extend(s2_collector.collect(query="SOTA power load prediction", limit=50))

    return all_papers


def deduplicate_papers(papers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """去重（基于 arxiv_id 或 title）"""
    seen_ids = set()
    seen_titles = set()
    unique = []

    for paper in papers:
        arxiv_id = paper.get("arxiv_id", "")
        title = paper.get("title", "").lower().strip()

        if arxiv_id and arxiv_id in seen_ids:
            continue
        if title and title in seen_titles:
            continue

        if arxiv_id:
            seen_ids.add(arxiv_id)
        if title:
            seen_titles.add(title)

        unique.append(paper)

    print(f"[Dedup] {len(papers)} 篇 → {len(unique)} 篇（去重后）")
    return unique


def sort_by_date(papers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """按时间倒序排序（最新的在前）"""
    def get_date(paper: dict[str, Any]) -> datetime:
        # 尝试从不同字段获取日期
        for field in ["published", "collected_at"]:
            date_str = paper.get(field, "")
            if date_str:
                try:
                    # 处理 ISO 格式
                    if "T" in date_str:
                        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    else:
                        return datetime.strptime(date_str, "%Y-%m-%d")
                except (ValueError, TypeError):
                    pass
        return datetime.min

    return sorted(papers, key=get_date, reverse=True)


def save_to_jsonl(papers: list[dict[str, Any]], output_path: str) -> None:
    """保存为 JSONL 格式"""
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        for paper in papers:
            f.write(json.dumps(paper, ensure_ascii=False) + "\n")

    print(f"[Save] 已保存 {len(papers)} 篇论文到 {output_path}")


def main():
    """主流程"""
    print("=" * 60)
    print("SOTA 论文收集器")
    print("=" * 60)

    # 1. 收集所有论文
    all_papers = collect_all_papers()
    if not all_papers:
        print("未收集到任何论文，退出")
        sys.exit(1)

    # 2. 去重
    unique_papers = deduplicate_papers(all_papers)

    # 3. SOTA 过滤
    print("\n=== SOTA 过滤 ===")
    filer = SOTAFiler(require_github=True, min_stars=GITHUB_STARS_THRESHOLD)
    sota_papers = filer.filter(unique_papers)

    # 4. 按时间排序
    sorted_papers = sort_by_date(sota_papers)

    # 5. 保存
    output_path = "data/sota_papers.jsonl"
    save_to_jsonl(sorted_papers, output_path)

    # 6. 生成统计信息
    print("\n=== 统计信息 ===")
    print(f"总收集：{len(all_papers)} 篇")
    print(f"去重后：{len(unique_papers)} 篇")
    print(f"SOTA 过滤后：{len(sota_papers)} 篇")

    # 按会议统计
    conference_counts = {}
    for paper in sota_papers:
        conf = paper.get("conference", "Unknown")
        conference_counts[conf] = conference_counts.get(conf, 0) + 1

    print("\n按会议分布：")
    for conf, count in sorted(conference_counts.items(), key=lambda x: -x[1]):
        print(f"  {conf}: {count} 篇")

    print("\n✅ SOTA 论文收集完成！")


if __name__ == "__main__":
    main()
