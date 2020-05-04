#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import csv
import os
from collections import OrderedDict
import datetime
import getpass
import requests
import mysql.connector
import pprint
import json
import sys
import ast

# Globals
current_timestamp = str(datetime.datetime.now().strftime(
    '%Y-%m-%d-%Hh-%Mm'))  # was .strftime('%Y-%m-%d'))
path = os.path.abspath(os.path.dirname(__file__))
csv_file_name = current_timestamp + '-traffic-stats.csv'
csv_file_name_clones = current_timestamp + '-clone-stats.csv'
csv_file_name_referrers = current_timestamp + '-referrer-stats.csv'


def send_request(resource, organization, auth, repo=None):
    """ Send request to specific Github API endpoint
    :param resource: string - specify the API to call
    :param organization: string - specify the repository organization if not owner by username
    :param auth: username:password separated string - if no password specified, interactive dialog used
    :param repo: string - if specified, the specific repository name
    :param headers: dict - if specified, the request headers
    :param params: dict - if specified, the parameters
    :return: response - GET request response, if a tuple then (response, header) responses
    """
    if resource == 'traffic':
        # GET /repos/:owner/:repo/traffic/views <- from developer.github.com/v3/repos/traffic/#views
        base_url = 'https://api.github.com/repos/'
        base_url = base_url + organization + '/' + repo + '/traffic/views'
        response = requests.get(base_url, auth=auth)
        return response
    elif resource == 'repos':
        # GET /user/repos <- from developer.github.com/v3/repos/#list-your-repositories
        base_url = 'https://api.github.com/users/'
        base_url = base_url + organization + '/repos'
        params = {'per_page': '100'}
        response = requests.get(base_url, auth=auth, params=params)
        headers = requests.head(base_url, auth=auth, params=params)
        return (response, headers)
    elif resource == 'clones':
        # GET /repos/:owner/:repo/traffic/clones <- from developer.github.com/v3/repos/traffic/#clones
        base_url = 'https://api.github.com/repos/'
        base_url = base_url + organization + '/' + repo + '/traffic/clones'
        response = requests.get(base_url, auth=auth)
        return response
    elif resource == 'referrers':
        # GET /repos/:owner/:repo/traffic/popular/referrers <- from developer.github.com/v3/repos/traffic/#list-referrers
        base_url = 'https://api.github.com/repos/'
        base_url = base_url + organization + '/' + repo + '/traffic/popular/referrers'
        response = requests.get(base_url, auth=auth)
        return response
    elif resource == 'paths':
        # GET /repos/:owner/:repo/traffic/popular/paths <- from developer.github.com/v3/repos/traffic/#list-paths
        base_url = 'https://api.github.com/repos/'
        base_url = base_url + organization + '/' + repo + '/traffic/popular/paths'
        response = requests.get(base_url, auth=auth)
        return response


def send_request_pagination(url, auth):
    """ Send request to specific Github API endpoint using pagination
    :param url: string - the URL from the "response.links" header
    :param auth: username:password separated string - if no password specified, interactive dialog used
    :param params: dict - if specified, the parameters
    :return: response - a tuple of (response, header) responses
    """
    params = {'per_page': '100'}
    response = requests.get(url, auth=auth, params=params)
    headers = requests.head(url)
    return (response, headers)


def GetIndexTables(db_config={}):
    github_stats_db = mysql.connector.connect(host=db_config['host'], port=db_config['port'],
                                              user=db_config['user'], password=db_config['password'],
                                              database=db_config['database'])
    cursor = github_stats_db.cursor()
    # Index tables follow a pattern
    # Name: Index__<ITEM>s
    # Col1: <ITEM>_ID
    # Col2: <ITEM>
    data={}
    items = ("Title","Referral","Path","Date","Repo")
    data["NEXT_ID"]={}
    for item in items:
        data[item] = {}
        cursor.execute(
            "SELECT COALESCE(MAX(`{0}_ID`),0) + 1 FROM `Index__{0}s`".format(item))
        data["NEXT_ID"][item] = cursor.fetchone()[0]
        if item == "Date":
            sql = ("Select "+'DATE_FORMAT(Date,"%Y-%m-%'+'d")' +
                    " as `{0}`, `{0}_ID` from `Index__{0}s`".format(item))
        else:
            sql = ("Select `{0}`, `{0}_ID` from `Index__{0}s`".format(item))
        cursor.execute(sql)
        result = cursor.fetchall()
        for line in result:
            data[item][line[0]] = line[1]
    cursor.close()
    github_stats_db.close()
    return data

