import mysql.connector
import datetime

while True:
    mydb = mysql.connector.connect(
        host="192.168.3.14",
        port="988",
        user="BiliBiliSpider",
        passwd="331868381",
        database="BiliBili_ALL"
    )

    mycursor = mydb.cursor()
    sql = "SELECT UID,DATE FROM BiliBili_User_ALL WHERE DATA_Int=0 LIMIT 1"
    mycursor.execute(sql)
    results = mycursor.fetchall()
    print(results)
    Data_INT = datetime.datetime.strptime(results[0][1], '%Y-%m-%d %H:%M:%S')
    Horizen = datetime.datetime.strptime('2020-10-01 00:00:00', '%Y-%m-%d %H:%M:%S')
    DateDiff = Data_INT - Horizen

    sql = '''UPDATE BiliBili_User_ALL SET DATA_Int=%d WHERE UID=%d
        ''' % (int(DateDiff.days), int(results[0][0]))
    print(sql)
    # mycursor.fetchall()
    mycursor = mydb.cursor()
    mycursor.execute(sql)
    mydb.commit()
