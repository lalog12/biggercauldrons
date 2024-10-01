from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    """ """
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")
    total_green_ml = 0
    total_gold = 0
    with db.engine.begin() as connection:
        green_potions_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory")).scalar()
        total_gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory")).scalar()
        total_green_ml += green_potions_ml
        for barrel in barrels_delivered:
            total_green_ml += barrel.ml_per_barrel * barrel.quantity
            total_gold -= barrel.price * barrel.quantity 
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = :total_green_ml"),
                           [{"total_green_ml": total_green_ml}])
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = :total_gold"),
                           [{"total_gold": total_gold}])
    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """"""
    print(wholesale_catalog)

    with db.engine.begin() as connection:
        green_potions_num = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).scalar()
        if green_potions_num is None:
            green_potions_num = 0
        purchase_green_barrel = 0

        if green_potions_num < 10 and green_potions_num > 0:
            purchase_green_barrel = 1

    return [
        {
            "sku": "SMALL_GREEN_BARREL",
            "quantity": purchase_green_barrel,
        }
    ]

