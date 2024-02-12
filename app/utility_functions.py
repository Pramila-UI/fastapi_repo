import hashlib
import jwt
from datetime import datetime ,timedelta 
from fastapi import Request
from fastapi.exceptions import HTTPException
from functools import wraps


def generate_password_hash(password):
    """ Hash the password using SHA-256 """
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    return password_hash


def checking_hashed_password(input_password , stored_hash_password) :
    """ genrating the hashed for the input """
    input_hash = generate_password_hash(input_password)
    if input_hash == stored_hash_password:
        return True
    else:
        return False
    

def generate_access_token(payload):
    encoded_data = jwt.encode(
        payload = payload ,
        key = "testing" ,
        algorithm = "HS256"
    )
    return encoded_data


def decrypted_token(token):
    decoded_data = jwt.decode(
        jwt =  token ,
        key   = "testing" ,
        algorithms = ["HS256"]
    )

    return decoded_data
    

def generating_payload(user_id , is_staff):
    payload = {
        "id": user_id,
        "is_staff": is_staff
        # "exp": datetime.utcnow() + timedelta(days=20)  # Token expiration time
        # "iat": datetime.utcnow()  # Token issued at time
    }

    return payload

def authenticate_user(func):
    @wraps(func)
    async def wrapper(*args ,**kwargs):
        request =  kwargs['request']
        headers = request.headers
        token = headers.get('Authorization')

        if not token:
            raise HTTPException(status_code=401, detail="Token is missing in headers")
        
        # Perform authentication check
        try:
            decoded_token = decrypted_token(token=token)
        except Exception as e:
            raise HTTPException(detail=f"{e}")
        
        if decoded_token['is_staff']:
            raise HTTPException(status_code=401, detail="Invalid User")
        
        return await func(*args ,**kwargs)
    
    return wrapper


def authenticate_staff_user(func):
    @wraps(func)
    async def wrapper(*args ,**kwargs):
        request =  kwargs['request']
        headers = request.headers
        token = headers.get('Authorization')

        if not token:
            raise HTTPException(status_code=401, detail="Token is missing in headers")
        
        # Perform authentication check
        decoded_token = decrypted_token(token=token)

        if not decoded_token['is_staff']:
            raise HTTPException(status_code=401, detail="Invalid User")
        
        return await func(*args ,**kwargs)
    
    return wrapper