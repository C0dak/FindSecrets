#!/usr/bin/python3


import requests
import random
import argparse
import os
import sys
import re, fnmatch
import glob
import datetime, time
import shutil
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import colors


__AUTHOR__ = 'Gh0sTNiL'
__VERSION__ = 'v01.BETA'


## GLOBAL VARS
global agent
global dirname
dirname = ''
agent = ''
HEADERS = {"User-Agent": agent}


## REGEX PATTERNS
REGEX_PATTERN = {"Api": '/api\/[A-Za-z0-9\._+]*',
"AmazonEndPoint": 'https:\/\/[A-Za-z0-9\-.*]*.amazonaws.com/[A-Za-z0-9\-.*]*',
"AmazonEndPointHTTP": 'http:\/\/[A-Za-z0-9\-.*]*.amazonaws.com/[A-Za-z0-9\-.*]*',
"AcessKeyAws": "ACCESS_KEY_ID",
"accessKeyId": 'accessKeyId:([A-Za-z1-9]{0,30})',
"secretAccessKey": 'secretAccessKey:([A-Za-z1-9]{0,50})',
"SecretKeyAws": 'SECRET_KEY:([A-Za-z1-9]{0,50})',
"Graphql": '([A-Za-z0-9\._+])/graphql/([A-Za-z0-9\._+])',
"Authorization": "Authorization:\s[A-Za-z0-9]*\s[A-Za-z0-9]",
 "appToken": "appToken:\s([A-Za-z1-9]{0,50}",
 "apiWithSlash": '/api\/[A-Aa-z0-9]*\/[A-Aa-z0-9]*',
 "apiWithDot": '/api.[A-Za-z0-9\._+]*\/[A-Za-z0-9\._+]*\/[A-Za-z0-9\._+]*',
 "appKey":'appkey(\S[A-Za-z0-9]*)'}



def random_mobile_agent():
    lines = open('utils/mobile_agent.txt').read().splitlines()
    line = random.choice(lines)
    return line


def random_web_agent():
    lines = open('utils/web_agent.txt').read().splitlines()
    line = random.choice(lines)
    return line


def random_game_agent():
    lines = open('utils/game_consoles.txt').read().splitlines()
    line = random.choice(lines)
    return line




def banner():

    p = '''
    {}:{}

███████╗██╗███╗   ██╗██████╗ ███████╗███████╗ ██████╗██████╗ ███████╗████████╗███████╗
██╔════╝██║████╗  ██║██╔══██╗██╔════╝██╔════╝██╔════╝██╔══██╗██╔════╝╚══██╔══╝██╔════╝
█████╗  ██║██╔██╗ ██║██║  ██║███████╗█████╗  ██║     ██████╔╝█████╗     ██║   ███████╗
██╔══╝  ██║██║╚██╗██║██║  ██║╚════██║██╔══╝  ██║     ██╔══██╗██╔══╝     ██║   ╚════██║
██║     ██║██║ ╚████║██████╔╝███████║███████╗╚██████╗██║  ██║███████╗   ██║   ███████║
╚═╝     ╚═╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝


usage: find_secrets.py [-h] -u URL [--random_agent_web]
                       [--random_agent_mobile] [--random_agent_console]

Tool to find secrets on input domain

optional arguments:
  -h, --help            show this help message and exit
  -u URL, --url URL     [+] URL for crawler ex: https://domain.com
  --random_agent_web    Random user agents web
  --random_agent_mobile
                        Random user agents mobile
  --random_agent_console
                        Random user agents console
     '''
    return p.format(__AUTHOR__, __VERSION__)



def send_requests(url):


    print(colors.Color.OKBLUE + "\n\n[+] Random Agent set: {}\n".format(agent))
    print(colors.Color.END)


    try:
        r = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        if r.status_code != 404:
            print(colors.Color.OKGREEN + "[*] Crawler start!")
            print(colors.Color.END)
            crawler_js(r.text, url)


    except requests.exceptions.Timeout as e:
        print("[+] Timeout Error for {}".format(e))
        pass
    except requests.exceptions.MissingSchema as e:
        print("[+] Missing Schema https:// or http:// for {}".format(url))
        pass
    except requests.exceptions.TooManyRedirects as e:
        print("[+] Too many redirects found for {}".format(url))
        pass
    except requests.exceptions.RetryError as e:
        print("[+] Redirect Error for {}".format(url))



