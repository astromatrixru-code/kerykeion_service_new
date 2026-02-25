from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.core.config import settings
from app.schemas.shema import AstroRequest, SynastryRequest, TransitRequest
from app.services.natalchartruler_service import NatalchartrulerService

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware, 
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,         
    allow_methods=["POST"],
    allow_headers=["*"],
)

natalchartruler_service = NatalchartrulerService()

@app.post("/calculate/natal")
async def calculate_natal(req: AstroRequest):
    try:
        return natalchartruler_service.get_full_report(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/calculate/transit")
async def calculate_transit(req: TransitRequest):
    try:
        return natalchartruler_service.get_transit_report(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/calculate/synastry")
async def calculate_synastry(req: SynastryRequest):
    try:
        return natalchartruler_service.get_synastry_report(req)
    except Exception as e:
        print(f"❌ Synastry Calculation Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))    

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)