def InsertItemIfNotExists(indexTables, itemList, itemType):
    for item in itemList:
        if not item in indexTables[itemType]:
            indexTables[itemType][item] = indexTables["NEXT_ID"][itemType]
            indexTables["NEXT_ID"][itemType] = indexTables[itemType][item] + 1

def GetList(base, index=None):
    if None!=index:
        if index in base and isinstance(base[index], list):
            return base[index]
        return []
    if isinstance(base, list):
        return base
    return []

def BuildIndexTables(db_config,repos_data):
    indexTables = GetIndexTables(db_config)
    repoList = repos_data.keys()
    InsertItemIfNotExists(indexTables, repoList, "Repo")
    pathList=[]
    referralList=[]
    titleList=[]
    timestampList=[]
    for repo in repoList:
        if not repo in indexTables["Repo"]:
            print "Error, repo \"" + repo + "\" should exist, but doesn\'t in:"
            pprint.pprint(indexTables["Repo"])
            sys.exit(-1)
        for key in sorted(repos_data[repo].keys()):
            if('message' in repos_data[repo][key]):
                print("# message found in \"{}\" response \"{}\": \"{}\"".format(repo, key, repos_data[repo][key]['message']))
        for cloneData in GetList(repos_data[repo]['clones'], 'clones'):
            timestampList.append(str(cloneData['timestamp'][0:10]))
        for trafficData in GetList(repos_data[repo]['traffic'],'views'):
            timestampList.append(str(trafficData['timestamp'][0:10]))
        for pathData in GetList(repos_data[repo]['paths']):
            titleList.append(pathData["title"])
            pathList.append(pathData["path"])
        for referralData in GetList(repos_data[repo]['referrers']):
            referralList.append(referralData['referrer'])
    # Removing data already captured in weekly form
    dateList = sorted(set(timestampList))
    timestampList=[]
    for item in dateList:
        if item < "2020-04-21":
            continue
        timestampList.append(item)
    InsertItemIfNotExists(indexTables, sorted(set(titleList)), "Title")
    InsertItemIfNotExists(indexTables, sorted(set(pathList)), "Path")
    InsertItemIfNotExists(indexTables, sorted(set(referralList)), "Referral")
    InsertItemIfNotExists(indexTables, sorted(set(timestampList)), "Date")
    return indexTables

def GetTrafficValue(traffic, date, item):
    if not date in traffic:
        return str(0)
    if not item in traffic[date]:
        return str(0)
    return str(traffic[date][item])

