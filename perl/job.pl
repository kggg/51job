#!/usr/bin/perl
use strict;
use warnings;
use 5.024;
use Mojo::UserAgent;
use Encode;
use DBI;


my $argc = scalar( @ARGV );
if ($argc < 1){
        say "usage: $0 parmas";
        exit(0);
}
my $user = $ARGV[0];

## connect to database
my $dbname="blog"; my $dbhost='127.0.0.1'; my $dbport = 3306;
my $dsn = "dbi:mysql:database=$dbname;hostname=$dbhost;port=$dbport";
my $dbh = DBI -> connect ($dsn, 'root', '', { RaiseError => 1, PrintError => 0 });
my $dbsql = "select name,pass from jobusers where user='$user'";
my $sth = $dbh->prepare($dbsql);
$sth->execute()|| die DBI::err.": ".$DBI::errstr;
my $row = $sth->fetchrow_hashref();
$sth->finish();
my $username = $row->{name}; my $pass = $row->{pass};

# fetch page content
my $login_url = 'http://login.51job.com/login.php?lang=c';
my $ua  = Mojo::UserAgent->new;
$ua = $ua->cookie_jar(Mojo::UserAgent::CookieJar->new);
$ua->transactor->name('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36');
my %formdata = (lang => 'c', action => 'save',from_domain =>'i',loginname => $username, password => $pass,verifycodechked=>'0');
my $applyurl = 'http://i.51job.com/userset/my_apply.php?lang=c';
my $tx = Post($login_url, %formdata);
if($tx) {
        my $res = Get($applyurl);
        my $position = $res->dom->find('a.zhn')->map('text')->join("\n");
        $position = encode("utf-8",decode("gbk",$position));
        my $company = $res->dom->find('a.gs')->map('text')->join("\n");
        $company = encode("utf-8",decode("gbk",$company));
        my $location = $res->dom->find('span.dq')->map('text')->join("\n");
        $location = encode("utf-8",decode("gbk",$location));
        my $salary = $res->dom->find('span.xz')->map('text')->join("\n");
        $salary = encode("utf-8",decode("gbk",$salary));
        my $adate = $res->dom->find('div.rq')->map('text')->join("\n");
        $adate = encode("utf-8",decode("gbk",$adate));
        say "$position $company $location $salary $adate";
}
$dbh->disconnect();


sub Post{
        my($url,  %data ) = @_;
        my $tx = $ua->post($url=>form=>{%data});
        if($tx->success){
                return $tx;
        }else{
                say "post to website failed";
                return 0;
        }
}

sub Get{
        my $url  = shift;
        my $tx = $ua->get($url);
        if($tx->success){
                return $tx->result;
        }else{
                say "Fetch $url failed";
                return 0;
        }
}


