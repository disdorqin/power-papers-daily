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

# 顶会 GitHub 仓库列表（Papers-with-Code）
CONFERENCE_GITHUB_REPOS = [
    # CVPR 系列
    {
        "name": "CVPR 2026",
        "url": "https://github.com/amusi/CVPR2026-Papers-with-Code",
        "raw_url": "https://raw.githubusercontent.com/amusi/CVPR2026-Papers-with-Code/main/README.md",
    },
    {
        "name": "CVPR 2025",
        "url": "https://github.com/amusi/CVPR2025-Papers-with-Code",
        "raw_url": "https://raw.githubusercontent.com/amusi/CVPR2025-Papers-with-Code/main/README.md",
    },
    {
        "name": "CVPR 2024",
        "url": "https://github.com/amusi/CVPR2024-Papers-with-Code",
        "raw_url": "https://raw.githubusercontent.com/amusi/CVPR2024-Papers-with-Code/main/README.md",
    },
    # ICCV 系列
    {
        "name": "ICCV 2025",
        "url": "https://github.com/amusi/ICCV2025-Papers-with-Code",
        "raw_url": "https://raw.githubusercontent.com/amusi/ICCV2025-Papers-with-Code/main/README.md",
    },
    {
        "name": "ICCV 2023",
        "url": "https://github.com/amusi/ICCV2023-Papers-with-Code",
        "raw_url": "https://raw.githubusercontent.com/amusi/ICCV2023-Papers-with-Code/main/README.md",
    },
    # ECCV 系列
    {
        "name": "ECCV 2024",
        "url": "https://github.com/amusi/ECCV2024-Papers-with-Code",
        "raw_url": "https://raw.githubusercontent.com/amusi/ECCV2024-Papers-with-Code/master/README.md",
    },
    # AIGC 合集
    {
        "name": "AIGC Papers (CVPR/ICCV/ECCV)",
        "url": "https://github.com/Kobaayyy/Awesome-CVPR2026-CVPR2025-ICCV2025-CVPR2024-ECCV2024-AIGC",
        "raw_url": "https://raw.githubusercontent.com/Kobaayyy/Awesome-CVPR2026-CVPR2025-ICCV2025-CVPR2024-ECCV2024-AIGC/main/CVPR2026.md",
    },
    # 低层视觉
    {
        "name": "Low-Level Vision (CVPR2026)",
        "url": "https://github.com/Kobaayyy/Awesome-CVPR2026-CVPR2025-CVPR2024-CVPR2021-CVPR2020-Low-Level-Vision",
        "raw_url": "https://raw.githubusercontent.com/Kobaayyy/Awesome-CVPR2026-CVPR2025-CVPR2024-CVPR2021-CVPR2020-Low-Level-Vision/master/CVPR2026.md",
    },
    # 视频理解
    {
        "name": "Video Understanding Papers",
        "url": "https://github.com/jinwchoi/awesome-action-recognition",
        "raw_url": "https://raw.githubusercontent.com/jinwchoi/awesome-action-recognition/master/README.md",
    },
    # GAN/生成模型
    {
        "name": "GAN Papers",
        "url": "https://github.com/hindupuravinash/the-gan-zoo",
        "raw_url": "https://raw.githubusercontent.com/hindupuravinash/the-gan-zoo/master/README.md",
    },
    # 视觉 Transformer
    {
        "name": "Vision Transformer Papers",
        "url": "https://github.com/lucidrains/vit-pytorch",
        "raw_url": "https://raw.githubusercontent.com/lucidrains/vit-pytorch/main/README.md",
    },
    # Papers with Code 合集
    {
        "name": "Papers with Code (CVPR/ICCV/ECCV/NeurIPS)",
        "url": "https://github.com/zziz/pwc",
        "raw_url": "https://raw.githubusercontent.com/zziz/pwc/master/README.md",
    },
    # 语义分割
    {
        "name": "Semantic Segmentation Papers",
        "url": "https://github.com/mrgloom/awesome-semantic-segmentation",
        "raw_url": "https://raw.githubusercontent.com/mrgloom/awesome-semantic-segmentation/master/README.md",
    },
    # 目标检测
    {
        "name": "Object Detection Papers",
        "url": "https://github.com/amusi/awesome-object-detection",
        "raw_url": "https://raw.githubusercontent.com/amusi/awesome-object-detection/master/README.md",
    },
    # 人脸检测识别
    {
        "name": "Face Detection and Recognition",
        "url": "https://github.com/ChanChiChoi/awesome-Face_Recognition",
        "raw_url": "https://raw.githubusercontent.com/ChanChiChoi/awesome-Face_Recognition/master/README.md",
    },
    # 超分辨率
    {
        "name": "Super Resolution Papers",
        "url": "https://github.com/YapengTian/Single-Image-Super-Resolution",
        "raw_url": "https://raw.githubusercontent.com/YapengTian/Single-Image-Super-Resolution/master/README.md",
    },
    # 点云处理
    {
        "name": "Point Cloud Papers",
        "url": "https://github.com/Yochengliu/awesome-point-cloud-analysis",
        "raw_url": "https://raw.githubusercontent.com/Yochengliu/awesome-point-cloud-analysis/master/README.md",
    },
    # 3D重建
    {
        "name": "3D Reconstruction Papers",
        "url": "https://github.com/openMVG/awesome_3DReconstruction_list",
        "raw_url": "https://raw.githubusercontent.com/openMVG/awesome_3DReconstruction_list/master/README.md",
    },
    # 图像检索
    {
        "name": "Image Retrieval Papers",
        "url": "https://github.com/VisualLip/awesome-image-retrieval",
        "raw_url": "https://raw.githubusercontent.com/VisualLip/awesome-image-retrieval/master/README.md",
    },
    # GAN Papers (Updated)
    {
        "name": "GAN Papers (Updated)",
        "url": "https://github.com/nightrome/really-awesome-gan",
        "raw_url": "https://raw.githubusercontent.com/nightrome/really-awesome-gan/master/README.md",
    },
    # 强化学习
    {
        "name": "Reinforcement Learning Papers",
        "url": "https://github.com/aikorea/awesome-rl",
        "raw_url": "https://raw.githubusercontent.com/aikorea/awesome-rl/master/README.md",
    },
    # 时序预测
    {
        "name": "Time Series Forecasting (Updated)",
        "url": "https://github.com/rob-med/awesome-TS",
        "raw_url": "https://raw.githubusercontent.com/rob-med/awesome-TS/master/README.md",
    },
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

class ConferencePapersCollector:
    """从 GitHub Papers-with-Code 仓库收集论文"""

    def __init__(self, name: str, raw_url: str, conference: str):
        self.name = name
        self.raw_url = raw_url
        self.conference = conference

    def collect(self) -> list[dict[str, Any]]:
        """从 GitHub README 解析论文列表"""
        papers = []
        try:
            print(f"[{self.name}] 正在获取...")
            response = requests.get(
                self.raw_url,
                timeout=30,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            response.raise_for_status()
            
            papers = self._parse_readme(response.text)
            print(f"[{self.name}] 收集到 {len(papers)} 篇论文")
        except Exception as e:
            print(f"[{self.name}] 收集失败：{e}", file=sys.stderr)

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

            # 检测论文行（包含 arXiv 链接）
            if "arxiv.org" in line.lower() or "arxiv" in line.lower():
                paper = self._parse_paper_line(line, current_section)
                if paper:
                    papers.append(paper)

        return papers

    def _parse_paper_line(self, line: str, section: str) -> dict[str, Any] | None:
        """解析单篇论文行"""
        # 提取标题（多种格式）
        title = ""
        
        # 格式 1: [标题](链接)
        md_link = re.search(r"\[(.+?)\]\(.+?\)", line)
        if md_link:
            title = md_link.group(1).strip()
        
        # 格式 2: **标题**
        if not title:
            bold_match = re.search(r"\*\*(.+?)\*\*", line)
            if bold_match:
                title = bold_match.group(1).strip()
        
        # 格式 3: 行首 - 或 * 开头
        if not title:
            title_match = re.match(r"^\s*[-*]\s*(.+?)(?:\s*\[|\s*\(|\s*$)", line)
            if title_match:
                title = title_match.group(1).strip()
        
        if not title or len(title) < 10:
            return None

        # 提取 arXiv 链接
        arxiv_match = re.search(r"https://arxiv\.org/abs/([^\s\)\]]+)", line)
        arxiv_id = arxiv_match.group(1) if arxiv_match else ""
        
        # 尝试从其他格式提取 arxiv ID
        if not arxiv_id:
            arxiv_id_match = re.search(r"arxiv\.org/abs/(\d+\.\d+)", line)
            if arxiv_id_match:
                arxiv_id = arxiv_id_match.group(1)

        # 提取 GitHub 链接
        github_match = re.search(r"https://github\.com/[^\s\)\]]+", line)
        github_url = github_match.group(0) if github_match else ""

        # 必须有 arxiv ID 或 GitHub 链接
        if not arxiv_id and not github_url:
            return None

        return {
            "title": title,
            "arxiv_id": arxiv_id,
            "arxiv_url": f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else "",
            "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}" if arxiv_id else "",
            "github_url": github_url,
            "conference": self.conference,
            "section": section,
            "source": self.name,
            "collected_at": datetime.utcnow().isoformat(),
        }

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

    def collect(self, max_results: int = 200, categories: list[str] | None = None) -> list[dict[str, Any]]:
        """从 arXiv 收集最新论文"""
        papers = []
        try:
            import arxiv

            # 使用传入的 categories 或默认的
            cats = categories or self.categories
            query = " AND ".join([f"cat:{cat}" for cat in cats])

            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate,
            )

            client = arxiv.Client(page_size=100, delay_seconds=3)
            
            for result in client.results(search):
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
                
                if len(papers) % 100 == 0:
                    print(f"  [{cats[0]}] 已收集 {len(papers)} 篇...", flush=True)

            print(f"[arXiv] 收集到 {len(papers)} 篇论文 (categories: {cats})")
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
        # 来自顶会 Papers-with-Code 仓库的论文，默认已经有开源代码，直接通过
        source = paper.get("source", "")
        if "Papers-with-Code" in source or "Papers with Code" in source:
            return True
        
        # 来自 awesome 列表的论文，默认已经是精选的，直接通过
        if "awesome" in source.lower():
            return True
        
        # 其他来源需要有 GitHub 链接
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

def collect_all_papers(existing_papers: list[dict[str, Any]] = None, data_path: str = None) -> list[dict[str, Any]]:
    """从所有数据源收集论文"""
    all_papers = list(existing_papers) if existing_papers else []

    # 1. 从多个顶会 GitHub 仓库收集
    print("\n=== 收集顶会论文（GitHub Papers-with-Code）===")
    for repo in CONFERENCE_GITHUB_REPOS:
        try:
            collector = ConferencePapersCollector(
                name=repo["name"],
                raw_url=repo["raw_url"],
                conference=repo["name"],
            )
            all_papers.extend(collector.collect())
        except Exception as e:
            print(f"[{repo['name']}] 收集失败：{e}", flush=True)

    # 2. arXiv 最新论文（大量获取 - 目标15000+篇）
    print("\n=== 收集 arXiv 最新论文 ===")
    arxiv_collector = ArxivCollector()
    
    # 主要领域 - 超大量收集
    categories_large = [
        ("cs.CV", 2000),    # 计算机视觉
        ("cs.LG", 2000),    # 机器学习
        ("cs.AI", 1500),    # 人工智能
        ("cs.CL", 1500),    # 计算语言学
        ("eess.SP", 1000),  # 信号处理
        ("eess.IV", 1000),  # 图像处理
        ("stat.ML", 1000),  # 统计机器学习
        ("cs.RO", 800),     # 机器人
        ("cs.NE", 800),     # 神经网络
        ("cs.SD", 600),     # 声音
    ]
    
    for cat, count in categories_large:
        try:
            print(f"  收集 {cat} ({count}篇)...", flush=True)
            papers = arxiv_collector.collect(max_results=count, categories=[cat])
            all_papers.extend(papers)
            print(f"  ✓ {cat} 完成，共 {len(papers)} 篇", flush=True)
            # 增量保存
            if data_path and len(all_papers) % 1000 < count:
                save_to_jsonl(all_papers, data_path)
        except Exception as e:
            print(f"  ✗ {cat} 失败：{e}，已收集 {len(all_papers)} 篇", flush=True)
            # 失败时保存已有数据
            if data_path:
                save_to_jsonl(all_papers, data_path)
    
    # 次要领域 - 大量收集
    categories_medium = [
        "cs.GR", "cs.MM", "cs.HC", "cs.IR", "cs.DB",
        "cs.SE", "cs.CR", "cs.DC", "cs.DS", "cs.AR",
        "cs.NI", "cs.LO", "cs.PL", "cs.CC", "cs.CG",
        "cs.MA", "cs.SC", "cs.SI", "cs.SY", "cs.ET",
    ]
    
    for cat in categories_medium:
        try:
            print(f"  收集 {cat} (500篇)...", flush=True)
            papers = arxiv_collector.collect(max_results=500, categories=[cat])
            all_papers.extend(papers)
            print(f"  ✓ {cat} 完成，共 {len(papers)} 篇", flush=True)
        except Exception as e:
            print(f"  ✗ {cat} 失败：{e}", flush=True)
            # 失败时保存已有数据
            if data_path:
                save_to_jsonl(all_papers, data_path)

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
                        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                        # 统一转换为 naive datetime 用于比较
                        return dt.replace(tzinfo=None)
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
    # 定义数据路径
    DATA_PATH = "data/sota_papers.jsonl"
    
    print("=" * 60)
    print("SOTA 论文收集器")
    print("=" * 60)

    # 0. 加载已有论文（增量收集）
    existing_papers = []
    if Path(DATA_PATH).exists():
        try:
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                existing_papers = [json.loads(line) for line in f if line.strip()]
            print(f"\n[Load] 已加载 {len(existing_papers)} 篇已有论文")
        except Exception as e:
            print(f"\n[Load] 加载失败：{e}")

    # 1. 收集所有论文（增量）
    all_papers = collect_all_papers(existing_papers, DATA_PATH)
    if not all_papers:
        print("未收集到任何论文，退出")
        sys.exit(1)

    # 2. 去重
    unique_papers = deduplicate_papers(all_papers)

    # 3. SOTA 过滤（放宽条件：arXiv论文不强制要求GitHub）
    print("\n=== SOTA 过滤 ===")
    filer = SOTAFiler(require_github=False, min_stars=GITHUB_STARS_THRESHOLD)
    sota_papers = filer.filter(unique_papers)

    # 4. 按时间排序
    sorted_papers = sort_by_date(sota_papers)

    # 5. 保存
    save_to_jsonl(sorted_papers, DATA_PATH)

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

    print("\nSOTA 论文收集完成！")


if __name__ == "__main__":
    main()
