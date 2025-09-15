import os
from Apps.login import Login
from Apps.Profile import Profile
def main():
    if not os.path.exists(".env"):
        os.makedirs("sessions")
        lg = Login()
        client_number = input("Enter Phone Number : ")
        lg.set_user_number(client_number)
        lg.execute_login_l1()
        client_otp = input("Enter Phone OTP : ")
        lg.set_otp_user(client_otp)
        lg.execute_login_l2()

    else:
        pf = Profile()
        pf.request()
        pf.request_me()




if __name__  == "__main__":
    main()