import time
import numpy as np
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from app.etl.bronze.models import BronzePumpTelemetry

def generate_live_reading(pump_id: str, wear_multiplier: float) -> dict:
    """Simulates a single sensor reading with progressive degradation."""
    return {
        'timestamp': datetime.now(),
        'pump_id': pump_id,
        'vibration_axial_mm_s': round(np.random.normal(2.5, 0.2) + (wear_multiplier * 6.5), 2),
        'vibration_radial_mm_s': round(np.random.normal(2.2, 0.2) + (wear_multiplier * 5.0), 2),
        'temperature_bearing_c': round(np.random.normal(65.0, 1.5) + (wear_multiplier * 35.0), 2),
        'temperature_casing_c': round(np.random.normal(55.0, 1.0) + (wear_multiplier * 20.0), 2),
        'pressure_suction_psi': round(np.random.normal(45.0, 2.0), 2),
        'pressure_discharge_psi': round(np.random.normal(600.0, 10.0) - (wear_multiplier * 80.0), 2),
        'motor_current_amps': round(np.random.normal(120.0, 2.5) + (wear_multiplier * 45.0), 2),
        'motor_voltage_v': round(np.normal(415.0, 5.0), 2) if hasattr(np, 'normal') else round(np.random.normal(415.0, 5.0), 2),
        'rul_hours': max(0, int(1200 - (wear_multiplier * 1200))),
        'failure_risk_7_day': 1 if wear_multiplier > 0.8 else 0
    }

def stream_data(session: Session):
    """Streams simulated KPC sensor data into the database via the Bronze layer."""
    print("🚀 Starting KPC Sensor Stream. Press Ctrl+C to stop.")
    degradation = 0.0 

    while True:
        try:
            reading_data = generate_live_reading('PUMP_01', degradation)
            new_reading = BronzePumpTelemetry(**reading_data)
            
            session.add(new_reading)
            session.commit()
                
            print(f"[{reading_data['timestamp'].strftime('%H:%M:%S')}] 📡 Inserted {reading_data['pump_id']} | Vib: {reading_data['vibration_axial_mm_s']} | Temp: {reading_data['temperature_bearing_c']}")
            
            degradation += 0.005 
            if degradation > 1.0:
                degradation = 0.0 
                print("\n🔧 Pump Replaced. Resetting degradation cycle.\n")

            time.sleep(3) 
            
        except KeyboardInterrupt:
            print("\n🛑 Streaming stopped by user.")
            break
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Database Error: {e}")
            time.sleep(3)
        except Exception as e:
            print(f"Unexpected Error: {e}")
            time.sleep(3)

# Execution entry point
if __name__ == "__main__":
    engine = create_engine('postgresql://postgres:Kabarnet%409@localhost:5432/kpc_predictive_maintenance')
    SessionLocal = sessionmaker(bind=engine)
    with SessionLocal() as db_session:
        stream_data(db_session)