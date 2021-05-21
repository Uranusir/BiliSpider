import datetime

now = datetime.datetime.now()
d2 = datetime.datetime.strptime('2020-10-01 00:00:00', '%Y-%m-%d %H:%M:%S')
delta = now - d2
print (delta.days)