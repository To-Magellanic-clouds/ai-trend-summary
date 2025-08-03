# 更新导入语句
import os
from langchain.graphs import Neo4jGraph

from langchain.chains import GraphCypherQAChain

from src.infrastructure.utils import LLMUtil

# 更新初始化参数
graph = Neo4jGraph(
    url="bolt://47.117.98.209:7687",  # 注意：使用bolt协议和正确的端口
    username="neo4j",
    password="562Huangyihang"
)

provider = LLMUtil.CompatibleOpenAIProvider(os.getenv("ALIYUN_URL"),"ALIYUN_API_KEY")

llm = provider.get_llm(model_name="qwen-turbo-2025-07-15")
chain = GraphCypherQAChain.from_llm(
    llm=llm,
    graph=graph,
    verbose=True
)
# 执行NER查询
result = chain.run("Extract companies and locations from the news: Apple acquires British startup.")