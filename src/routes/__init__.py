# TIP: Initialize package exports here.
from fastapi import APIRouter , UploadFile , File
from routes.schema import UploadResponse , ProcessResponse
from helpers.config import get_settings
import motor.motor_asyncio
from controllers import upload_file, process_file, search_and_answer
from routes.schema import UploadResponse, ProcessResponse, SearchRequest, SearchResponse

#define el 3 API endpoints -> upload , process , search & answer
#create a mongodb connection 3n tre2 motor
#bwsl el frontend bl controllers
settings = get_settings()
#create mongodb client
client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URI)
db= client[settings.MONGODB_DB_NAME]
router = APIRouter(prefix = "/api/v1" , tags = ["api_v1"])
@router.post("/upload" , response_model= UploadResponse)
async def upload(file: UploadFile = File (...)):
    project_id = await upload_file(file = file , db = db)
    return UploadResponse(project_id = project_id , message = "File uploaded successfully")

@router.post("/process/{project_id}", response_model=ProcessResponse)
async def process(project_id: str):
    chunk_count = await process_file(project_id=project_id, db=db)
    return ProcessResponse(
        project_id=project_id,
        chunk_count=chunk_count,
        message="File processed successfully"
    )
@router.post("/search/{project_id}", response_model=SearchResponse)
async def search(project_id: str, request: SearchRequest):
    answer, sources = await search_and_answer(
        project_id=project_id,
        question=request.question,
        db=db
    )
    return SearchResponse(answer=answer, sources=sources)