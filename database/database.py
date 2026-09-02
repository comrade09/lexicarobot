"""(©) Codexbotz — modernized for Python 3.12+

Still uses the synchronous `pymongo` driver inside `async def` functions,
same as before — each call briefly blocks the event loop while it waits
on MongoDB. Left as-is by request; swap to `motor` (the async driver) if
that ever becomes a bottleneck worth fixing.
"""

from __future__ import annotations

from typing import Any

import pymongo
from bson import ObjectId

from config import DB_NAME, DB_URI

dbclient = pymongo.MongoClient(DB_URI)
database = dbclient[DB_NAME]

user_data = database["users"]
accounts_data = database["accounts"]


# --- users ---------------------------------------------------------------

async def present_user(user_id: int) -> bool:
    return user_data.find_one({"_id": user_id}) is not None


async def add_user(user_id: int) -> None:
    user_data.insert_one({"_id": user_id})


async def full_userbase() -> list[int]:
    return [doc["_id"] for doc in user_data.find()]


async def del_user(user_id: int) -> None:
    user_data.delete_one({"_id": user_id})


# --- accounts (shared expense tracking) -----------------------------------

async def add_new_person(user_id: int, name: str) -> None:
    accounts_data.insert_one(
        {
            "user_id": user_id,
            "name": name,
            "spent": 0.0,  # Money they owe me
            "owed": 0.0,   # Money I owe them
            "transactions": [],
        }
    )


async def get_people(user_id: int) -> list[dict[str, Any]]:
    return list(accounts_data.find({"user_id": user_id}))


async def get_person_by_id(person_id: str) -> dict[str, Any] | None:
    return accounts_data.find_one({"_id": ObjectId(person_id)})


_TX_FIELD_BY_TYPE = {
    "spent": "spent",
    "owed": "owed",
    "they_paid": "spent",  # reduces what they owe me
    "i_sent": "owed",      # reduces what I owe them
}
_TX_SIGN_BY_TYPE = {"spent": 1, "owed": 1, "they_paid": -1, "i_sent": -1}


async def add_transaction(person_id: str, tx_type: str, amount: float, reason: str, date_str: str) -> None:
    field = _TX_FIELD_BY_TYPE.get(tx_type)
    inc_fields = {field: amount * _TX_SIGN_BY_TYPE[tx_type]} if field else {}

    accounts_data.update_one(
        {"_id": ObjectId(person_id)},
        {
            "$inc": inc_fields,
            "$push": {
                "transactions": {
                    "date": date_str,
                    "amount": amount,
                    "type": tx_type,
                    "reason": reason,
                }
            },
        },
    )


async def get_total_stats(user_id: int) -> tuple[float, float]:
    pipeline = [
        {"$match": {"user_id": user_id}},
        {
            "$group": {
                "_id": None,
                "total_spending": {"$sum": "$spent"},
                "total_debt": {"$sum": "$owed"},
            }
        },
    ]
    result = list(accounts_data.aggregate(pipeline))
    if result:
        return result[0].get("total_spending", 0.0), result[0].get("total_debt", 0.0)
    return 0.0, 0.0
