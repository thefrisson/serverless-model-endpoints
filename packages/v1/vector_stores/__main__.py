from context.context import secured_user
from crud.c import create_vector_store
from crud.r import list_vector_stores, retrieve_vector_store
from crud.u import update_vector_store
from crud.d import delete_vector_store




def main(event):

    method = event['http']['method']
    print(method)
    
    if method == "OPTIONS":
        print("options request")
        return { 
            "statusCode": 200, 
            "headers": {
                'Access-Control-Allow-Credentials': 'true',
            }
        }
    
    if method == "GET":
        user_type, user = secured_user(event)
        if not isinstance(user, dict):
            if 'id' in event:
                public_id = event['id']
                assistant_type = event.get('assistant', user_type if user_type != "system_admin" else "system")
                endpoint = retrieve_vector_store(user, user_type, assistant_type, public_id=public_id)
                return {
                    "body": endpoint, 
                    "statusCode": endpoint['statusCode'], 
                    "headers": {
                        'Access-Control-Allow-Credentials': 'true',
                    }
                }
            else:
                assistant_type = event.get('assistant', user_type if user_type != "system_admin" else "system")
                endpoint = list_vector_stores(user, user_type, assistant_type)

                return {
                    "body": endpoint, 
                    "statusCode": endpoint['statusCode'], 
                    "headers": {
                        'Access-Control-Allow-Credentials': 'true',
                    }
                }
        
        else:
            endpoint = user
            return {
                "body": endpoint, 
                "statusCode": endpoint['statusCode'], 
                "headers": {
                    'Access-Control-Allow-Credentials': 'true',
                }
            }
    elif method == "POST":
        user_type, user = secured_user(event)
        if not isinstance(user, dict):
            assistant_type = event.get('assistant', user_type if user_type != "system_admin" else "system")
            print("assistant ", assistant_type)
            endpoint = create_vector_store(event, user, user_type, assistant_type)
            
        else:
            return {
                "body": {"error": "Unauthorized access or invalid user type"},
                "statusCode": 403,
                "headers": {
                    'Access-Control-Allow-Credentials': 'true',
                }
            }
        
    elif method == "PUT":
        public_id = event.get('id', None)
        if public_id is None:
            return {
                'body': "Method requires id",
                "statusCode": 401, 
                "headers": {
                    'Access-Control-Allow-Credentials': 'true',
                }
            }
        
        user_type, user = secured_user(event)
        if not isinstance(user, dict):
            assistant_type = event.get('assistant', user_type if user_type != "system_admin" else "system")
            endpoint = update_vector_store(user, user_type)
            return {
                "body": endpoint, 
                "statusCode": endpoint['statusCode'], 
                "headers": {
                    'Access-Control-Allow-Credentials': 'true',
                }
            }
        
    elif method == "DELETE":
        public_id = event.get('id', None)
        if public_id is None:
            return {
                'body': "Method requires id",
                "statusCode": 401, 
                "headers": {
                    'Access-Control-Allow-Credentials': 'true',
                }
            }
        
        user_type, user = secured_user(event)
        if not isinstance(user, dict):
            assistant_type = event.get('assistant', user_type if user_type != "system_admin" else "system")
            endpoint = delete_vector_store(user, user_type)
            return {
                "body": endpoint, 
                "statusCode": endpoint['statusCode'], 
                "headers": {
                    'Access-Control-Allow-Credentials': 'true',
                    'Content-Type': "application/json"
                }
            }