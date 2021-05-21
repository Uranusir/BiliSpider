import urllib.request, urllib.error
import xlwt
import json
import time
import mysql.connector
import datetime

# --------------------parameter-----------------

DBTitle = ["UID", "Name", "FollowersNumber", "FollowingNumber", "Sex", "Photo", "Sign", "Birthday", "Tags", "LiveURL",
           "Traversed", "DATE"]

ExcelTitle = ["个人ID", "昵称", "粉丝数量", "关注他人人数", "性别", "头像", "签名", "生日", "标签", "直播间网址",
              1, "更新日期"]
savePath = r"./BiliBiliUser_Master.xls"
Threshold = 1000000

# -------------------\parameter-----------------


# --------------------BaseURL--------------------

ModelURL = "https://api.bilibili.com/x/relation/followings?vmid=2169841&pn=1&ps=50"

FollowingURL = "https://api.bilibili.com/x/relation/stat?vmid="

BaseURL = "https://api.bilibili.com/x/relation/followings?vmid="
BaseURL_2 = "&pn=1&ps=50"

# --------------------\BaseURL--------------------

DataList = []

def getNowInt():    #返回今天得相对值
    now = datetime.datetime.now()
    d2 = datetime.datetime.strptime('2020-10-01 00:00:00', '%Y-%m-%d %H:%M:%S')
    delta = now - d2
    return delta.days

def Connect2Mysql():
    mydb = mysql.connector.connect(
        host="192.168.3.14",
        port="988",
        user="BiliBiliSpider",
        passwd="331868381",
        database="BiliBili_ALL"
    )
    return mydb


def getData(followingURL, baseURL, UIDStart):
    data = getOneUrl(followingURL + str(UIDStart))
    try:
        dataJson = json.loads(data)
        print(dataJson)
    except Exception:
        print("爬取失败")
        return 0

    followeringNum = dataJson.get("data").get("following")
    followerNum = dataJson.get("data").get("follower")

    mydb = Connect2Mysql()
    mycursor = mydb.cursor()

    UID = dataJson.get("data").get("mid")

    sql = '''UPDATE BiliBili_User_ALL
    SET FollowersNumber=%d,FollowingNumber=%d, Traversed=1, DATE='%s', DATA_Int=%d
    WHERE UID=%d
    ''' % (followerNum, followeringNum, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), getNowInt(), int(UID))
    print('sql: ' + sql)
    mycursor.execute(sql)
    mydb.commit()

    for page in range(0, followeringNum // 50 + 1):
        # time.sleep(4)
        data = getOneUrl(baseURL + str(UIDStart) + "&pn=" + str(page + 1) + "&ps=50")
        try:
            dataJson = json.loads(data)
            # print("即将写入数据：")
            # print(dataJson)
            # print(dataJson.get("data").get("list"))
            # print("-"*30)
            # print(dataJson.get("data").get("list")[0])
            # print("-"*30)
            # print(dataJson.get("data").get("list")[0].get("mid"))
        except Exception as result:
            print("爬取失败:")
            print(result)
            return 0

        if page == followeringNum // 50:
            final = followeringNum % 50
        else:
            final = 50

        for Number in range(0, final):
            try:
                UID = dataJson.get("data").get("list")[Number].get("mid")
                UName = dataJson.get("data").get("list")[Number].get("uname")
                UPhoto = dataJson.get("data").get("list")[Number].get("face")
                USign = dataJson.get("data").get("list")[Number].get("sign")
                UnitData = [int(UID), UName, -1, -1, "", UPhoto, USign, "", "", "", 0,
                            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),getNowInt()]
                DataList.append(UnitData)
            except Exception as e:
                print("Json错误: " + str(e))
                continue

    return 1


def SaveData2DB(datalist):
    mydb = Connect2Mysql()

    for data in datalist:

        mycursor = mydb.cursor()
        UID = data[0]
        sql = "SELECT Traversed FROM BiliBili_User_ALL WHERE UID='%d'" % UID
        mycursor.execute(sql)
        results = mycursor.fetchall()

        if len(results) > 0:
            continue

        print(results)
        if len(results) > 0:
            # print("continue")
            continue
        else:
            mycursor = mydb.cursor()
            sql = '''
            insert into BiliBili_User_ALL (
            UID,Name,FollowersNumber,FollowingNumber,Sex,Photo,Sign,Birthday,Tags,LiveURL,Traversed,DATE,DATA_Int
            )
            values(%s);''' % str(data).strip("[""]")
            print("执行sql: ", end="")
            try:
                print(sql)
                mycursor.execute(sql)
            except Exception as e:
                print("数据库写入错误： " + str(e))
                continue


def SaveData2Excel(SavePath, threshold):
    workbook = xlwt.Workbook(encoding="utf-8")
    worksheet = workbook.add_sheet('UserFollower>%d' % threshold, cell_overwrite_ok=True)

    for k in range(0, len(ExcelTitle)):
        worksheet.write(0, k, ExcelTitle[k])

    mydb = Connect2Mysql()
    mycursor = mydb.cursor()
    sql = "SELECT * FROM BiliBili_User_ALL WHERE FollowersNumber>%d" % threshold
    # print("execute SQL: " + sql)
    mycursor.execute(sql)
    results = mycursor.fetchall()
    # print("result = ")
    # print(results)
    for j in range(0, len(results)):
        # print("No.%d" % j)
        data = results[j]
        for k in range(0, len(data)):
            worksheet.write(j + 1, k, data[k])
    try:
        workbook.save(SavePath)
        print("已将请求数据写入Excel表格")
    except Exception as results:
        print("Excel写入错误: " + str(results))
        return 1


def getOneUrl(url):
    time.sleep(2)
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
    }

    try:
        print(url)
        req = urllib.request.Request(url, headers=header)
        respond = urllib.request.urlopen(req, timeout=5)
        show = respond.read().decode('utf-8')
    except Exception as result:
        print("网站请求错误: " + str(result))
        return 0

    return show


def InterFace(UIDStart, Count):
    getData(FollowingURL, BaseURL, UIDStart)
    SaveData2DB(DataList)
    if Count > 0:
        SaveData2Excel(savePath, Threshold)
    return 1
