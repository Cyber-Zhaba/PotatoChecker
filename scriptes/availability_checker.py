import time
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


def availability_checker(url):
    req = Request(url)
    answer = []
    try:
        for counter in range(5):
            response = urlopen(req)
            time.sleep(7)
            if counter >= 3:
                answer.append("The site is loading to slow")
            if response:
                answer.append("Website is working fine")
        answer.append("Couldn't load website")
    except HTTPError as err:
        answer.append('The server couldn\'t fulfill the request.')
        answer.append(f'Error code: {err.code}')
    except URLError as err:
        answer.append('We failed to reach a server.')
        answer.append(f'Reason: {err.reason}')
    else:
        answer.append('Website is working fine')
    return answer