def parser_js_endpoints(src_tag, url):
    # return a domain from URL passed
    domain_path = urlparse(src_tag)


    if domain_path.netloc == '':
        return url + src_tag

    # if domain is different from the original domain
    elif domain_path.netloc != url:
        if src_tag[:2] == '//':
            new_src_tag = src_tag.replace('//', 'https://')
            return new_src_tag
        return src_tag
    else:
        return url + src_tag



def save_jsEnpoint_file(js_endpoint):

    parsed_endpoint_name_https = js_endpoint.replace('https://', '_')
    parsed_endpoint_name_slash = parsed_endpoint_name_https.replace('/','_')
    parsed_endpoint_name_txt = parsed_endpoint_name_slash.replace('.js', '.txt')

    ## parse URL when the length is higher than 150 to save with the name
    if len(parsed_endpoint_name_txt) > 150:
        parsed_endpoint_name_txt = parsed_endpoint_name_txt.split('?')[0]

    fullpath = os.path.join(dirname, parsed_endpoint_name_txt)


    try:
        r = requests.get(js_endpoint, headers=HEADERS, timeout=10, allow_redirects=True)
        if r.status_code != 404:
            with open(fullpath, 'wb') as f:
                f.write(r.content)
            f.close()

    except requests.exceptions.Timeout as e:
        print("[+] Timeout Error for {}".format(e))
        pass
    except requests.exceptions.MissingSchema as e:
        print("[+] Missing Schema https:// or http:// for {}".format(url))
        pass
    except requests.exceptions.TooManyRedirects as e:
        print("[+] Too many redirects found for {}".format(url))
        pass


def grab_patterns_from_js(regex_pattern_hash):
    #api = re.findall(regex_pattern_hash['Api'], text)
    #amazonaws = re.findall(regex_pattern_hash['AmazonEndPoint'], text)

    for filepath in glob.glob(os.path.join(dirname, '*.txt')):
        with open(filepath, errors='ignore') as f:
            content = f.read()
            # regex grabber
            api = re.findall(regex_pattern_hash['Api'], content)
            amazonaws = re.findall(regex_pattern_hash['AmazonEndPoint'], content)
            amazonawshttp = re.findall(regex_pattern_hash['AmazonEndPointHTTP'], content)
            AcessKeyAws = re.findall(regex_pattern_hash['AcessKeyAws'], content)
            SecretKeyAws = re.findall(regex_pattern_hash['SecretKeyAws'], content)
            Authorization = re.findall(regex_pattern_hash['Authorization'], content)
            apiWithSlash = re.findall(regex_pattern_hash['apiWithSlash'], content)
            apiWithDot = re.findall(regex_pattern_hash['apiWithDot'], content)
            appKey = re.findall(regex_pattern_hash['appKey'], content)
            Graphql = re.findall(regex_pattern_hash['Graphql'], content)
            secretAccessKey = re.findall(regex_pattern_hash['secretAccessKey'], content)
            accessKeyId = re.findall(regex_pattern_hash['accessKeyId'], content)




            if api:
                print(colors.Color.OKGREEN + f"[*]Found API end points on " + colors.Color.FAIL + f"{filepath}" + colors.Color.END + f"\n\n {api} \n\n")
                print(colors.Color.END)
            if amazonaws:
                print(colors.Color.OKGREEN + f"[*]Found AWS end points on " + colors.Color.FAIL + f"{filepath}" + colors.Color.END + f"\n\n {amazonaws} \n\n")
                print(colors.Color.END)
            if amazonawshttp:
                print(colors.Color.OKGREEN + f"[*]Found AWS end points on " + colors.Color.FAIL + f"{filepath}" + colors.Color.END + f"\n\n {amazonawshttp} \n\n")
                print(colors.Color.END)
            if AcessKeyAws:
                print(colors.Color.OKGREEN + f"[*]Found AcessKeyAws end points on " + colors.Color.FAIL + f"{filepath}" + colors.Color.END + f"\n\n {AcessKeyAws} \n\n")
                print(colors.Color.END)
            if SecretKeyAws:
                print(colors.Color.OKGREEN + "[*] Possible secret key found on")
                print(colors.Color.END)
            if Authorization:
                print(colors.Color.OKGREEN + "[*] Possible authorization key found on")
                print(colors.Color.END)
            if apiWithSlash:
                print(colors.Color.OKGREEN + f"[*]Found apiWithSlash end points on " + colors.Color.FAIL + f"{filepath}" + colors.Color.END + f"\n\n {apiWithSlash} \n\n")
                print(colors.Color.END)
            if apiWithDot:
                print(colors.Color.OKGREEN + f"[*]Found apiWithDot end points on " + colors.Color.FAIL + f"{filepath}" + colors.Color.END + f"\n\n {apiWithDot} \n\n")
                print(colors.Color.END)
            if appKey:
                print(colors.Color.OKGREEN + f"[*]Found appKey end points on " + colors.Color.FAIL + f"{filepath}" + colors.Color.END + f"\n\n {[m for m in appKey]} \n\n")
                print(colors.Color.END)
            if Graphql:
                print(colors.Color.OKGREEN + f"[*]Found Graphql end points on " + colors.Color.FAIL + f"{filepath}" + colors.Color.END + f"\n\n {m for m in Graphql} \n\n")
                print(colors.Color.END)
            if secretAccessKey:
                print(colors.Color.OKGREEN + f"[*]Found secretAccessKey end points on " + colors.Color.FAIL + f"{filepath}" + colors.Color.END + f"\n\n {secretAccessKey} \n\n")
                print(colors.Color.END)
            if accessKeyId:
                print(colors.Color.OKGREEN + f"[*]Found accessKeyId end points on " + colors.Color.FAIL + f"{filepath}" + colors.Color.END + f"\n\n {accessKeyId} \n\n")
                print(colors.Color.END)




