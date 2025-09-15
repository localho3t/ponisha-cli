

BASE_URL = "https://api.ponisha.ir/api/v1/"

def login_url():
    return BASE_URL+"auth/login"

def otp_url():
    return BASE_URL+"auth/otp/verification"