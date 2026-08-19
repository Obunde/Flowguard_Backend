import time
from sqlalchemy import create_engine, text

# Updated with the URL-encoded password
engine = create_engine('postgresql://postgres:Kabarnet%409@localhost:5432/kpc_predictive_maintenance')

def run_micro_batch():
    print("⚙️ Starting Pipeline Orchestrator. Press Ctrl+C to stop.")
    
    while True:
        try:
            print(f"[{time.strftime('%H:%M:%S')}] Refreshing Gold Materialized View...")
            
            with engine.begin() as conn:
                # This single command forces Postgres to update the ML features
                conn.execute(text("REFRESH MATERIALIZED VIEW gold_ml_features;"))
                
            print("✅ Refresh complete. Dashboard and ML views updated.")
            
            # Wait 15 seconds before the next refresh
            time.sleep(15)
            
        except KeyboardInterrupt:
            print("\n🛑 Orchestrator stopped.")
            break
        except Exception as e:
            print(f"Pipeline Error: {e}")
            time.sleep(15)

if __name__ == "__main__":
    run_micro_batch()