def crawler_js(requests_objt, url):

    soup = BeautifulSoup(requests_objt, 'html.parser')
    src_tags_list = []

    # verify if scripts tags with were found
    if len(soup.find_all('script')) == 0:
        print(colors.Color.FAIL + "[-] No scripts founded on this page {} \n or maybe a bug please open a issue".format(url))

    for script_tag in soup.find_all('script'):
        if script_tag:
            src_tags_list.append(script_tag.get('src'))

    # Remove None elements from list scripts
    filter_src_tag_list = [ src_js for src_js in src_tags_list if src_js is not None]

    # Concat js with domain crawled
    print(colors.Color.OKGREEN + "[*] Scripts were founded")
    print(colors.Color.END)
    for endpoint_js in filter_src_tag_list:
        parsed_endpoint = parser_js_endpoints(endpoint_js, url)
        print(parsed_endpoint)
        save_jsEnpoint_file(parsed_endpoint)

    print(colors.Color.OKGREEN + "\n\n[*] Crawler end, total scripts founded! {}".format(len(filter_src_tag_list)))
    print(colors.Color.OKGREEN + "[*] All scripts were saved on dir called {} !".format(dirname))
    print(colors.Color.END)




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Tool to find secrets on input domai')
    parser.add_argument('-u', '--url', type=str, required=True, help="[+] URL for crawler")
    parser.add_argument('--random_agent_web',help="Random user agents web", action='store_true')
    parser.add_argument('--random_agent_mobile', help="Random user agents mobile", action='store_true')
    parser.add_argument('--random_agent_console', help="Random user agents console", action='store_true')
    args = parser.parse_args()
    url = args.url
    web_user_agent = args.random_agent_web
    mobile_user_agent = args.random_agent_mobile
    console_user_agent = args.random_agent_console

    if 'http://' not in url and 'https://' not in url:
        print("[-] Provide a schema http:// or https:// for {}".format(url))
        sys.exit()

    print(banner())
    # create a dir with name of target name
    dirname = urlparse(url).netloc
    try:
        os.mkdir(dirname)
        print(colors.Color.OKBLUE + "[*] Created a DIR with name {}".format(dirname))
        print(colors.Color.END)
    except FileExistsError as e:
        print(colors.Color.FAIL + "[-] File Exists {} Would u like to overwrite {} y/n".format(dirname,dirname))
        print(colors.Color.END)
        c = input()
        if len(c) == 1 and c.lower() == 'y':
            shutil.rmtree(dirname)
            os.mkdir(dirname)
        else:
            print(colors.Color.FAIL + "[*] Delete manually and try again ;)")
            print(colors.Color.END)
            sys.exit()


    if console_user_agent:
        agent = random_game_agent()
    if mobile_user_agent:
        agent = random_mobile_agent()
    if web_user_agent:
        agent = random_web_agent()

    if agent == '':
            agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0'

    send_requests(url)
    grab_patterns_from_js(REGEX_PATTERN)
