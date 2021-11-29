import sqlite3,argparse,datetime,sys,time,subprocess,os
sys.path.append("C:/Users/2000005332/AppData/Local/Programs/Python/Python39/Lib/site-packages")
t1=time.time()
import schedule
DHCPClients = []
today = datetime.date.today()
day=str(today).split("-")
try:
    path = os.path.join("/usr/local/avrestor/","WebReports")
    os.mkdir(path)
except FileExistsError:
    pass
try:
    path = os.path.join("/usr/local/avrestor/WebReports/",f"{day[0]}")
    os.mkdir(path)
except FileExistsError:
    pass
try:
    path = os.path.join(f"/usr/local/avrestor/WebReports/{day[0]}/",f"{day[1]}")
    os.mkdir(path)
except FileExistsError:
    pass
try:
    path = os.path.join(f"/usr/local/avrestor/WebReports/{day[0]}/{day[1]}/",f"{day[2]}")
    os.mkdir(path)
except FileExistsError:
    pass
sqlGeneralReports=sqlite3.connect(f"/usr/local/avrestor/WebReports/{day[0]}/{day[1]}/{day[2]}/AvrestorWebReports.db")
sqlGeneralReports.execute("CREATE TABLE IF NOT EXISTS webConnection (hostname text, ziyaretSayisi INTEGER DEFAULT 1);")
sqlGeneralReports.execute("CREATE TABLE IF NOT EXISTS ipConnectionEx (ipAddress text, ziyaretSayisi INTEGER DEFAULT 1);")
sqlGeneralReports.execute("CREATE TABLE IF NOT EXISTS portConnection (port text, ziyaretSayisi INTEGER DEFAULT 1);")
sqlGeneralReports.execute("CREATE TABLE IF NOT EXISTS countConnection (ip text, ziyaretSayisi INTEGER DEFAULT 1);")
sqlGeneralReports.commit()


def hostnameBul():
    DHCPFile = open("/var/dhcpd/var/db/dhcpd.leases").read().split("\n")
    ARPTable = str(subprocess.check_output("/usr/sbin/arp -a", shell=True)).replace("b'","").split("\\n")[:-1]
    ##print(DHCPFile[-5])
    ##print('\n'.join(map(str, ARPTable)))

    for i in range(len(DHCPFile)):
        if("lease" in DHCPFile[i] and "{" in DHCPFile[i]) and ("active" in (DHCPFile[i+4])):
            MacAdr = DHCPFile[i+7].split(" ")[-1].replace(";"," ").replace(" ","")
            if("hostname" in DHCPFile[i+10]):
                HostName = DHCPFile[i+10].split(" ")[-1].replace(";","").replace('"','')
            elif("hostname" in DHCPFile[i+9]):
                HostName = DHCPFile[i+9].split(" ")[-1].replace(";","").replace('"','')
            else:
                HostName = "?"
            if ([MacAdr,HostName,DHCPFile[i].split(" ")[1]] not in DHCPClients): DHCPClients.append([MacAdr,HostName,DHCPFile[i].split(" ")[1]])
    for i in range(len(ARPTable)):
        temp = ARPTable[i].split(" ")
        if([temp[3], temp[0].split(".")[0], temp[1].replace("(","").replace(")","")] not in DHCPClients): DHCPClients.append([temp[3], temp[0].split(".")[0], temp[1].replace("(","").replace(")","")])
    ##print('\n'.join(map(str, DHCPClients)))
    """
    for line in DHCPFile:
        if "lease" in line and "{" in line:
            #print(line.split(" ")[1])
    """
def genelRapor():
    
    with open(f"/var/log/avrestor/5651_logger/WebLogs_{today}.alert","r+") as f:
        weblogsliste=f.read()
        f.truncate(0)
        f.seek(0)
    weblogsliste=weblogsliste.split("\n")
    for i in weblogsliste:
        try:
            if i.split(" ")[2]!="127.0.0.1":
                if "google" in i:
                    temp = "Google Servisleri"
                elif "microsoft" in i or "login.live.com" in i or "windows" in i or "office" in i:
                    temp = "Microsoft Servisleri"
                elif "avturk" in i or "avrestor" in i:
                    temp = "Avturk"
                elif "spotify" in i:
                    temp = "Spotify"
                elif "whatsapp" in i:
                    temp = "Whatsapp"
                elif "anydesk" in i:
                    temp = "AnyDesk"
                elif "facebook" in i:
                    temp = "Facebook"
                elif "apple" in i:
                    temp = "Apple"
                elif "instagram" in i:
                    temp = "Instagram"
                else:
                    temp = i.split(" ")[3]
                try:
                    if len(list(sqlGeneralReports.execute(f"SELECT * FROM webConnection WHERE hostname ='{temp}'"))) == 0:
                        sqlGeneralReports.execute(f"insert into webConnection (hostname) values ('{temp}')")
                    else:
                        ziyaretSayisi = \
                        list(sqlGeneralReports.execute(f"select ziyaretSayisi from webConnection where hostname ='{temp}'"))[0][0]
                        sqlGeneralReports.execute(f"update webConnection set ziyaretSayisi ='{ziyaretSayisi + 1}' where hostname = '{temp}'")
                    sqlGeneralReports.commit()
                except BaseException as err:
                    print(err)
        except BaseException as err:
            print(err)
        
