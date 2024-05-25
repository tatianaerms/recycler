import ydb


def parse_sql(query, values):
    for key, value in values.items():
        if isinstance(value, str):
            query = query.replace(f":{key}", f"'{value}'")
        else:
            query = query.replace(f":{key}", str(value))
    return query


def run_sql(sql, pool):
    print("Running SQL query:", sql)
    return pool.retry_operation_sync(lambda s: s.transaction().execute(
        sql,
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    ))
