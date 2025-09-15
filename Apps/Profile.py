from dotenv import load_dotenv
import os
from Urls import urls
import requests
from header import get_header
import datetime
import random
import json
load_dotenv()

class Profile:
    def __init__(self):
        self.token = os.getenv('token')
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        self.filename = f"{now}_{str(random.randint(10**12, 10**13 - 1))}.sessionProfile"
        self.mefilename = f"{now}_{str(random.randint(10**12, 10**13 - 1))}.sessionMe"


    def request(self):
        r = requests.get(urls['profile'],headers=get_header("with_token",self.token))
        data = json.dumps(r.json(), ensure_ascii=False)
        if r.status_code == 200:
            f = open(f"./sessions/{self.filename}",'w+')
            f.writelines(data)
            f.close()
        else:
            print(r.status_code)

    def request_me(self):
        r = requests.get(urls['me'],headers=get_header("with_token",self.token))
        data = json.dumps(r.json(), ensure_ascii=False)
        if r.status_code == 200:
            f = open(f"./sessions/{self.mefilename}",'w+')
            f.writelines(data)
            f.close()
        else:
            print(r.status_code)

    
    def get_filename(self):
        return self.filename
    
    def get_mefilename(self):
        return self.mefilename
