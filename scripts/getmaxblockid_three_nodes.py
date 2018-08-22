import requests
import sys
import os
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-type1', default='http')
parser.add_argument('-type2', default='http')
parser.add_argument('-type3', default='http')
parser.add_argument('-host1', default='localhost')
parser.add_argument('-host2', default='localhost')
parser.add_argument('-host3', default='localhost')
parser.add_argument('-port1', default='7079')
parser.add_argument('-port2', default='7018')
parser.add_argument('-port3', default='7082')
parser.add_argument('-interval', default='3')
args = parser.parse_args()

while True:
    api_point = "/api/v2/maxblockid"

    r1 = requests.get(args.type1 + "://" + args.host1 + ":" + args.port1 + api_point)
    r2 = requests.get(args.type2 + "://" + args.host2 + ":" + args.port2 + api_point)
    r3 = requests.get(args.type3 + "://" + args.host3 + ":" + args.port3 + api_point)

    answers = dict(r1=r1.json(),
                   r2=r2.json(),
                   r3=r3.json(),
                   )

    for ans in answers.values():
        print(ans)

    time.sleep(int(args.interval))

    if sys.platform == 'win32':
        os.system('cls')
    else:
        os.system('clear')
