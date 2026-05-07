import pymysql

conn = pymysql.connect(
    host="database-1.cxi80iy86th1.ap-south-1.rds.amazonaws.com",
    user="admin",
    password="Deepi#03",
    database="database-1")

print("Connected successfully!")