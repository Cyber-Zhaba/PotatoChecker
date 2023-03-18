import sys
sys.path.insert(0, f'{sys.path[2]}/scripts')
print(sys.path[0])
from availability_checker import ping_website
from my_email import send_email
from utilities import status