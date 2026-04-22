"""SOTA 论文 AI 增强处理 - 生成中文摘要和结构化信息"""

import os
import json
import sys
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List
import requests

import dotenv
import argparse
from tqdm import tqdm

import langchain_core.exceptions
from langchain_openai import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

if os.path.exists('.env'):
    dotenv.load_dotenv()

template_path = os.path.join(os.path.dirname(__file__), "template.txt")
system_path = os.path.join(os.path.dirname(__file__), "system.txt")

try:
    template = open(template_path, "r").read()
    system = open(system_path, "r").read()
except FileNotFoundError:
    # 使用默认模板
    template = "Please analyze the following abstract of papers.\n\nContent:\n{content}"
    system = "You are an expert researcher. Analyze the paper and provide a structured summary in Chinese including: motivation, method, results, and conclusion."


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, required=True, help="jsonline data file")
    parser.add_argument("--max_workers", type=int, default=1, help="Maximum number of parallel workers")
    parser.add_argument("--language", type=str, default="Chinese", help="Output language")
    return parser.parse_args()


def check_github_code(content: str) -> Dict:
    """提取并验证 GitHub 链接"""
    code_info = {}

    # 1. 优先匹配 github.com/owner/repo 格式
    github_pattern = r"https?://github\.com/([a-zA-Z0-9-_]+)/([a-zA-Z0-9-_\.]+)"
    match = re.search(github_pattern, content)
    
    if match:
        owner, repo = match.groups()
        repo = repo.rstrip(".git").rstrip(".,)")
        
        full_url = f"https://github.com/{owner}/{repo}"
        code_info["code_url"] = full_url
        
        # 尝试调用 GitHub API 获取 Stars 数量
        github_token = os.environ.get("TOKEN_GITHUB")
        if github_token:
            try:
                headers = {
                    "Authorization": f"token {github_token}",
                    "Accept": "application/vnd.github.v3+json"
                }
                resp = requests.get(
                    f"https://api.github.com/repos/{owner}/{repo}",
                    headers=headers,
                    timeout=5
                )
                if resp.status_code == 200:
                    repo_data = resp.json()
                    code_info["stars"] = repo_data.get("stargazers_count", 0)
                    code_info["language"] = repo_data.get("language", "")
                    code_info["description"] = repo_data.get("description", "")
            except Exception as e:
                print(f"GitHub API error: {e}", file=sys.stderr)
    
    return code_info


def process_single_item(chain, item: Dict, language: str) -> Dict:
    """处理单篇论文"""
    try:
        title = item.get("title", "")
        authors = item.get("authors", [])
        summary = item.get("summary", "")
        
        # 构建输入内容
        content = f"Title: {title}\nAuthors: {', '.join(authors)}\nAbstract: {summary}"
        
        # 调用 LLM 生成结构化摘要
        try:
            response = chain.invoke({"content": content})
            enhanced_summary = response.content if hasattr(response, 'content') else str(response)
        except langchain_core.exceptions.OutputParserException:
            enhanced_summary = summary
        
        # 提取 GitHub 代码信息
        github_info = check_github_code(f"{summary} {item.get('github_url', '')}")
        
        # 构建增强后的论文信息
        enhanced_item = {
            **item,
            "title": title,
            "authors": authors,
            "summary": summary,
            "details": enhanced_summary,
            "motivation": "",
            "method": "",
            "result": "",
            "conclusion": "",
            "code_info": github_info,
            "language": language,
        }
        
        return enhanced_item
        
    except Exception as e:
        print(f"Error processing item: {e}", file=sys.stderr)
        return item


def main():
    args = parse_args()
    
    # 读取输入数据
    input_file = args.data
    if not os.path.exists(input_file):
        print(f"Error: input file not found: {input_file}", file=sys.stderr)
        sys.exit(1)
    
    papers = []
    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                papers.append(json.loads(line))
    
    print(f"Loaded {len(papers)} papers from {input_file}")
    
    # 初始化 LLM
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model_name = os.environ.get("MODEL_NAME", "gpt-4o-mini")
    language = args.language or os.environ.get("LANGUAGE", "Chinese")
    
    if not api_key:
        print("Warning: OPENAI_API_KEY not set, skipping AI enhancement", file=sys.stderr)
        # 直接输出原始数据
        output_file = input_file.replace(".jsonl", f"_AI_enhanced_{language}.jsonl")
        with open(output_file, "w", encoding="utf-8") as f:
            for paper in papers:
                f.write(json.dumps(paper, ensure_ascii=False) + "\n")
        print(f"Saved {len(papers)} papers to {output_file} (no AI enhancement)")
        return
    
    llm = ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url=base_url,
        temperature=0.3,
    )
    
    system_prompt = SystemMessagePromptTemplate.from_template(system)
    human_prompt = HumanMessagePromptTemplate.from_template(template)
    chat_prompt = ChatPromptTemplate.from_messages([system_prompt, human_prompt])
    chain = chat_prompt | llm
    
    # 并行处理
    enhanced_papers = []
    max_workers = args.max_workers
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_single_item, chain, paper, language): paper
            for paper in papers
        }
        
        for future in tqdm(as_completed(futures), total=len(futures), desc="AI Enhancement"):
            try:
                enhanced_paper = future.result()
                enhanced_papers.append(enhanced_paper)
            except Exception as e:
                print(f"Error in future: {e}", file=sys.stderr)
    
    # 保存增强后的数据
    output_file = input_file.replace(".jsonl", f"_AI_enhanced_{language}.jsonl")
    with open(output_file, "w", encoding="utf-8") as f:
        for paper in enhanced_papers:
            f.write(json.dumps(paper, ensure_ascii=False) + "\n")
    
    print(f"Saved {len(enhanced_papers)} enhanced papers to {output_file}")


if __name__ == "__main__":
    main()
