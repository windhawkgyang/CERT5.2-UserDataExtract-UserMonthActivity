# coding:utf-8
# 本程序脚本主要针对CERT5.2的数据格式，针对每个用户提取其对应的日志数据
# 本程序Main_0的主要任务是将混在一起的所有用户所有时间的单域行为整理为用户/日期/单域行为记录
# 正常的思路应当是读入全部五种行为域数据，然后循环每个用户的每一天分别记录形成文件，但是这样要求内存足够大，遍历足够快，否则无法程序实现；
# 因此Main_0只完成特定的一项工作：
# 1. 读入获取CERT5.2全部2000个用户的User_id作为用户名循环列表：Users_CERT52 = []
# 2. 在每个用户的循环中：
# 2.1 分别对于五类行为域模块分别进行：
# 2.1.1 遍历该域行为中该用户的所有记录，得到其存在的一个日期列表User_Months = [] and User_Days = []分别用于建立月目录与日期目录
# 2.1.2 按照日期建立相应的月份目录与日期目录
# 2.1.3 然后重新遍历用户的每一个月每一天，将该天的该域所有行为写到对应文件中，关闭，继续下一天；
# 2.2 遍历其他所有行为域，得到该用户的第一版记录；

# 需要注意的是，再提取记录时不包括ID与内容数据，即
# Logon: date,user,pc,activity
# File: date,user,pc,filename,activity,to_removable_media,from_removable_media
# HTTP: date,user,pc,url
# Email:  date,user,pc,to,cc,bcc,from,activity,size,attachments
# Device: date,user,pc,file_tree,activity
# 实际编写时需要重新确认原始数据格式与要提取的数据格式

import os # 用于创建目录等应用
import sys # 用于返回当前目录，以及关闭程序等
import User_Month_Day_Extract




# 开始上述程序编写
print '本程序主要用于从CERT5.2中提取用户-月-日-行为域数据...\n\n'
print '.......<<<<<<程序即将开始>>>>>>......\n\n'

print '首先写死CERT5.2的源数据地址，不同机器上需要重新填写...\n'
CERTPath = r'G:\r5.2'
CERT_LDAP_Path = r'G:\r5.2\LDAP'

print '依据psychological文件确定所有用户ID列表...\n'
filePsy = open(CERTPath + '\\' + 'psychometric.csv', 'r')
# employee_name,user_id,O,C,E,A,N
filePsy_lst = filePsy.readlines()
filePsy.close()
Users_CERT52 = []
for line in filePsy_lst:
    line_lst = line.strip('\n').strip(',').split(',')
    if line_lst[1] == 'user_id':
        continue
    Users_CERT52.append(line_lst[1])
print 'CERT5.2中所有用户统计完毕，共有： ',len(Users_CERT52), 'like : ', Users_CERT52[:10], '\n\n'




# 开始按照每个用户遍历，分别进入每个行为域数据的循环
# 在此之前，每个用户需要建立相应的日期列表，并进行初始目录的建立
# 首先指定每个行为域存在的路径
LogonPath = CERTPath + '\\' + 'logon.csv'
FilePath = CERTPath + '\\' + 'file.csv'
HttpPath = CERTPath + '\\' + 'http.csv'
EmailPath = CERTPath + '\\' + 'email.csv'
DevicePath = CERTPath + '\\' + 'device.csv'

# 进入每个用户的大循环
# 尝试将所有用户的记录月份日期信息保存在一个大的CSV中
Results_Path = r'G:\GitHub\Essay-Experiments\CERT5.2-Results'  # CERT5.2数据的存放位置，不更新到GitHub
Results_Path = Results_Path + '\\' + 'CERT5.2-Users-Records' # 更新目录路径
if os.path.exists(Results_Path) == False:
    os.makedirs(Results_Path + '\\' + 'CERT5.2-Users-Records')
