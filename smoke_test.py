import os
import sys
import boto3
import pymysql

# AWS SSM Client
client = boto3.client("ssm", region_name="us-east-1")

# Fetch Parameters from Parameter Store
response = client.get_parameters_by_path(
    Path="/application/banking",
    Recursive=True,
    WithDecryption=True
)

params = {
    os.path.basename(param["Name"]): param["Value"]
    for param in response["Parameters"]
}

# Required Parameters
required = [
    "DB_HOST",
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD",
    "DB_PORT"
]

missing = [key for key in required if key not in params]

print("========= Parameter Check =========")

for key in required:
    print(f"{key}: {'✅' if key in params else '❌'}")

if missing:
    print(f"\n❌ Missing Parameters: {missing}")
    sys.exit(1)

print("\n✅ All Parameters Found\n")

# Database Connection Test
try:
    connection = pymysql.connect(
        host=params["DB_HOST"],
        user=params["DB_USER"],
        password=params["DB_PASSWORD"],
        database=params["DB_NAME"],
        port=int(params["DB_PORT"]),
        connect_timeout=10
    )

    cursor = connection.cursor()

    cursor.execute("SHOW TABLES")

    tables = [row[0] for row in cursor.fetchall()]

    print(f"Database : {params['DB_NAME']}")
    print("Tables :")

    for table in tables:
        print(f" - {table}")

    connection.close()

except Exception as e:
    print(f"\n❌ Database Connection Failed")
    print(e)
    sys.exit(1)

print("\n✅ Smoke Test Passed Successfully")