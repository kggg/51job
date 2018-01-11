#!/usr/bin/env python
#coding=utf-8
import requests
from bs4 import BeautifulSoup
import sys, re, time
import MySQLdb
import database
import cgi


class Job:
    def __init__(self, user=None, dbpass=None):
        self._loginurl = 'https://login.51job.com/login.php?lang=c'
        self._login_data = {'lang':'c', 'action':'save','from_domain':'i','loginname': user, 'password': dbpass,'verifycodechked':'0'}
        self._dbcharset = 'utf8'
        self._ua = 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
        self._headers =  {"User-Agent": self._ua, "Referer": "http://www.51job.com"}
        self._session = self.Login()

    def Login(self):
        s = requests.Session()
        res=s.post(self._loginurl,data=self._login_data, headers=self._headers)
        return s

    def GetHtml(self, url):
        f = self._session.get(url, headers=self._headers)
        f.encoding='GBK'
        f.decoding='utf-8'
        return f.text

    def GetJob(self,cont):
        b = []
        soup=BeautifulSoup(cont,"html.parser")
        position=soup.find_all('a', class_='zhn')
        salary=soup.find_all('span', class_='xz')
        company=soup.find_all('a', class_="gs")
        location = soup.find_all("span", class_="dq")
        cdate = soup.find_all('div', class_="rq")
        i = 0
        for each in position:
            a = []
            if salary[i].string == None:
                salary[i].string = u"0/月"
            col1 = each.get("title").rstrip().lstrip()
            a.append(col1)
            col2 = company[i].get("title").rstrip().lstrip()
            a.append(col2)
            col3 = location[i].get_text().rstrip().lstrip()
            a.append(col3)
            col4 = salary[i].get_text().rstrip().lstrip()
            a.append(col4)
            col5 = cdate[i].get_text().rstrip().lstrip()
            i = i + 1
            p = re.compile(r'\d{4}-\d{2}-\d{2}')
            col6 = re.findall(p, col5)
            a.append(col6)
            b.append(a)
        return b

    def WhoSeeMe(self,cont):
        a = []
        soup=BeautifulSoup(cont,"html.parser")
        content=soup.find('div', class_='h1')
        if(content != None):
            col1 = content.a.string.rstrip().lstrip()
            a.append(col1)
            col2 = content.span.string.rstrip().lstrip()
            a.append(col2)
        return a

    def SearchJob(self, cont):
        soup=BeautifulSoup(cont,"html.parser")
        content=soup.find_all('div', attrs={"class": "el"})
        b = {}
        j = 0
        for i in content:
            a = []
            res = i.find_all('p', class_="t1")
            company = i.find_all('span', class_='t2')
            location = i.find_all('span', class_='t3')
            salary = i.find_all('span', class_='t4')
            for tt in res:
                if(tt.a.get_text() == None):
                    pass
                else:
                    a.append(tt.a.get_text().rstrip().lstrip())
                    a.append(tt.a['href'])
            for tt in company:
                a.append(tt.get_text().rstrip().lstrip())
            for ll in location:
                a.append(ll.get_text().rstrip().lstrip())
            for ss in salary:
                a.append(ss.get_text())
            if(len(a) == 5):
                b[j] = a
            else:
                pass
            j += 1
        return b

    def Jobinfo(self, cont):
        soup=BeautifulSoup(cont,"html.parser")
        content=soup.find_all('div', class_='bmsg job_msg inbox')
        a = []
        for i in content:
            i.find('div',class_='mt10').decompose()
            i.find('div',class_='share').decompose()
            i.find('div',class_='clear').decompose()
            a.append(i.get_text())
        addr = soup.find_all('div',attrs={"class": "bmsg inbox"})
        for i in addr:
            r = i.find('p',class_='fp')
            #for j in r:
            #    j.find('span', class_='label').decompose()
            if(r != None):
                a.append(r.get_text())
        company = soup.find('div',attrs={"class": "tmsg inbox"}).get_text()
        a.append(company)
        return a



if __name__ == '__main__':    
    url2='https://i.51job.com/userset/my_apply.php?lang=c'
    url3='https://i.51job.com/userset/resume_browsed.php?lang=c'
    url4='http://search.51job.com/list/190200,000000,2603%252C0127%252C2509%252C2701%252C2504,00,0,06%252C07%252C08,%2B,1,1.html?lang=c&stype=1&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=4&dibiaoid=0&address=&line=&specialarea=00&from=&welfare='
    if(len(sys.argv) < 2):
        print("参数太少, 后面要加用户名")
        sys.exit()

    username = sys.argv[1]
    password = ''
    name = ''
    sqluser = "select * from jobusers where user='%s' limit 1" % username

    mydb = database.Database('blog','127.0.0.1','webuser','Webuser_192', 3306)
    check = mydb.Query(sqluser)
    for row in check:
        password = row['pass']
        name = row['name']
    begintime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print("%s Try to login 51job with user %s, wait ..." % (begintime, name))
    myjob = Job(name,password)
    
    content = myjob.GetHtml(url2)
    job = myjob.GetJob(content)
    sqli = "select id,position,company,applydate from jobs where position=%s and company=%s order by id desc limit 1"
    for jj in job:
        res = mydb.CheckDB(sqli, jj[0],jj[1])
        if not res:
            sql = "insert into jobs (username, position,company,location,salary,applydate) values(%s, %s,%s,%s,%s,%s)"
            values = (username, jj[0], jj[1], jj[2], jj[3], jj[4])
            r = mydb.InsertDB(sql, values)
            print("insert into database %s" %r)
        else:
            pass
    who = myjob.GetHtml(url3)
    seen = myjob.WhoSeeMe(who)
    if len(seen) != 0:
        sqln = "select id,company,seentime from seenme where company=%s and seentime=%s order by id desc limit 1"
        see = mydb.CheckDB(sqln, seen[0], seen[1])
        if not see:
            sql = "insert into seenme (username, company, seentime) values(%s, %s,%s)"
            values = (username, seen[0], seen[1])
            r = mydb.InsertDB(sql, values)
            print("seenme insertid %s" %r)
        else:
            pass

    s = myjob.GetHtml(url4)
    search = myjob.SearchJob(s)
    sqls = "select id,position,company from searchjob where position=%s and company=%s order by id desc limit 1"
    for key, value in search.items():
        check = mydb.CheckDB(sqls, value[0], value[2])
        if not check:
            sqli = "insert into searchjob (username, position,company,location,salary) values(%s, %s,%s,%s,%s)"
            v = (username, value[0],value[2],value[3],value[4])
            res = mydb.InsertDB(sqli, v)
            if res:
                detail = myjob.GetHtml(value[1])
                details = myjob.Jobinfo(detail)
                sqld = "insert into jobdetail (position_id, pinfo, contact,companyinfo) values(%s, %s, %s,%s)"
                vs = (res, details[0],details[1],details[2])
                r = mydb.InsertDB(sqld, vs)
                print("new job search result, %s" %r)
        else:
            pass
    endtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print("%s Done, bye!" %endtime)



