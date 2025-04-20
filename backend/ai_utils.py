import os
from openai import OpenAI
import json
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

openai = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

# Update the function for OpenAI to use real-time data
async def evaluate_prediction(prediction_text: str):
    try:
        prompt = f"""
                You are an expert financial prediction evaluator. Analyze the following market prediction:
                {prediction_text} 

                and provide:
                1. Clarity score (0-10) - How clear and specific is the prediction?
                2. Plausibility score (0-10) - How plausible is the prediction based on current market conditions?
                3. Category - What category does this prediction fall into? (crypto, stock, forex, macro, commodities)
                4. A one-line summary of the prediction
                5. Brief constructive feedback
                
                Return your analysis in valid JSON format with the following keys: clarity, plausibility, category, summary, feedback
        """
        response = openai.chat.completions.create(
            model = "gpt-4",
            messages = [{"role": "user", "content": prompt}] 
        )

        data = json.loads(response.choices[0].message.content)
        if (data.get('clarity', 0) + data.get('plausibility', 0)) >= 15:
            data['is_valid'] = True
        else:
            data['is_valid'] = False
        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating prediction: {str(e)}")
