from event_consumer import start
from db import engine, SessionLocal
from common.models import Base, RuleModel
from common.rules import AutomationRule
from fastapi import FastAPI

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # crea le tabelle se non esistono
    Base.metadata.create_all(bind=engine)

    # crea una regola di test se la tabella è vuota
    db = SessionLocal()
    if db.query(RuleModel).count() == 0:
        rule = RuleModel(
            sensor_name="greenhouse_temperature",
            metric_name="temperature",
            operator=">",
            threshold=28,
            actuator_name="cooling_fan",
            target_state="ON"
        )
        db.add(rule)
        db.commit()
    db.close()


if __name__ == "__main__":
    start()    