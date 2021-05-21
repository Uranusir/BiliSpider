import SmartSpider_2_Mysql
import mysql.connector
import SpiderFolONLY
import datetime

# 配置？粉丝数UP主信息更新
DateDiff100w = 2
DateDiff10w = 5
DateDiff1w = 10
DateDiff0 = 20

def getNowInt():    #返回今天得相对值
    now = datetime.datetime.now()
    d2 = datetime.datetime.strptime('2020-10-01 00:00:00', '%Y-%m-%d %H:%M:%S')
    delta = now - d2
    return delta.days


def getUID():
    mydb = mysql.connector.connect(
        host="192.168.3.14",
        port="988",
        user="BiliBiliSpider",
        passwd="331868381",
        database="BiliBili_ALL"
    )
    mycursor = mydb.cursor()
    sql = "SELECT UID,DATA_Int FROM BiliBili_User_ALL WHERE Traversed='0' LIMIT 1"
    mycursor.execute(sql)
    results = mycursor.fetchall()
    print(results)

    if len(results) < 1:   # 100W
        sql = "SELECT UID FROM BiliBili_User_ALL WHERE FollowersNumber>1000000 and DATA_Int<%d LIMIT 1" % (getNowInt() - DateDiff100w)
        print(sql)
        mycursor.execute(sql)
        results = mycursor.fetchall()

        if len(results) < 1:   #10W
            sql = "SELECT UID FROM BiliBili_User_ALL WHERE FollowersNumber>100000 and DATA_Int<%d LIMIT 1" % (
                        getNowInt() - DateDiff10w)
            mycursor.execute(sql)
            results = mycursor.fetchall()

            if len(results) < 1:   #1W
                sql = "SELECT UID FROM BiliBili_User_ALL WHERE FollowersNumber>10000 and DATA_Int<%d LIMIT 1" % (
                        getNowInt() - DateDiff1w)
                mycursor.execute(sql)
                results = mycursor.fetchall()
                if len(results) < 1:   #实在没得更新了
                    sql = "SELECT UID FROM BiliBili_User_ALL WHERE DATA_Int<%d LIMIT 1" % (
                            getNowInt() - DateDiff0)
                    mycursor.execute(sql)
                    results = mycursor.fetchall()

        print("Spider UID:")
        print(results)
        return int(results[0][0])
    else:
        try:
            print("Spider UID Where Flag=0:" + str(results[0][0]))
            return int(results[0])
        except Exception as ErrorMess:
            print(ErrorMess)
            return 0





def main():
    # 1:爬取粉丝数，读取关注人，没见过的关注人加入数据库
    # 2:爬取粉丝数
    ScanTrigger = 2
    i = 3000

    if ScanTrigger == 1:
        while True:
            if i > 3000:
                SmartSpider_2_Mysql.InterFace(getUID(), 1)
                i = 0
            else:
                SmartSpider_2_Mysql.InterFace(getUID(), 0)
                i = i + 1
    else:
        while True:
            if i > 3000:
                SpiderFolONLY.InterFace(getUID(), 1)
                i = 0
            else:
                SpiderFolONLY.InterFace(getUID(), 0)
                i = i + 1


if __name__ == "__main__":
    main()
