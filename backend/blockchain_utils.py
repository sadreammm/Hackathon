from pysui import SyncClient, SuiConfig, handle_result
from pysui.sui.sui_txn import SyncTransaction
from pysui.sui.sui_types import ObjectID
from pysui.sui.sui_types import SuiAddress, SuiU64, SuiU8
from fastapi import HTTPException
import os
from dotenv import load_dotenv

load_dotenv()

SUI_RPC_URL = os.getenv("SUI_RPC_URL")
SUI_PRIVATE_KEY = os.getenv("SUI_PRIVATE_KEY")
SUI_ADDRESS = os.getenv("SUI_ADDRESS")
PACKAGE_ID = os.getenv("PREDICTIONS_PACKAGE_ID")
MODULE_NAME = os.getenv("PREDICTIONS_MODULE_NAME")
PREDICTIONS_OBJECT_ID = os.getenv("PREDICTIONS_OBJECT_ID")
GAS_BUDGET = os.getenv("GAS_BUDGET")


sui_config = SuiConfig.user_config(
    rpc_url=SUI_RPC_URL,
    prv_keys=[SUI_PRIVATE_KEY]
)
sui_client = SyncClient(sui_config)

def submit_to_chain(
        author: str,
        clarity: int,
        plausibility: int,
        summary: str,
        category: str,
        timestamp: int 
):
    try:
        tx = SyncTransaction(client=sui_client)
        predictions_obj = ObjectID(PREDICTIONS_OBJECT_ID)
        
        tx.move_call(
            target=f"{PACKAGE_ID}::{MODULE_NAME}::submit_prediction",
            arguments=[
                predictions_obj,
                SuiAddress(author),
                SuiU8(clarity),
                SuiU8(plausibility),
                summary,
                category,
                SuiU64(timestamp)
            ]
        )

        result = handle_result(tx.execute())
        print(result.to_json(indent=2)) 

        if result and hasattr(result, 'effects') and result.effects.status.status == "success":
            nft_minted = False
            if clarity + plausibility >= 15 and clarity >= 6 and plausibility >= 6:
                nft_result = mint_nft(author, clarity, plausibility, summary, category, timestamp)
                if nft_result and nft_result.get("status") == "success":
                    nft_minted = True
                else:
                    print(f"NFT minting encountered an error")

            return {
                "tx_digest": result.digest,
                "status": "success",
                "nft_minted": nft_minted
            }
            
        raise HTTPException(
            status_code=500,
            detail=f"Transaction failed with status: {result.effects.status if result and hasattr(result, 'effects') else 'unknown'}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error submitting to chain: {str(e)}"
        )

def mint_nft(
        author: str,
        clarity: int,
        plausibility: int,
        summary: str,
        category: str,
        timestamp: int
):
    try:
        tx = SyncTransaction(client=sui_client)

        tx.move_call(
            target=f"{PACKAGE_ID}::{MODULE_NAME}::mint_nft",
            arguments=[
                SuiAddress(author),
                SuiU8(clarity),
                SuiU8(plausibility),
                summary,
                category,
                SuiU64(timestamp)
            ]
        )

        result = handle_result(tx.execute())

        print("NFT minting result:") 
        print(result.to_json(indent=2)) 

        if result and hasattr(result, 'effects') and result.effects.status.status == "success":
            return {
                "tx_digest": result.digest,
                "status": "success"
            }
        raise HTTPException(
            status_code=500,
            detail=f"NFT minting failed with status: {result.effects.status if result and hasattr(result, 'effects') else 'unknown'}"
        )            

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"NFT minting failed: {str(e)}"
        )
