from fastapi import APIRouter , Depends  , status , Response , Request
from fastapi.encoders import jsonable_encoder
from .utility_functions import authenticate_user , authenticate_staff_user
from .database  import engine_connect
from sqlalchemy import text
from .schemas import OrderModel , OrderUpdateModel
from datetime import   date
from fastapi.exceptions import HTTPException


orders_router = APIRouter(
    prefix='/orders',
    tags= ["orders"]
)


@orders_router.get('/all_orders')
@authenticate_staff_user
async def get_all_order_details(request: Request) :
    try:
        with engine_connect.connect() as conn:
            sql = f"select * from orders order by id desc "
            result = conn.execute(text(sql)).fetchall()

            order_list  = []
            for item in result:
                order_dict = {}
                order_dict['order_id'] = item[0]
                order_dict['order_quantity'] = item[1]
                order_dict['order_status'] = item[2]
                order_dict['pizza_size'] = item[3]
                order_dict['user_id'] = item[4]
                order_list.append(order_dict)

            return jsonable_encoder({
                    "status" : "success" ,
                    "data"  : order_list 
            })
       
    except Exception as e:
         return {
            "status"  : "failure" ,
            "message" : f"Exception while fetching the orders list: {e}"
        } , status.HTTP_400_BAD_REQUEST



@orders_router.get('/order_by_id/{order_id}')
async def get_particular_order_by_id(order_id : int , response : Response):
    try:
        with engine_connect.connect() as conn:
            sql = f"select * from orders where id = {order_id}"
            result = conn.execute(text(sql)).fetchone()

            if result is not None:
                order_data = {
                    "order_id" : result[0] ,
                    "order_quantity" : result[1] ,
                    "order_status" : result[2] ,
                    "pizza_size" : result[3] ,
                    "user_id" : result[4] ,
                }

                return jsonable_encoder({
                        "status" : "success" ,
                        "data"  : order_data 
                })
        
            else:
                response.status_code = status.HTTP_404_NOT_FOUND
                return HTTPException(status_code= status.HTTP_404_NOT_FOUND , detail="No order found")
       
    except Exception as e:
         return {
            "status"  : "failure" ,
            "message" : f"Exception while fetching the particular order: {e}"
        } , status.HTTP_400_BAD_REQUEST


@orders_router.get('/order_by_useres/{user_id}')
async def get_particular_order_by_id(user_id : int , response : Response):
    try:
        with engine_connect.connect() as conn:
            sql = f"select * from user where id = {user_id}"
            result = conn.execute(text(sql)).fetchone()

            if result is None:
                response.status_code = status.HTTP_404_NOT_FOUND
                return HTTPException(status_code= status.HTTP_404_NOT_FOUND , detail="No User found for the provided id")

       
        with engine_connect.connect() as conn:
            sql = f"select * from orders where user_id = {user_id}"
            result = conn.execute(text(sql)).fetchall()

            order_list  = []
            if len(result) > 0 :
                for item in result:
                    order_dict = {}
                    order_dict['order_id'] = item[0]
                    order_dict['order_quantity'] = item[1]
                    order_dict['order_status'] = item[2]
                    order_dict['pizza_size'] = item[3]
                    order_dict['user_id'] = item[4]
                    order_list.append(order_dict)

            return jsonable_encoder({
                    "status" : "success" ,
                    "data"  : order_list 
            })
            

    except Exception as e:
        return {
            "status"  : "failure" ,
            "message" : f"Exception while fetching the order of the particular users: {e}"
        } , status.HTTP_400_BAD_REQUEST



@orders_router.post('/add_order' , status_code=201)
@authenticate_user
async def order_pizza(request: Request , order_data : OrderModel):
    try:
        quantity =  order_data.quantity
        order_status  =  order_data.order_status
        pizza_size = order_data.pizza_size
        user_id = order_data.user_id


        with engine_connect.connect() as conn:
            sql = 'INSERT INTO orders ("quantity" , "order_status" , "pizza_size" , "user_id" , "created_date") VALUES ' \
                    f"({quantity} , '{order_status}' , '{pizza_size}' , {user_id} , '{date.today()}')"
            conn.execute(text(sql))
            conn.commit()

            return jsonable_encoder({
                    "status" : "success" ,
                    "message"  : "Order placed successfully"
            })
       
    except Exception as e:
        return {
            "status"  : "failure" ,
            "message" : f"Exception while fetching placing an order : {e}"
        } , status.HTTP_400_BAD_REQUEST


@orders_router.post('/update_order/{order_id}')
@authenticate_user
async def update_order_details(order_id : int , order_data : OrderUpdateModel,response : Response ,request: Request):
    try:
        with engine_connect.connect() as conn:
            sql = f"select  order_status  from orders where id = {order_id}"
            result = conn.execute(text(sql)).fetchone()

            if (result is not None):
                if result[0] == "PENDING" :
                    """ update the details """
                    sql = f"update orders set quantity = {order_data.quantity} , pizza_size = '{order_data.pizza_size}' where id = {order_id}"
                    conn.execute(text(sql))
                    conn.commit()

                    return jsonable_encoder({
                            "status" : "success" ,
                            "message"  : "Order updated successfullly" 
                    })
                
                else:
                    return HTTPException(status_code= status.HTTP_400_BAD_REQUEST , detail="Could not update the order")
        
            else:
                response.status_code = status.HTTP_404_NOT_FOUND
                return HTTPException(status_code= status.HTTP_404_NOT_FOUND , detail="No order found")
       
    except Exception as e:
         return {
            "status"  : "failure" ,
            "message" : f"Exception while fetching the particular order: {e}"
        } , status.HTTP_400_BAD_REQUEST
    

@orders_router.post('/update_order_status/{order_id}')
@authenticate_staff_user
async def update_order_status(order_id : int , order_status : str , response : Response , request: Request):
    try:
        with engine_connect.connect() as conn:
            sql = f"select  order_status  from orders where id = {order_id}"
            result = conn.execute(text(sql)).fetchone()

            if (result is not None):
                """ update the details """
                sql = f"update orders set order_status = '{order_status}' where id = {order_id}"
                conn.execute(text(sql))
                conn.commit()

                return {
                        "status" : "success" ,
                        "message"  : "Order updated successfullly" 
                    }
        
            else:
                response.status_code = status.HTTP_404_NOT_FOUND
                return HTTPException(status_code= status.HTTP_404_NOT_FOUND , detail="No order found")
       
    except Exception as e:
         return {
            "status"  : "failure" ,
            "message" : f"Exception while fetching the particular order: {e}"
        } , status.HTTP_400_BAD_REQUEST