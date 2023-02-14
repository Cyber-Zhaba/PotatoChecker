import time
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


def availability_checker(url):
    req = Request(url)
    answer = []
    try:
        flag = True
        for counter in range(5):
            response = urlopen(req)
            if counter >= 3:
                answer.append("The site is loading to slow")
            if response:
                answer.append("Website is working fine")
                flag = False
                break
            time.sleep(7)
        if flag:
            answer.append("Couldn't load website")
    except HTTPError as err:
        answer.append('The server couldn\'t fulfill the request.')
        answer.append(f'Error code: {err.code}')
    except URLError as err:
        answer.append('We failed to reach a server.')
        answer.append(f'Reason: {err.reason}')
    return answer


if __name__ == '__main__':
    print(availability_checker('https://aboba.io'))