def BuildAllTables(db_config, reposData, indexTables):

    github_stats_db = mysql.connector.connect(host=db_config['host'], port=db_config['port'],
                                              user=db_config['user'], password=db_config['password'],
                                              database=db_config['database'])
    github_stats_db.autocommit = False
    cursor = github_stats_db.cursor()
    allTables={}
    indexList = indexTables.keys()
    for item in indexList:
        if item == "NEXT_ID":
            continue
        allTables["`Index__{0}s`".format(item)] = [["`{0}_ID`".format(item), '`'+item+'`']]
        for value in sorted(indexTables[item].keys()):
            allTables["`Index__{0}s`".format(item)].append([str(indexTables[item][value]), json.dumps(value, ensure_ascii=False).encode('utf8')])
    repoList = reposData.keys()
    trafficData=[["`Repo_ID`", "`Date_ID`", "`Clones`", "`Unique Cloners`", "`Views`", "`Unique Visitors`"]]
    referralData = [["`Repo_ID`", "`Date_ID`", "`Referral_ID`", "`Views`", "`Unique Visitors`"]]
    pathData = [["`Repo_ID`", "`Date_ID`", "`Path_ID`",
                "`Title_ID`", "`Views`", "`Unique Visitors`"]]

    maxdate = max(indexTables["Date"].keys())
    maxDateId = str(indexTables["Date"][maxdate])

    for repo in repoList:
        sql = 'Select DATE_FORMAT(MAX(date), "%Y-%m-%d") as Date from GitHub_Traffic where `Repo` = "{0}"'.format(repo)
        cursor.execute(sql)
        trafficList={}
        databaseTimeStamp = cursor.fetchone()[0]
        timestampList = []
        if databaseTimeStamp is None:
            minDate = min(indexTables["Date"].keys())
        else:
            for date_key in indexTables["Date"].keys():
                if date_key <= databaseTimeStamp:
                    continue
                timestampList.append(date_key)
            minDate = databaseTimeStamp
        for cloneData in GetList(reposData[repo]['clones'],'clones'):
            ts = str(cloneData['timestamp'][0:10])
            if ts <= minDate:
                continue
            timestampList.append(ts)
            trafficList[ts]={}
            trafficList[ts]["clones"] = cloneData['count']
            trafficList[ts]["unique cloners"] = cloneData['uniques']
        for viewData in GetList(reposData[repo]['traffic'], 'views'):
            ts = str(viewData['timestamp'][0:10])
            if ts <= minDate:
                continue
            timestampList.append(ts)
            if not (ts in trafficList):
                trafficList[ts] = {}
            trafficList[ts]["views"] = viewData['count']
            trafficList[ts]["unique visitors"] = viewData['uniques']
        timestampList = sorted(set(timestampList))

        # might not be able to read from the repo, so skip it.
        if 0 < len(timestampList):
            minDate = timestampList.pop(0)
            # this is taking advantage of two things, first the way strings are compared in
            # python, and second the format being used.  A better way may be to convert everything
            # to dates and back, but that's a lot of extra processing for minimal benefit
            
            for date in sorted(indexTables["Date"].keys()):
                if date < minDate:
                    continue
                row = [
                    str(indexTables["Repo"][repo]),
                    str(indexTables["Date"][date]),
                    GetTrafficValue(trafficList, date, "clones"),
                    GetTrafficValue(trafficList, date, "unique cloners"),
                    GetTrafficValue(trafficList, date, "views"),
                    GetTrafficValue(trafficList, date, "unique visitors")]

                trafficData.append(row)
        for pathResponse in GetList(reposData[repo]['paths']):
            pathData.append([
                str(indexTables["Repo"][repo]),
                maxDateId,
                str(indexTables["Path"][pathResponse['path']]),
                str(indexTables["Title"][pathResponse['title']]), 
                str(pathResponse['count']),
                str(pathResponse['uniques'])])
        for referralResponse in GetList(reposData[repo]['referrers']):
            referralData.append([
                str(indexTables["Repo"][repo]),
                maxDateId,
                str(indexTables["Referral"][referralResponse['referrer']]),
                str(referralResponse['count']),
                str(referralResponse['uniques'])])
    allTables["`Data__Paths`"]=pathData
    allTables["`Data__Traffic`"]=trafficData
    allTables["`Data__Referrals`"]=referralData
    cursor.close()
    github_stats_db.close()
    return allTables

