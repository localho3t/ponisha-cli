from header import *
from Urls import *
import requests
class Login:
    def __init__(self):
        self.url = login_url()
        self.otp_url = otp_url()
        self.header = get_header("login")


    def __login_with_otp(self):
        r = requests.post(self.otp_url,headers=self.header,json=self.data)
        if r.status_code == 200:
            content = r.json()
            
            f = open(".env",'w+')
            f.writelines(f"user_id={content['data']['user_id']}\n")
            f.writelines(f"username={content['data']['username']}\n")
            f.writelines(f"token={content['data']['token']}\n")
            f.writelines(f"token_type={content['data']['token_type']}\n")
            f.writelines(f"token_expired_at={content['data']['token_expired_at']}\n")
            f.close()


    def __login_send_code(self):
        requests.post(self.url,headers=self.header,json=self.data)




    def set_otp_user(self,otp:str):
        self.data = {"mobile": self.number, "otp": otp}


    def set_user_number(self,number:str):
        self.number = number
        self.data = {
            "mobile":number
        }
    
    def execute_login_l1(self):
        self.__login_send_code()
    
    def execute_login_l2(self):
        self.__login_with_otp()

        