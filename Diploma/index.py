import random

import ydb.iam
from db.model.user_entity import User
from db.sql_tools import parse_sql, run_sql
from exception.LoginException import LoginExeption

# Constants
create_user_db = (
    "INSERT INTO user (id, name, surname, email, password_hash) "
    "VALUES (:id, :name, :surname, :email, :password_hash);"
)

select_recycle_record = (
    "SELECT * FROM user WHERE email = :email "
    "AND password_hash = :password_hash;"
)

# creates connection to YDB
iam_token = "t1.9euelZqQmseOmZ3Ml5fKl5fLyI6ZmO3rnpWanMbPmpeMlpPGj86UmczLxp3l8_dDOzdN-e8Hcw0v_t3z9wNqNE357wdzDS_-zef1656VmpqMypXLkJnLi8yaxomdys7O7_zF656VmpqMypXLkJnLi8yaxomdys7O.k2MODr6Lz0_VQYhNNd5BL4Cuza48wGWjkTxdBHbYN16JUYAubkg8DpJhdlcl9S9qgr43VUYIkAAxcdmpoK2nCg"

driver_config = ydb.DriverConfig(
    'grpcs://ydb.serverless.yandexcloud.net:2135',
    '/ru-central1/b1g57aekkvt3nitkqvs3/etnutkm6qrd2jpal2ehc',  # unique token for specific cluster
    credentials=ydb.AccessTokenCredentials(iam_token)
)
driver = ydb.Driver(driver_config)
driver.wait(fail_fast=True, timeout=5)
pool = ydb.SessionPool(driver)

def auth(email, password_hash):
    values = {
        "email": email,
        "password_hash": password_hash
    }
    result = run_sql(parse_sql(select_recycle_record, values), pool)
    user_ids = []
    for row_item in result:
        rows = row_item.rows
        for row in rows:
            uid = row['id']
            user_ids.append(uid)

    if len(user_ids) == 0 or len(user_ids) > 1:
        raise LoginExeption()

    return user_ids[0]


def create_user(name, surname, email, password_hash):
    user_record_db = User(
        random.getrandbits(62),
        name,
        surname,
        email,
        password_hash
    )

    values = {
        "id": user_record_db.id,
        "name": user_record_db.name,
        "surname": user_record_db.surname,
        "email": user_record_db.email,
        "password_hash": user_record_db.password_hash
    }

    run_sql(parse_sql(create_user_db, values), pool)

# server handler
def handler(event, context):
    # creates user
    if event["httpMethod"] == "POST":
        name = event["params"]["name"]
        surname = event["params"]["surname"]
        email = event["params"]["email"]
        password_hash = event["params"]["password_hash"]
        create_user(name, surname, email, password_hash)
        return {
            'statusCode': 200
        }
    elif event["httpMethod"] == "GET":
        email = event["params"]["login"]
        password_hash = event["params"]["password_hash"]
        user_id = auth(email, password_hash)
        return {
            'statusCode': 200,
            'body': user_id
        }
    else:
        return {
            'statusCode': 404,
            'body': 'Not found'
        }
