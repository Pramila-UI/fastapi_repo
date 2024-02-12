from fastapi import APIRouter , status , Response 
from fastapi.encoders import jsonable_encoder
from .schemas import SignUpModel , LoginModel
from .database import engine_connect
from sqlalchemy import text
 
from .utility_functions import generate_password_hash , generating_payload , generate_access_token , checking_hashed_password
from fastapi.exceptions import HTTPException
from datetime import   date

auth_router = APIRouter(
    prefix='/auth',
    tags= ["auth"]
)


@auth_router.post('/signup' , status_code=201)
async def SignUp(data : SignUpModel , response : Response):
    try:
        with engine_connect.connect() as conn:
            sql = f"select * from users where email like '%{data.email}%' "
            existing_email = conn.execute(text(sql)).fetchone()
            
        if existing_email is not None:
            response.status_code =  status.HTTP_400_BAD_REQUEST
            return HTTPException(status_code = status.HTTP_400_BAD_REQUEST , detail=f"User with the {data.email} already exists")

        with engine_connect.connect() as conn:
            sql = f"select * from users where username like '%{data.username}%' "
            existing_username = conn.execute(text(sql)).fetchone()
            
        if existing_username is not None:
            response.status_code =  status.HTTP_400_BAD_REQUEST
            return HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail=f"User with the {data.username} already exists")

        """ create the user """
        password = generate_password_hash(data.password)
        sql = f'INSERT INTO users ("username" , "email", "password" , "is_active" ,"is_staff" , "created_date")  VALUES ' \
              f" ('{data.username}' , '{data.email}' , '{password}' , {data.is_active} , {data.is_staff} , '{date.today()}') " 
        
        with engine_connect.connect() as conn:
            conn.execute(text(sql))
            conn.commit()

            return jsonable_encoder({
                "status" :"success" ,
                "message" : "User Created successfully"
            })

    except Exception as e:
        return {
            "status"  : "failure" ,
            "message" : f"Exception while adding the new user : {e}"
        } , status.HTTP_400_BAD_REQUEST
    

@auth_router.post('/login')
async def login(data : LoginModel , response : Response):
    try:
        """Check the user is exist in the database or not . if not display the error message else create the jwt token and send the token and the user info"""
        username = data.username
        email = data.email
        input_password = data.password

        if (username == None or username == '') and (email == None or email == ''):
            response.status_code = status.HTTP_400_BAD_REQUEST 
            return HTTPException(status_code = status.HTTP_400_BAD_REQUEST , detail = "username or email are mandatory!!!")
        
        if (input_password == None and input_password == ''):
            response.status_code = status.HTTP_400_BAD_REQUEST 
            return HTTPException(status_code = status.HTTP_400_BAD_REQUEST , detail = "Provide valid password")

        if (email is not None and  email != ''): 
            with engine_connect.connect() as conn:
                sql = f"select * from users where email = '{email}' "
                existing_user = conn.execute(text(sql)).fetchone()
        else:
            with engine_connect.connect() as conn:
                sql = f"select * from users where username = '{username}' "
                existing_user = conn.execute(text(sql)).fetchone()
        
        if existing_user is not None:
            """ checking the password is incorrect or not """
            password = existing_user.password

            checking_password = checking_hashed_password(input_password , password)
            if not checking_password:
                response.status_code = status.HTTP_400_BAD_REQUEST 
                return HTTPException(status_code = status.HTTP_400_BAD_REQUEST , detail = "Incorrect password") 

            """ create the jwt token and sent the data into the client """
            genrate_payload = generating_payload( existing_user.id  , existing_user.is_staff )
            token = generate_access_token(genrate_payload)

            user_data = {
                "id" : existing_user.id ,
                "username" : existing_user.username,
                "email" : existing_user.email ,
                "is_active" : existing_user.is_active  , 
                "is_staff" : existing_user.is_staff ,
            }

            return jsonable_encoder({
                                "status" : "success" ,
                                "data"  : user_data ,
                                "token" : token 
                            })

        else:
            response.status_code = status.HTTP_404_NOT_FOUND
            return jsonable_encoder({
                    "status" : 'failure',
                    "message" : "User not found"
            })

    except Exception as e:
        return {
            "status"  : "failure" ,
            "message" : f"Exception while log-In : {e}"
        } , status.HTTP_400_BAD_REQUEST
    