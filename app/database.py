from sqlalchemy import create_engine , text
from urllib.parse import quote_plus

username = "postgres"
password = "root1234"
endpoint = "testingdbinstance.clescgcoec5z.ap-south-1.rds.amazonaws.com:5432"
db_name = "testing"

engine_connect = create_engine(f"postgresql://{username}:{quote_plus(password)}@{endpoint}/{db_name}") 
