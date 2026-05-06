# TIP: Initialize package exports here.
import os
import uuid
import aiofiles
from fastapi import UploadFile , HTTPException
from helpers.config import get_settings
from datetime import datetime
from processors.pdf_parser import PDFParser
from processors.chunker import CVChunker
from stores.vectordb.provider.QdrantDBClient import QdrantDBClient
from sentence_transformers import SentenceTransformer
from openai import OpenAI

settings = get_settings()

async def upload_file(file: UploadFile , db):
    # awl 7aga validate the file type(pdf)
    if file.content_type not in settings.FILE_ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400 , detail = "File type is not allowed")
    #tany 7aga validate the file size
    contents = await file.read()
    if len(contents) > (settings.FILE_MAX_SIZE_MB * 1024 * 1024):
        raise HTTPException(status_code= 400 , detail= "File is too large")
    # talt 7aga generate project id w save it ll disk
    project_id = str(uuid.uuid4())
    file_dir = os.path.join("assets", project_id)
    os.makedirs(file_dir , exist_ok= True)
    file_path = os.path.join(file_dir , file.filename)
    async with aiofiles.open(file_path , "wb") as f:
        await f.write(contents)
    #a5r 7aga save el project l mongodb
    await db["projects"].insert_one({
        "project_id": project_id,
        "file_name": file.filename,
        "file_size": len(contents),
        "created_at": datetime.utcnow()
    })
    return project_id

async def process_file(project_id: str , db):
    #aa4of el file mn 3l disk
    file_dir = os.path.join("assets", project_id)
    files = os.listdir(file_dir)
    if not files:
        raise HTTPException(status_code=404, detail="No file found")
    file_path = os.path.join(file_dir, files[0])
    #Parse PDF
    parser = PDFParser()
    pages = parser.parse(file_path)
    #a2sm el pdf (chunks)
    chunker = CVChunker(chunk_size_tokens=settings.FILE_CHUNK_SIZE)
    chunks = chunker.chunk_pages(pages, source_file=files[0])
    if not chunks:
        raise HTTPException(status_code=400, detail="No content extracted from file")
    #Embed chunks using OpenAI
    texts = [chunk.text for chunk in chunks]
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    vectors = embedding_model.encode(texts).tolist()
    #Store in Qdrant
    qdrant = QdrantDBClient(
        db_path=settings.VECTOR_DB_PATH,
        distance_metric=settings.VECTOR_DISTANCE_METRIC,
        embedding_dim=settings.EMBEDDING_DIMENSION
    )
    qdrant.create_collection(collection_name=project_id)
    ids = list(range(len(chunks)))
    # payloads = [chunk.metadata for chunk in chunks]
    #kan 3ndy hna mo4kla eni b3ml el metadata bs f kan ay so2al bs2lo ll model bta3y kan by2oly en m3ndo4 el m3loma w mkn4 by3rf ygawb
    payloads = [{**chunk.metadata, "text": chunk.text} for chunk in chunks]
    qdrant.insert_vectors(
        collection_name=project_id,
        vectors=vectors,
        payloads=payloads,
        ids=ids
    )
    #Update MongoDB
    await db["projects"].update_one(
        {"project_id": project_id},
        {"$set": {"chunk_count": len(chunks)}}
    )
    return len(chunks)

async def search_and_answer(project_id: str, question:str, db):
    #awl 7aga embed the question
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    question_vector = embedding_model.encode([question]).tolist()[0]
    #tany 7aga search Qdrant
    qdrant = QdrantDBClient(db_path=settings.VECTOR_DB_PATH, distance_metric=settings.VECTOR_DISTANCE_METRIC , embedding_dim=settings.EMBEDDING_DIMENSION)
    results = qdrant.search(collection_name= project_id , query_vector= question_vector , top_k = 5)
    if not results :
        raise HTTPException(status_code=404, detail="No content found")
    #talt 7aga build context from results
    context = "\n\n".join(
        [r.payload.get("source_file", "") + ": " + r.payload.get("text", str(r.payload)) for r in results])
    #rab3 7aga send to gemini
    context = "\n\n".join(
        [r.payload.get("source_file", "") + ": " + r.payload.get("text", str(r.payload)) for r in results])

    prompt = f"""Based on the following context, answer the question.

    Context:
    {context}

    Question: {question}

    Answer:"""
    llm_client = OpenAI(
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_API_BASE
    )
    response = llm_client.chat.completions.create(
        model=settings.GENERATE_RESPONSE_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=settings.TEMPERATURE,
        max_tokens=settings.MAX_RESPONSE_TOKENS
    )
    answer = response.choices[0].message.content
    #a5r 7aga return el resources
    sources = [r.payload for r in results]
    return answer , sources