def log(x):
    with open(f"/var/log/avrestor/5651_logger/5651Logs_{today}.alert","r") as f:
        iplogsliste=f.readlines()
    hostnameBul()

    for i in iplogsliste[x:]:
        disIp=" ".join(i.split()).split(" ")[5]
        disPort=" ".join(i.split()).split(" ")[7]
        iplist=" ".join(i.split()).split(" ")[2]
        zaman=" ".join(i.split()).split(" ")[1]
        try:
            if len(list(sqlGeneralReports.execute(f"SELECT * FROM ipConnectionEx WHERE ipAddress ='{disIp}'"))) == 0:
                sqlGeneralReports.execute(f"insert into ipConnectionEx (ipAddress) values ('{disIp}')")
            else:
                ziyaretSayisi = list(sqlGeneralReports.execute(f"select ziyaretSayisi from ipConnectionEx where ipAddress ='{disIp}'"))[0][0]
                sqlGeneralReports.execute(f"update ipConnectionEx set ziyaretSayisi ='{ziyaretSayisi + 1}' where ipAddress = '{disIp}'")
            if len(list(sqlGeneralReports.execute(f"SELECT * FROM portConnection WHERE port ='{disPort}'"))) == 0:
                sqlGeneralReports.execute(f"insert into portConnection (port) values ('{disPort}')")
            else:
                ziyaretSayisi = list(sqlGeneralReports.execute(f"select ziyaretSayisi from portConnection where port ='{disPort}'"))[0][0]
                sqlGeneralReports.execute(f"update portConnection set ziyaretSayisi ='{ziyaretSayisi + 1}' where port = '{disPort}'")
            if len(list(sqlGeneralReports.execute(f"SELECT * FROM countConnection WHERE ip ='{iplist}'"))) == 0:
                sqlGeneralReports.execute(f"insert into countConnection (ip) values ('{iplist}')")
            else:
                ziyaretSayisi = list(sqlGeneralReports.execute(f"select ziyaretSayisi from countConnection where ip ='{iplist}'"))[0][0]
                sqlGeneralReports.execute(f"update countConnection set ziyaretSayisi ='{ziyaretSayisi + 1}' where ip = '{iplist}'")
            sqlGeneralReports.commit()
            for i in DHCPClients:
                if iplist == i[2]:
                    if i[1]=="?":
                        sql=sqlite3.connect(f"/usr/local/avrestor/WebReports/{day[0]}/{day[1]}/{day[2]}/{iplist}.db")
                        sql.execute(f"CREATE TABLE IF NOT EXISTS logs (zaman text, MACAdresi text, localIp text, disIp text, disPort int);")
                        sql.commit()
                        sql.execute(f"insert into logs (zaman, MACAdresi, localIp, disIp, disPort) values ('{zaman}','{i[0]}','{i[2]}','{disIp}',{disPort})")
                    else:
                        sql=sqlite3.connect(f"/usr/local/avrestor/WebReports/{day[0]}/{day[1]}/{day[2]}/{i[1]}.db")
                        sql.execute(f"CREATE TABLE IF NOT EXISTS logs (zaman text, MACAdresi text, localIp text, disIp text, disPort int);")
                        sql.commit()
                        sql.execute(f"insert into logs (zaman, MACAdresi, localIp, disIp, disPort) values ('{zaman}','{i[0]}','{i[2]}','{disIp}',{disPort})")
                    sql.commit()
                    break
                """
                 iplist[0] = mac
                    iplist[1] = hostname
                    iplist[2] = IP
                """
        except BaseException as err:
            print(err)
            pass
            
def top20():
    yesterday = today - datetime.timedelta(days=1)
    yesterday=str(yesterday).split("-")
    try:
        sqlTop20=sqlite3.connect(f"/usr/local/avrestor/WebReports/{yesterday[0]}/{yesterday[1]}/{yesterday[2]}/AvrestorWebReports.db")
        sqlTop20.execute(f"Delete from webConnection where rowid not IN (select rowid from webConnection order by ziyaretSayisi DESC LIMIT 20)")
        sqlTop20.execute(f"Delete from ipConnectionEx where rowid not IN (select rowid from ipConnectionEx order by ziyaretSayisi DESC LIMIT 20)")
        sqlTop20.execute(f"Delete from portConnection where rowid not IN (select rowid from portConnection order by ziyaretSayisi DESC LIMIT 20)")
        sqlTop20.execute(f"Delete from countConnection where rowid not IN (select rowid from countConnection order by ziyaretSayisi DESC LIMIT 20)")
        sqlTop20.commit()
    except BaseException as err:
        print(err)
        pass
if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('satirSayisi')
        parser.add_argument('temizleAct')
        values = parser.parse_args()
        
        log(int(values.satirSayisi))
        
        genelRapor()
        if(int(values.temizleAct) == 1):
            top20()
        print(time.time()-t1)
    except KeyboardInterrupt:
        print ("Crtl+C Pressed. Shutting down.")