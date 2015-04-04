from datetime import datetime
from django.utils import timezone

import re
def parse_date(date_str):
    # in the form of 2015-01-01
    if '-' in date_str:
        try:
            to_return = datetime.strptime(date_str, '%y-%m-%d')
        except:
            return None
    # in the form of 
    else:
        try:

            to_return = datetime.strptime(date_str, '%y%m%d')
        except:
            print "wrong"
            return None
    return to_return

pattern = re.compile(r".*")

if __name__ == '__main__':
    # print re.match(pattern, "adf,adsf")
    
