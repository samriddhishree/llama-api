from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from routers.utils.engine import Engine, global_indexes

from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.core.retrievers import BaseRetriever
from llama_index.core import PromptTemplate
from llama_index.core import get_response_synthesizer
from llama_index.core.query_engine import RetrieverQueryEngine

router = APIRouter()

def get_query_engine():
    return Engine()

class QueryInput(BaseModel):
    prompt: str
    namespace: str
    temperature: float = 0.0

@router.post("/query")
# async def query(input: QueryInput, query_engine: Engine = Depends(get_query_engine)):
async def query(input: QueryInput):

    print("Namespaces in query_engine.indexes:")
    print("Namespaces in global_indexes:")
    for namespace in global_indexes.keys():
        print(namespace)

    print(f"Received input:")
    print(f"Namespace: {input.namespace}")
    print(f"Prompt: {input.prompt}")
    print(f"Temperature: {input.temperature}")

    index = global_indexes.get(input.namespace)

    if index is None:
        raise HTTPException(status_code=404, detail=f"Namespace '{input.namespace}' not found.")
    

    # retireve the top 5 most similar nodes using embeddings
    vector_retriever = index.as_retriever(similarity_top_k=5)
    # retireve the top 5 most similar nodes using embeddings
    bm25_retriever = BM25Retriever.from_defaults(index=index,similarity_top_k=5)

    hybrid_retriever = HybridRetriever(vector_retriever, bm25_retriever)

    qa_prompt_tmpl = (
    "Context information is below.\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Given the context information and not prior knowledge, "
    "answer the query. Be very concise, and complete.\n"
    "If the context information does not contain an answer to the query, "
    "respond with \"No information\"."
    "Query: {query_str}\n"
    "Answer: "
    )

    qa_prompt = PromptTemplate(qa_prompt_tmpl)

    response_synthesizer = get_response_synthesizer(
    text_qa_template=qa_prompt,
    response_mode="compact"
    )

    query_engine = RetrieverQueryEngine.from_args(
    retriever=hybrid_retriever,
    structured_answer_filtering=False,
    response_synthesizer=response_synthesizer
    )

    response = query_engine.query(input.prompt)

    print(response)

    return {
        "input": input.prompt,
        "response": response
    }

class HybridRetriever(BaseRetriever):
    def __init__(self, vector_retriever, bm25_retriever):
        self.vector_retriever = vector_retriever
        self.bm25_retriever = bm25_retriever
        super().__init__()

    def _retrieve(self, query, **kwargs):
        bm25_nodes = self.bm25_retriever.retrieve(query, **kwargs)
        vector_nodes = self.vector_retriever.retrieve(query, **kwargs)

        # combine the two lists of nodes
        all_nodes = []

        node_ids = set()
        for n in bm25_nodes + vector_nodes:
            if n.node.node_id not in node_ids:
                all_nodes.append(n)
                node_ids.add(n.node.node_id)

        return all_nodes