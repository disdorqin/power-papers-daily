"""测试 SOTA 论文收集流程"""

import json
import sys
import io
from pathlib import Path

# 修复 Windows 控制台编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def test_data_loading():
    """测试数据加载"""
    data_file = Path("data/sota_papers.jsonl")
    
    if not data_file.exists():
        print("❌ 数据文件不存在")
        return False
    
    papers = []
    with open(data_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                papers.append(json.loads(line))
    
    print(f"✅ 成功加载 {len(papers)} 篇论文")
    
    # 检查论文结构
    required_fields = ["title", "arxiv_url", "github_url", "conference"]
    for i, paper in enumerate(papers[:3]):
        print(f"\n论文 {i+1}:")
        print(f"  标题: {paper.get('title', 'N/A')[:60]}...")
        print(f"  会议: {paper.get('conference', 'N/A')}")
        print(f"  GitHub: {'✅' if paper.get('github_url') else '❌'}")
        
        missing = [f for f in required_fields if f not in paper]
        if missing:
            print(f"  ⚠️ 缺少字段: {missing}")
    
    return True

def test_frontend_files():
    """测试前端文件"""
    required_files = [
        "sota.html",
        "css/sota.css",
        "js/sota-app.js",
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} 不存在")
            all_exist = False
    
    return all_exist

def test_github_actions():
    """测试 GitHub Actions 工作流"""
    workflow_file = Path(".github/workflows/sota-collect.yml")
    
    if workflow_file.exists():
        print(f"✅ GitHub Actions 工作流文件存在")
        return True
    else:
        print(f"❌ GitHub Actions 工作流文件不存在")
        return False

def main():
    print("=" * 60)
    print("SOTA 论文收集系统测试")
    print("=" * 60)
    
    print("\n1. 测试数据加载...")
    data_ok = test_data_loading()
    
    print("\n2. 测试前端文件...")
    frontend_ok = test_frontend_files()
    
    print("\n3. 测试 GitHub Actions...")
    workflow_ok = test_github_actions()
    
    print("\n" + "=" * 60)
    if data_ok and frontend_ok and workflow_ok:
        print("✅ 所有测试通过！SOTA 论文收集系统已就绪")
    else:
        print("❌ 部分测试失败，请检查上述输出")
    print("=" * 60)

if __name__ == "__main__":
    main()
