module fintech::fintech {
    
    use sui::table::{Self, Table};
    use std::string::String;
    use sui::event;


    public struct Predictions has key {
        id: UID,
        predictions: Table<u64, Prediction>,
        counter: u64,
    }

    public struct Prediction has key, store {
        id: UID,
        author: address,
        clarity: u8,
        plausibility: u8,
        summary: String,
        category: String,
        timestamp: u64
    }

    public struct ProofOfForecast has key, store {
        id: UID,
        author: address,
        clarity: u8,
        plausibility: u8,
        summary: String,
        category: String,
        timestamp: u64,
    }

    // Events
    public struct PredictionSubmitted has copy, drop {
        id: u64,
        author: address,
        summary: String,
        category: String,
    }

    public struct NFTMinted has copy, drop {
        id: address,
        author: address,
        summary: String,
        timestamp: u64
    }

    fun init(ctx: &mut TxContext) {
        let pred_store = Predictions {
            id: object::new(ctx),
            predictions: table::new<u64, Prediction>(ctx),
            counter: 0
        };
        transfer::share_object(pred_store);
    }
    
    public fun submit_prediction(
        store: &mut Predictions,
        author: address, 
        clarity: u8,
        plausibility: u8,
        summary: String,
        category: String,
        timestamp: u64,
        ctx: &mut TxContext
    ) {
        let id = object::new(ctx);
        let current_count = store.counter;
        
        let prediction = Prediction {
            id,
            author,
            clarity,
            plausibility,
            summary,
            category,
            timestamp
        };

        table::add(&mut store.predictions, store.counter, prediction);
        store.counter = store.counter + 1;
        
        // Emit event
        event::emit(PredictionSubmitted {
            id: current_count,
            author,
            summary,
            category,
        });
    }

    public fun mint_nft(
        author: address,
        clarity: u8,
        plausibility: u8,
        summary: String,
        category: String,
        timestamp: u64,
        ctx: &mut TxContext
    ) {
        
        let id = object::new(ctx);
        let nft_address = object::uid_to_address(&id);
        
        let nft = ProofOfForecast {
            id,
            author,
            clarity,
            plausibility,
            summary,
            category,
            timestamp
        };
        
        // Emit event
        event::emit(NFTMinted {
            id: nft_address,
            author,
            summary,
            timestamp
        });
        
        transfer::public_transfer(nft, author);
    }
    
    // View function to get prediction by index
    public fun get_prediction(store: &Predictions, index: u64): (address, u8, u8, String, String, u64) {
        let prediction = table::borrow(&store.predictions, index);
        (
            prediction.author,
            prediction.clarity,
            prediction.plausibility,
            prediction.summary,
            prediction.category,
            prediction.timestamp
        )
    }
    
    // Get total predictions count
    public fun get_predictions_count(store: &Predictions): u64 {
        store.counter
    }
}