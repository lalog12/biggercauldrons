from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int
#Receiving bottled potions. Adding potions to database
# Bobo (bottler) won't call post_deliver function if no ml were given to him/her
@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):
    """ """
    with db.engine.begin() as connection:
        num_potion_green = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).scalar()
        num_potion_green += 1
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_potions = :green_potions"),
            {"green_potions": num_potion_green})
        print(f"potions delievered: {potions_delivered} order_id: {order_id}")

    return "OK"
#Giving potion ml to bottler so he can bring bottled potions
@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    with db.engine.begin() as connection:
        ml_num_green = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory")).scalar()
        if ml_num_green is not None and ml_num_green >= 100:
            ml_num_green -= 100
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = :ml_value"),
                               {"ml_value": ml_num_green})
            return [
                {
                    "potion_type": [0, 100, 0, 0],
                    "quantity": 1,
                }
            ]
        else:
                return [
            {
                "potion_type": [0, 100, 0, 0],
                "quantity": 0,
            }
        ]




        

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.



if __name__ == "__main__":
    print(get_bottle_plan())