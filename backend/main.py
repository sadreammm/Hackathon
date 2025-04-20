import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from ai_utils import evaluate_prediction
from blockchain_utils import submit_to_chain, mint_nft
from typing import Optional, Dict, Any
from datetime import datetime
import json


app = FastAPI()

class PredictionRequest(BaseModel):
    author: str
    prediction: str

class PredictionResponse(BaseModel):
    clarity: int
    plausibility: int
    summary: str
    category: str
    feedback: str
    is_valid: bool
    prediction_id: Optional[int] = None
    blockchain_tx: Optional[Dict[str, Any]] = None
    nft_minted: bool = False
    timestamp: int = None

def initialize_db():
    conn = sqlite3.connect('predictions.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT NOT NULL,
            clarity INTEGER NOT NULL,
            plausibility INTEGER NOT NULL,
            summary TEXT NOT NULL,
            category TEXT NOT NULL,
            timestamp INTEGER NOT NULL,
            prediction TEXT NOT NULL,
            feedback TEXT NOT NULL,
            is_valid INTEGER NOT NULL,
            blockchain_tx TEXT,
            nft_minted BOOLEAN DEFAULT FALSE)
    ''')
    conn.commit()
    conn.close()

@app.post("/submit_prediction", response_model=PredictionResponse)
async def submit_prediction(request: PredictionRequest):
    evaluation = await evaluate_prediction(request.prediction)

    conn = sqlite3.connect('predictions.db')
    cursor = conn.cursor()
    
    timestamp = int(datetime.now().timestamp())
    blockchain_tx = None
    nft_minted = False

    if evaluation['is_valid']:
        try:
            print("Submitting to blockchain...")
            blockchain_result = await run_in_threadpool(
                submit_to_chain,
                request.author,
                evaluation['clarity'],
                evaluation['plausibility'],
                evaluation['summary'],
                evaluation['category'],
                timestamp
            )

            print("Submitted to blockchain")
            print("Blockchain submission result:", blockchain_result)

            blockchain_tx = json.dumps(blockchain_result)
            nft_minted = blockchain_result.get('nft_minted', False)
        except Exception as e:
            print("Blockchain submission failed:", e)

    cursor.execute('''
        INSERT INTO predictions (author, clarity, plausibility, summary, category, timestamp, prediction, feedback, is_valid, blockchain_tx, nft_minted)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
            request.author,
            evaluation['clarity'],
            evaluation['plausibility'],
            evaluation['summary'],
            evaluation['category'],
            timestamp,
            request.prediction,
            evaluation['feedback'],
            evaluation['is_valid'],
            blockchain_tx,
            nft_minted
    ))
    conn.commit()
    prediction_id = cursor.lastrowid
    conn.close()

    response = PredictionResponse(
        clarity=evaluation['clarity'],
        plausibility=evaluation['plausibility'],
        summary=evaluation['summary'],
        category=evaluation['category'],
        feedback=evaluation['feedback'],
        is_valid=evaluation['is_valid'],
        prediction_id=prediction_id,
        blockchain_tx= json.loads(blockchain_tx) if blockchain_tx else None,
        nft_minted=nft_minted,
        timestamp=timestamp
    )

    status_code = 200 if evaluation['is_valid'] else 220

    return JSONResponse(
        content=response.dict(),
        status_code=status_code
    )

@app.get("/get_prediction/{prediction_id}")
async def get_prediction(prediction_id: int):
    conn = sqlite3.connect('predictions.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM predictions WHERE id = ?''', (prediction_id,))
    prediction = cursor.fetchone()
    conn.close()

    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    columns = [column[0] for column in cursor.description]
    result = dict(zip(columns, prediction))

    if result['blockchain_tx']:
        result['blockchain_tx'] = json.loads(result['blockchain_tx'])
    
    return result

@app.get("/all_predictions")
async def all_predictions():
    conn = sqlite3.connect('predictions.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM predictions ORDER BY id DESC")
    predictions = cursor.fetchall()
    conn.close()

    results = []
    for prediction in predictions:
        columns = [column[0] for column in cursor.description]
        pred_dict = dict(zip(columns, prediction))
        if pred_dict['blockchain_tx']:
            pred_dict['blockchain_tx'] = json.loads(pred_dict['blockchain_tx'])
        results.append(pred_dict)

    return results

@app.on_event("startup")
def startup_event():
    initialize_db()
    print("Database initialized and ready to use.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0" , port=8000, reload=True)
