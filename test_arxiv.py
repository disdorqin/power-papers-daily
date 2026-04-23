from collect_sota_papers import ArxivCollector

c = ArxivCollector()
papers = c.collect(max_results=100, categories=['cs.CV'])
print(f'Collected {len(papers)} papers')
if papers:
    print(f'First: {papers[0]["title"]}')
