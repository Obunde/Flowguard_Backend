import time
from sqlalchemy import create_engine, text, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from app.etl.gold.models import GoldMLFeatures

def run_micro_batch(session: Session):
    """Orchestrates the periodic refresh of the Gold ML features view."""
    print("⚙️ Starting Pipeline Orchestrator. Press Ctrl+C to stop.")
    refresh_query = text("REFRESH MATERIALIZED VIEW gold_ml_features;")
    
    while True:
        try:
            print(f"[{time.strftime('%H:%M:%S')}] Refreshing Gold Materialized View...")
            session.execute(refresh_query)
            session.commit()
            print("✅ Refresh complete. Dashboard and ML views updated.")
            time.sleep(15)
        except KeyboardInterrupt:
            print("\n🛑 Orchestrator stopped.")
            break
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Database Error: {e}")
            time.sleep(15)
        except Exception as e:
            print(f"Pipeline Error: {e}")
            time.sleep(15)

def get_ml_features(session: Session, pump_id: str, limit: int = 50):
    """Retrieves the aggregated rolling averages and failure risk metrics."""
    stmt = select(GoldMLFeatures).where(
        GoldMLFeatures.pump_id == pump_id
    ).order_by(GoldMLFeatures.timestamp.desc()).limit(limit)
    return session.scalars(stmt).all()

# Execution entry point
if __name__ == "__main__":
    engine = create_engine('postgresql://postgres:Kabarnet%409@localhost:5432/kpc_predictive_maintenance')
    SessionLocal = sessionmaker(bind=engine)
    with SessionLocal() as db_session:
        run_micro_batch(db_session)