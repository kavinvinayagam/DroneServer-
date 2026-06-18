import psycopg2

try:
    conn = psycopg2.connect(
        host="127.0.0.1",
        port = 5433,
        database="droneserver",
        user="droneadmin",
        password="DroneAdmin123"
    )

    print("CONNECTED SUCCESSFULLY")

except Exception as e:
    print("ERROR:")
    print(e)