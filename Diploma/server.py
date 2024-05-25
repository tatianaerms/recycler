import random

import ydb.iam
from db.model.material_to_record_entity import MaterialToRecord
from db.model.recycle_record_entity import RecycleRecord
from db.sql_tools import parse_sql, run_sql
from dto.material_to_record_response_dto import MaterialToRecordResponseDto
from dto.report_response_dto import ReportResponseDto
import json
from utils.mappers import custom_serializer, parse_materials

# Constants
create_recycling_record_sql = (
    "INSERT INTO recycling_record (id, user_id, created_at, comments) "
    "VALUES (:id, :user_id, DATETIME(:created_at), :comments);"
)

create_material_sql = (
    "INSERT INTO material (id, unit_of_weight, material_type_name) "
    "VALUES (:id, :unit_of_weight, :material_type_name);"
)

create_material_to_record_sql = (
    "INSERT INTO record_to_material (id, record_id, material_type_name, count) "
    "VALUES (:id, :record_id, :material_type_name, :count);"
)

select_recycle_record = (
    "SELECT * FROM recycling_record WHERE user_id = :user_id "
    "AND created_at >= DATETIME(:start_time) "
    "AND created_at <= DATETIME(:end_time);"
)

select_record_to_materials = (
    "SELECT * FROM record_to_material WHERE record_id = :record_id;"
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


def get_record_to_marerials(record_id):
    values = {
        "record_id": record_id
    }
    result = run_sql(parse_sql(select_record_to_materials, values), pool)
    record_to_materials = []
    for row_item in result:
        rows = row_item.rows
        for row in rows:
            count = row['count']
            material_type_name = row['material_type_name']
            record_to_materials.append(MaterialToRecordResponseDto(material_type_name, count))
    return record_to_materials


def get_report(start_date, end_date, user_id):
    values = {
        "user_id": user_id,
        "start_time": start_date,
        "end_time": end_date
    }
    result = run_sql(parse_sql(select_recycle_record, values), pool)
    reports = []
    for row_item in result:
        rows = row_item.rows
        for row in rows:
            id = row['id']
            user_id = row['user_id']
            comments = row['comments']
            record_to_materials = get_record_to_marerials(id)
            reports.append(ReportResponseDto(
                user_id, record_to_materials, comments
            ))
    return reports


def assign_material_to_record(material, record, frequency):
    material_to_record_db = MaterialToRecord(
        random.getrandbits(62),
        record.id,
        material.material_type_name,
        frequency
    )
    values = {
        "id": material_to_record_db.id,
        "record_id": material_to_record_db.record_id,
        "material_type_name": material_to_record_db.material_type_name,
        "count": material_to_record_db.count
    }
    run_sql(parse_sql(create_material_to_record_sql, values), pool)


def create_recycling_record(user_id, materials, comments, time):
    recycling_record_db = RecycleRecord(
        random.getrandbits(62),
        user_id,
        time,
        comments
    )

    for material in materials:
        assign_material_to_record(material, recycling_record_db, material.cnt)

    values = {
        "id": recycling_record_db.id,
        "user_id": recycling_record_db.user_id,
        "created_at": recycling_record_db.created_at,
        "comments": recycling_record_db.comments
    }

    run_sql(parse_sql(create_recycling_record_sql, values), pool)  # create recycling record itself

# server handler
def handler(event, context):
    # create recycling record
    if event["httpMethod"] == "POST":
        user_id = int(event["params"]["user_id"])
        materials = parse_materials(event["params"]["materials"])
        comments = event["params"]["comments"]
        date = event["params"]["date"]
        print("-->materials=" + str(materials) + " user_id=" + str(user_id) + " comments=" + comments + " date=" + date)
        create_recycling_record(user_id, materials, comments, date)
        return {
            'statusCode': 200
        }
    elif event["httpMethod"] == "GET":
        user_id = int(event["params"]["user_id"])
        start = event["params"]["start_time"]
        end = event["params"]["end_time"]
        reports = get_report(start, end, user_id)
        return {
            'statusCode': 200,
            'body': json.dumps(reports, default=custom_serializer, indent=4, ensure_ascii=False)
        }
    else:
        return {
            'statusCode': 404,
            'body': 'Not found'
        }