def Commit(db_config, tables, dryrun):
    github_stats_db = mysql.connector.connect(host=db_config['host'], port=db_config['port'],
                                              user=db_config['user'], password=db_config['password'],
                                              database=db_config['database'])
    github_stats_db.autocommit = False
    
    github_stats_db.start_transaction()
    cursor = github_stats_db.cursor()
    cursor.execute("set names 'utf8';")
    for table_name in tables.keys():
        table = tables[table_name]
        values = []
        fields = ",".join(table.pop(0))
        for row in table:
            values.append("("+",".join(row)+")")
        if table_name.startswith("`Index"):
            ign="IGNORE "
        else:
            ign=" "
        sql = "INSERT {0} INTO {1} ({2}) VALUES {3};".format(ign, table_name, fields, ",\n".join(values))
        filename = ("cache/sql_"+table_name+".sql").replace('`', "").replace(' ',"_")
        with open(filename, "w+") as f:
            f.write('\ufeff')
            f.write(sql)
        cursor.execute(sql)
    if True == dryrun:
        print("# Dry run, rolling back sql statements (use --commit to add to the database)")
        github_stats_db.rollback()
    else:
        github_stats_db.commit()
        print("# Data committed")
    cursor.close()
    github_stats_db.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('username', help='Github username')
    parser.add_argument('-o', '--organization',
                        default='', help='Github organization')
    parser.add_argument('-s', '--skip_load',  dest='skip_load', action='store_true', default=False,
                        help="Skips pulling data from github and uses the cached data from the last pull")
    parser.add_argument('--commit',  dest='dryrun', action='store_false', default=True,
                        help="Commit the changes (default is dryrun)")
    # Database config input
    parser.add_argument('-hp', '--host',  default='localhost:3306',
                        help='Set database host and port [127.0.0.1:3306]', nargs='?')
    parser.add_argument('-usr', '--db-user', default='usr:""',
                        help='Set database user and password [usr:""]', nargs='?')
    parser.add_argument('-name', '--db-name',  default='',
                        help='Set database where data will be stored', nargs='?')
    args = parser.parse_args()
    """ Run main code logic
    :param username: string - GitHub username, or username:password pair
    :param repo: string - GitHub user's repo name or by default 'ALL' repos
    :param save_csv: string - Specify if CSV log should be saved
    :optional:
    param -hp, --host: string - Host and port to the database
    param -usr, --db-user: string - user and password to the database 
    param -name, --db-name: string - database name 
    param -o, --organization: string - GitHub organization (if different from username)
    """
    str = args.username.strip()
    sub = str.split(':', 1)
    len_sub = len(sub)

    username = sub[0].strip()
    if len_sub > 1:
        pw = sub[1].strip()
    else:
        pw = getpass.getpass('Password:')

    organization = username
    if args.organization != None:
        organization = args.organization.strip()

    auth_pair = (username, pw)
    # traffic_headers = {'Accept': 'application/vnd.github.spiderman-preview'}

    # database config info
    db_config = {'host': args.host.strip().split(":")[0],
                 'port': int(args.host.strip().split(":")[1]),
                 'user': args.db_user.strip().split(":")[0],
                 'password': args.db_user.strip().split(":")[1],
                 'database': args.db_name.strip()
                 }
    # By default iterate over all repositories
    repos = []
    repos_response = send_request('repos', organization, auth_pair)
    repos_json = repos_response[0]  # 1st element from requests.get()
    # print(repos_json.json())
    # 2nd element from requests.head()
    repos_links = repos_response[1].links
    # Error handling in case of {'documentation_url':'https://developer.github.com/v3','message':'Not Found'}
    try:
        err_msg = repos_json.json().get('message')
        print(err_msg)
        return 'Code done.'
    except AttributeError:
        print("Finding repos")
        # Add the repos from the first request
        if args.skip_load:
            with open('cache/repos.py', 'r') as f:
                repos = ast.literal_eval(f.read())
        else:
            for repo in repos_json.json():
                repos.append(repo['name'])
            while repos_links.get('next'):
                url = repos_links['next']['url']
                repos_response = send_request_pagination(url, auth_pair)
                for repo in repos_response[0].json():
                    repos.append(repo['name'])
                repos_links = repos_response[1].links
            with open('cache/repos.py', "w+") as f:
                f.write(repr(repos))
        # Iterate over collected repos list:
        # print(len(repos))  # commenting out the next 12 lines, correctly retrieves all org. repos
        repos_data={}
        repocnt=0
        repotlt=len(repos)
        skip_load = True
        if args.skip_load:
            with open('cache/repos_data.py', 'r') as f:
                repos_data = ast.literal_eval(f.read())
        else:
            for repo in repos:
                repocnt = repocnt + 1
                print "\rWorking on {0} of {1}".format(repocnt, repotlt),
                sys.stdout.flush()
                if ".github" == repo:
                    continue
                repos_data[repo]={}
                repos_data[repo]['traffic'] = send_request(
                    'traffic', organization, auth_pair, repo).json()
                repos_data[repo]['clones'] = send_request(
                    'clones', organization, auth_pair, repo).json()
                repos_data[repo]['referrers'] = send_request(
                    'referrers', organization, auth_pair, repo).json()
                repos_data[repo]['paths'] = send_request(
                    'paths', organization, auth_pair, repo).json()
            print("")
            with open('cache/repos_data.py', "w+") as f:
                f.write(repr(repos_data))
        print("Building index...")
        indexTables = BuildIndexTables(db_config, repos_data)
        print("Building data tables...")
        tables = BuildAllTables(db_config, repos_data, indexTables)
        print("Commiting data...")
        Commit(db_config, tables, args.dryrun)

if __name__ == '__main__':
    main()
