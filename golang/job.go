package main

import (
	"fmt"
	"github.com/PuerkitoBio/goquery"
	"github.com/axgle/mahonia"
	"io"
	//"io/ioutil"
	"job/querydb"
	"net/http"
	"net/http/cookiejar"
	"net/url"
	"os"
	"strings"
)

func checkerr(err error) {
	if err != nil {
		panic(err)
	}
}

func ConvertToString(src string, srcCode string, tagCode string) string {
	srcCoder := mahonia.NewDecoder(srcCode)
	srcResult := srcCoder.ConvertString(src)
	tagCoder := mahonia.NewDecoder(tagCode)
	_, cdata, err := tagCoder.Translate([]byte(srcResult), true)
	checkerr(err)
	result := string(cdata)
	return result
}

func NewClient() *http.Client {
	jar, err := cookiejar.New(nil)
	checkerr(err)
	return &http.Client{Jar: jar}
}

func Login(lurl string, user string, pass string) *http.Client {
	client := NewClient()
	data := url.Values{}
	data.Add("action", "save")
	data.Add("from_domain", "i")
	data.Add("loginname", user)
	data.Add("password", pass)
	data.Add("verifycodechked", "0")
	req, err := http.NewRequest("POST", lurl, strings.NewReader(data.Encode()))
	checkerr(err)
	req.Header.Add("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")
	req.Header.Add("Content-Type", "application/x-www-form-urlencoded")
	req.Header.Add("Referer", "https://login.51job.com/login.php?lang=c")
	client.Do(req)
	return client
}

func ParseApply(content io.Reader) [][]string {
	doc, err := goquery.NewDocumentFromReader(content)
	checkerr(err)
	var position, company, address, salary, adate []string
	var result [][]string
	doc.Find("a.zhn").Each(func(i int, s *goquery.Selection) {
		p := s.Text()
		p = ConvertToString(p, "gbk", "utf-8")
		p = strings.TrimSpace(p)
		position = append(position, p)
	})
	doc.Find("a.gs").Each(func(i int, s *goquery.Selection) {
		p := s.Text()
		p = ConvertToString(p, "gbk", "utf-8")
		p = strings.TrimSpace(p)
		company = append(company, p)
	})
	doc.Find("span.dq").Each(func(i int, s *goquery.Selection) {
		p := s.Text()
		p = ConvertToString(p, "gbk", "utf-8")
		p = strings.TrimSpace(p)
		address = append(address, p)
	})
	doc.Find("span.xz").Each(func(i int, s *goquery.Selection) {
		p := s.Text()
		p = ConvertToString(p, "gbk", "utf-8")
		p = strings.TrimSpace(p)
		salary = append(salary, p)
	})
	doc.Find("div.rq").Each(func(i int, s *goquery.Selection) {
		p := s.Text()
		p = ConvertToString(p, "gbk", "utf-8")
		p = strings.TrimSpace(p)
		adate = append(adate, p)
	})
	for j, v := range position {
		if v == "" {
			continue
		}
		var str []string
		str = append(str, v, company[j], address[j], salary[j], adate[j])
		result = append(result, str)
	}
	return result
}

func WhoseeMe(content io.Reader) map[string]string {
	doc, err := goquery.NewDocumentFromReader(content)
	checkerr(err)
	who := make(map[string]string)
	doc.Find("div.h1").Each(func(i int, s *goquery.Selection) {
		company := s.Find("a").Text()
		var dd []string
		s.Find("span").Each(func(i int, ss *goquery.Selection) {
			date := ss.Eq(0).Text()
			date = strings.TrimSpace(date)
			dtime := ss.Eq(1).Text()
			dtime = strings.TrimSpace(dtime)
			dd = append(dd, date)
			dd = append(dd, dtime)
		})
		sdate := strings.Join(dd, " ")
		company = ConvertToString(company, "gbk", "utf-8")
		sdate = ConvertToString(sdate, "gbk", "utf-8")
		sdate = strings.TrimSpace(sdate)
		company = strings.TrimSpace(company)
		who[company] = sdate
	})
	return who
}

func SearchJob(content io.Reader) []string {
	doc, err := goquery.NewDocumentFromReader(content)
	checkerr(err)
	var jobgroup []string
	doc.Find("div.el").Each(func(i int, s *goquery.Selection) {
		posit := s.Find("p.t1").Text()
		company := s.Find("span.t2").Text()
		location := s.Find("span.t3").Text()
		salary := s.Find("span.t4").Text()
		posit = ConvertToString(posit, "gbk", "utf-8")
		company = ConvertToString(company, "gbk", "utf-8")
		location = ConvertToString(location, "gbk", "utf-8")
		salary = ConvertToString(salary, "gbk", "utf-8")
		posit = strings.TrimSpace(posit)
		company = strings.TrimSpace(company)
		location = strings.TrimSpace(location)
		salary = strings.TrimSpace(salary)
		if posit != "" {
			jobgroup = append(jobgroup, posit, company, location, salary)
		}
	})
	return jobgroup
}

func main() {
	if len(os.Args) < 2 {
		fmt.Println("The Args less 1, need to provide the user")
		os.Exit(0)
	}
	user := os.Args[1]
	condb, err := querydb.New("127.0.0.1", "root", "", "3306", "blog")
	checkerr(err)
	usersql := "select name,pass from jobusers where user=?"
	userinfo, err := querydb.FetchRows(condb, usersql, user)
	checkerr(err)
	var luser, lpass string
	for _, v := range userinfo {
		luser = v["name"]
		lpass = v["pass"]
	}
	loginurl := "http://login.51job.com/login.php?lang=c"
	cli := Login(loginurl, luser, lpass)
	applyurl := "https://i.51job.com/userset/my_apply.php?lang=c"
	apply, err := cli.Get(applyurl)
	checkerr(err)
	resapply := ParseApply(apply.Body)
	for _, v := range resapply {
		check := "select position,company from jobs where position=? and company=?"
		exists := querydb.CheckExists(condb, check, v[0], v[1])
		if exists {
			continue
		}
		fmt.Println(v[0], v[1], v[2], v[3], v[4])
		isql := "insert into jobs (username,position,company,location,salary,applydate) values(?, ?, ?, ?,?)"
		_, err = querydb.Insert(condb, isql, user, v[0], v[1], v[2], v[3], v[4])
		checkerr(err)
	}
	/*
		surl := "http://search.51job.com/list/190200,000000,2603%252C0127%252C2509%252C2701%252C2504,00,0,06%252C07%252C08,%2B,1,1.html?lang=c&stype=1&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=4&dibiaoid=0&address=&line=&specialarea=00&from=&welfare="
			sjob, err := cli.Get(surl)
			checkerr(err)
			searchjob := SearchJob(sjob.Body)
			for _, v := range searchjob {
				fmt.Println(v)
			}
	*/
	seenme, err := cli.Get("https://i.51job.com/userset/resume_browsed.php?lang=c")
	checkerr(err)
	whoseeme := WhoseeMe(seenme.Body)
	for k, v := range whoseeme {
		checksql := "select company,seentime from seenme where company=? and seentime=?"
		exists := querydb.CheckExists(condb, checksql, k, v)
		fmt.Println(exists)
		if exists {
			continue
		}
		fmt.Println(k, v)
		isql := "insert into seenme (username, company, seentime) values(?, ?, ?)"
		_, err = querydb.Insert(condb, isql, user, k, v)
		checkerr(err)
	}
}
