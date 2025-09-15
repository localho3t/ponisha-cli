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
        rand_num = str(random.randint(10**12, 10**13 - 1))
        self.filename = f"{now}_{rand_num}.sessionProfile"


    def request(self):
        r = requests.get(urls['profile'],headers=get_header("profile",self.token))
        # print(r.json())
        data = json.dumps(r.json(), ensure_ascii=False)
        if r.status_code == 200:
            f = open(f"./sessions/{self.filename}",'w+')
            f.writelines(data)
            f.close()
        else:
            print(r.status_code)

    
    def get_filename(self):
        return self.filename
