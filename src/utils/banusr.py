import os
import orjson

banend_users_path = "./database/banend_users.json"
if not os.path.exists(banend_users_path):
    with open(banend_users_path, "w", encoding="utf-8") as file:
        file.write("[]")

with open("./database/banend_users.json", "r", encoding="utf-8") as file:
    banend_users = orjson.loads(file.read())


async def banuser(id):
    banend_users.append(id)
    with open("./database/banend_users.json", "w", encoding="utf-8") as file:
        file.write(orjson.dumps(banend_users).decode())


async def unbanuser(id):
    banend_users.remove(id)
    with open("./database/banend_users.json", "w", encoding="utf-8") as file:
        file.write(orjson.dumps(banend_users).decode())
