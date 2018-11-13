import requests
import sys
import os
import time


def getmaxblockid_three_nodes(request):
    while True:
        api_point = '/api/v2/maxblockid'

        r1 = requests.get(request.config.getoption('--type1') + '://' + request.config.getoption('--httpHost1') + ':' +
                          request.config.getoption('--httpPort1') + api_point)
        r2 = requests.get(request.config.getoption('--type2') + '://' + request.config.getoption('--httpHost2') + ':' +
                          request.config.getoption('--httpPort2') + api_point)
        r3 = requests.get(request.config.getoption('--type3') + '://' + request.config.getoption('--httpHost3') + ':' +
                          request.config.getoption('--httpPort3') + api_point)

        answers = dict(r1=r1.json(),
                       r2=r2.json(),
                       r3=r3.json(),
                       )

        for ans in answers.values():
            print(ans)

        time.sleep(int(request.config.getoption('--timeout')))

        if sys.platform == 'win32':
            os.system('cls')
        else:
            os.system('clear')
