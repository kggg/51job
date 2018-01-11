package main

import (
	"fmt"
	"github.com/PuerkitoBio/goquery"
	"github.com/axgle/mahonia"
	"net/http"
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

func main() {
	surl := "http://search.51job.com/list/190200,000000,2603%252C0127%252C2509%252C2701%252C2504,00,0,06%252C07%252C08,%2B,1,1.html?lang=c&stype=1&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=4&dibiaoid=0&address=&line=&specialarea=00&from=&welfare="
	client := &http.Client{}
	req, err := http.NewRequest("GET", surl, nil)
	checkerr(err)
	req.Header.Add("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")
	req.Header.Add("Referer", "http://www.51job.com")
	//req.Header.Add("Cookie", "your cookie")
	res, err := client.Do(req)
	defer res.Body.Close()
	doc, err := goquery.NewDocumentFromReader(res.Body)
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
		jobgroup = append(jobgroup, posit, company, location, salary)
	})
	for _, v := range jobgroup {
		if v == "" || v == "公司名" || v == "工作地点" || v == "薪资" {
			continue
		}
		fmt.Printf(v)
		fmt.Printf("\n")
	}

}
