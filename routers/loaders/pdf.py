import tempfile, os
from routers.utils.engine import Engine
from llama_index.core import SimpleDirectoryReader
from fastapi import APIRouter, UploadFile, HTTPException, Depends

router = APIRouter()

def get_query_engine():
    return Engine()


@router.post("/pdf")
async def file(upload_file: UploadFile, namespace: str, query_engine: Engine = Depends(get_query_engine)):
    """
    Loader: https://llamahub.ai/l/file-pymu_pdf
    """
    file_preview_name, file_extension = os.path.splitext(upload_file.filename)
    if file_extension != '.pdf':
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    with tempfile.NamedTemporaryFile(delete=True, prefix=file_preview_name + '_', suffix=".pdf") as temp_file:
        content = await upload_file.read()
        temp_file.write(content)

        documents = SimpleDirectoryReader(input_files=[temp_file.name]).load_data()

        #loader = await LlamaParse(api_key=engine.llamaparse_key, result_type="markdown").aload_data([temp_file.name])

        await query_engine.load(documents, namespace)
        
    print("Namespaces in query_engine.indexes:")
    for namespace in query_engine.indexes.keys():
        print(namespace)
         
    return {'message': 'File uploaded successfully', 'filename': upload_file.filename, "namespace": namespace}