from llama_index.llms.anthropic import Anthropic
from llama_index.core import VectorStoreIndex, Settings, StorageContext

from llama_index.postprocessor.jinaai_rerank import JinaRerank
from llama_index.embeddings.jinaai import JinaEmbedding

from decouple import config

global_indexes = {}


class Engine:
    def __init__(self) -> None:
        self.llamaparse_key = config('LLAMA_CLOUD_API_KEY')
        self.anthropic_api_key = config('ANTHROPIC_API_KEY')
        self.jina_api_key = config('JINA_API_KEY')
        self.embedding_model = JinaEmbedding(model="jina-embeddings-v2-base-en", api_key=self.jina_api_key)
        self.rerank_model = JinaRerank(model="jina-reranker-v1-base-en", api_key=self.jina_api_key, top_n=5)
        self.llm_model = Anthropic(model="claude-3-opus-20240229", api_key=self.anthropic_api_key)
        self.indexes = {}


    async def load(self, loader: object, namespace: str):

        Settings.embed_model = self.embedding_model 
        Settings.node_postprocessors= self.rerank_model
        Settings.llm = self.llm_model
        Settings.chunk_size = 512

        #top doesnt work as it doesnt use qdrant yet
        index = VectorStoreIndex.from_documents(loader)
        self.indexes[namespace] = index
        global_indexes.update(self.indexes)  # Assign self.indexes to global_indexes

        print(f"Namespace '{namespace}' loaded successfully.")

        print("Namespaces in self.indexes:")
        for namespace in self.indexes.keys():
            print(namespace)

        return self.indexes[namespace]
    

    async def query(self, prompt: str, namespace: str, temperature: float):
        print("Namespaces in self.indexes:")
        for namespace in self.indexes.keys():
            print(namespace)

        index = self.indexes.get(namespace)
        if index is None:
            raise ValueError(f"Namespace '{namespace}' not found.")

        # Use the query_engine_obj to perform the query
        #response = await query_engine.aquery(prompt)
        
        #return response

    # def create_index(self, namespace: str):
    # # Check if the index exists, and create it if it doesn't
    # # Currently not using QDrant using SImpleVectorStore.. Need to update
    #     client = qdrant_client.QdrantClient(
    #         location = ":memory:"
    #     )
    #     self.vector_store = QdrantVectorStore(
    #         client=client, collection_name=namespace, enable_hybrid=True, batch_size=20
    #     )
    #     Settings.embed_model = self.embedding_model 
    #     Settings.node_postprocessors= self.rerank_model
    #     Settings.llm = self.llm_model
    #     Settings.chunk_size = 512

        # return self.vector_store
    

        # vector_store = self.create_index(namespace)

        # storage_context = StorageContext.from_defaults(vector_store=vector_store)
        # index1 = VectorStoreIndex.from_documents(
        #     loader,
        #     storage_context=storage_context,
        # )
        # self.indexes[namespace] = index1
        # print(index1)
    