# sys.exit()
UserDate = open('User-Date-CERT52.csv', 'w')
for user in Users_CERT52[:1]:
    # 第一件工作是获得用户的两个时间列表
    User_Months = []
    User_Days = []
    Flag_Activity = []
    for path in [LogonPath, FilePath, HttpPath, EmailPath, DevicePath]:
        User_Months, User_Days, flag_activity = User_Month_Day_Extract.Extract_Month_Day(user, path, User_Months, User_Days)
        print path, ': ', user, '分析完毕...\n'
        Flag_Activity.append(flag_activity)
    print user, ' 对应的记录月份为： ', User_Months, '\n'
    print user, ' 对应的记录日期为：', User_Days, '\n'
    print '......<<<<<<', user, '记录月份与日期统计完毕>>>>>>......\n\n'
    UserDate.write(user)
    UserDate.write('\n')
    UserDate.write('Months')
    for i in range(len(User_Months)):
        UserDate.write(User_Months[i])
        UserDate.write(',')
    UserDate.write('\n')
    UserDate.write('Days')
    UserDate.write(',')
    for j in range(len(User_Days)):
        UserDate.write(User_Days[j])
        UserDate.write(',')
    UserDate.write('\n')
    print '......<<<<<<', user, '记录月份日期数据写入完毕>>>>>>......\n\n'
    print '开始依据用户的记录月份与日期数据建立目录...\n'
    # 通过构建一个目录列表的方式直接初始化建立目录
    # 依次读取目录列表，作为路径的月份部分
    # 依次读取日期列表，作为日期的部分
    # 直接创建上述目录
    # G:\GitHub\Essay-Experiments\CERT5.2-Results\CERT5.2-Users-Records\CERT5.2-Users-Records
    # 创建一个用户目录
    UserPath = Results_Path + '\\' + user
    if os.path.exists(UserPath) == False:
        # 不存在则创建
        os.makedirs(UserPath)
    for month in User_Months:
        User_Month_Path = UserPath + '\\' + month
        if os.path.exists(User_Month_Path) == False:
            os.makedirs(User_Month_Path)
        for day in User_Days:
            # date: 2011-01-13
            if day[0:7] != month: #不属于该月份，跳过
                continue
            User_Month_Day_Path = User_Month_Path + '\\' + day
            if os.path.exists(User_Month_Day_Path) == False:
                os.makedirs(User_Month_Day_Path)
        print user, month, '目录创建完毕...\n\n'
    print '......<<<<<<', user, '记录月份日期目录初始化完毕>>>>>>......\n\n'


    print '......<<<<<<', '开始正式将该用户的数据写入到对应目录','>>>>>>......\n\n'
    # LogonPath = CERTPath + '\\' + 'logon.csv'
    # FilePath = CERTPath + '\\' + 'file.csv'
    # HttpPath = CERTPath + '\\' + 'http.csv'
    # EmailPath = CERTPath + '\\' + 'email.csv'
    # DevicePath = CERTPath + '\\' + 'device.csv'
    # 需要注意的是，再提取记录时不包括ID与内容数据，即
    # Logon: date,user,pc,activity
    # File: date,user,pc,filename,activity,to_removable_media,from_removable_media
    # HTTP: date,user,pc,url
    # Email:  date,user,pc,to,cc,bcc,from,activity,size,attachments
    # Device: date,user,pc,file_tree,activity
    # 实际编写时需要重新确认原始数据格式与要提取的数据格式
    # Flag_Activity = [Counts_Logon, Counts_File, Counts_HTTP, Counts_Email, Counts_Device]
    print '......<<<<<<开始分析 ', user, ':', LogonPath, '>>>>>>......\n'
    if Flag_Activity[0] > 0:
        for day in User_Days:
            f_day_path = UserPath + '\\' + day[0:7] + '\\' + day + '\\' + 'Logon.csv'
            f_day = open(f_day_path, 'w')
            with open(LogonPath, 'r') as f:
                for line in f:
                    line_lst = line.strip('\n').strip(',').split(',')
                    # Logon原始数据格式：id,date,user,pc,activity
                    # Logon目标数据格式：Logon: date,user,pc,activity
                    if line_lst[2] == 'user':
                        continue
                    if line_lst[2] != user:
                        continue
                    y, m, d = User_Month_Day_Extract.Extract_Date(line_lst[1])
                    if y + '-' + m + '-' + d != day:
                        continue
                    for ele in line_lst[1:]:
                        f_day.write(ele)
                        f_day.write(',')
                    f_day.write('\n')
            print user, day, 'Logon数据写入完毕...\n\n'
        print '......<<<<<<', user, 'Logon数据写入完毕>>>>>>......\n\n'
    else:
        print user, ' 不存在Logon记录，不写入文件...\n'

    print '......<<<<<<开始分析 ', user, ':', FilePath, '>>>>>>......\n'
    if Flag_Activity[1] > 0:
        for day in User_Days:
            f_day_path = UserPath + '\\' + day[0:7] + '\\' + day + '\\' + 'File.csv'
            f_day = open(f_day_path, 'w')
            with open(FilePath, 'r') as f:
                for line in f:
                    line_lst = line.strip('\n').strip(',').split(',')
                    # Logon原始数据格式：id,date,user,pc,filename,activity,to_removable_media,from_removable_media,content
                    # Logon目标数据格式：date,user,pc,filename,activity,to_removable_media,from_removable_media
                    if line_lst[2] == 'user':
                        continue
                    if line_lst[2] != user:
                        continue
                    y, m, d = User_Month_Day_Extract.Extract_Date(line_lst[1])
                    if y + '-' + m + '-' + d != day:
                        continue
                    print '当前的记录是：', line_lst, '\n', line_lst[1:-1], '\n\n'
                    for ele in line_lst[1:-1]:
                        f_day.write(ele)
                        f_day.write(',')
                    f_day.write('\n')
                    #sys.exit()
            print user, day, 'File数据写入完毕...\n\n'
    else:
        print user, ' 不存在File记录，不写入文件...\n'
    print '......<<<<<<', user, 'File数据写入完毕>>>>>>......\n\n'


    print '......<<<<<<开始分析 ', user, ':', HttpPath, '>>>>>>......\n'
    if Flag_Activity[2] > 0:
        for day in User_Days:
            f_day_path = UserPath + '\\' + day[0:7] + '\\' + day + '\\' + 'HTTP.csv'
            f_day = open(f_day_path, 'w')
            with open(HttpPath, 'r') as f:
                for line in f:
                    line_lst = line.strip('\n').strip(',').split(',')
                    # Logon原始数据格式：id,date,user,pc,url,content
                    # Logon目标数据格式：date,user,pc,url
                    if line_lst[2] == 'user':
                        continue
                    if line_lst[2] != user:
                        continue
                    y, m, d = User_Month_Day_Extract.Extract_Date(line_lst[1])
                    if y + '-' + m + '-' + d != day:
                        continue
                    for ele in line_lst[1:-1]:
                        f_day.write(ele)
                        f_day.write(',')
                    f_day.write('\n')
            print user, day, 'HTTP数据写入完毕...\n\n'
    else:
        print user, ' 不存在HTTP记录，不写入文件...\n'
    print '......<<<<<<', user, 'HTTP数据写入完毕>>>>>>......\n\n'

    print '......<<<<<<开始分析 ', user, ':', EmailPath, '>>>>>>......\n'
    if Flag_Activity[3] > 0:
        for day in User_Days:
            f_day_path = UserPath + '\\' + day[0:7] + '\\' + day + '\\' + 'Email.csv'
            f_day = open(f_day_path, 'w')
            with open(EmailPath, 'r') as f:
                for line in f:
                    line_lst = line.strip('\n').strip(',').split(',')
                    # Logon原始数据格式：id,date,user,pc,to,cc,bcc,from,activity,size,attachments,content
                    # Logon目标数据格式：date,user,pc,to,cc,bcc,from,activity,size,attachments
                    if line_lst[2] == 'user':
                        continue
                    if line_lst[2] != user:
                        continue
                    y, m, d = User_Month_Day_Extract.Extract_Date(line_lst[1])
                    if y + '-' + m + '-' + d != day:
                        continue
                    for ele in line_lst[1:-1]:
                        f_day.write(ele)
                        f_day.write(',')
                    f_day.write('\n')
            print user, day, 'Email数据写入完毕...\n\n'
    else:
        print user, ' 不存在Email记录，不写入文件...\n'
    print '......<<<<<<', user, 'Email数据写入完毕>>>>>>......\n\n'

    print '......<<<<<<开始分析 ', user, ':', DevicePath, '>>>>>>......\n'
    if Flag_Activity[4] > 0:
        for day in User_Days:
            f_day_path = UserPath + '\\' + day[0:7] + '\\' + day + '\\' + 'Device.csv'
            f_day = open(f_day_path, 'w')
            with open(DevicePath, 'r') as f:
                for line in f:
                    line_lst = line.strip('\n').strip(',').split(',')
                    # Logon原始数据格式：id,date,user,pc,file_tree,activity
                    # Logon目标数据格式：date,user,pc,file_tree,activity
                    if line_lst[2] == 'user':
                        continue
                    if line_lst[2] != user:
                        continue
                    y, m, d = User_Month_Day_Extract.Extract_Date(line_lst[1])
                    if y + '-' + m + '-' + d != day:
                        continue
                    for ele in line_lst[1:]:
                        f_day.write(ele)
                        f_day.write(',')
                    f_day.write('\n')
            print user, day, 'Device数据写入完毕...\n\n'
    else:
        print user, ' 不存在Device记录，不写入文件...\n'
    print '......<<<<<<', user, 'Device数据写入完毕>>>>>>......\n\n'




















UserDate.close()
sys.exit()





