from context.context import secured_user
from crud.c import create_solution
from crud.r import list_solutions, retrieve_solution
from crud.u import update_solution
from crud.d import delete_solution


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
                endpoint = retrieve_solution(user, user_type, assistant_type, public_id=public_id)
                return {
                    "body": endpoint, 
                    "statusCode": endpoint['statusCode'], 
                    "headers": {
                        'Access-Control-Allow-Credentials': 'true',
                    }
                }
            else:
                assistant_type = event.get('assistant', user_type if user_type != "system_admin" else "system")
                endpoint = list_solutions(user, user_type, assistant_type)

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
            endpoint = create_solution(event, user, user_type, assistant_type)
            return {
                "body": endpoint, 
                "statusCode": endpoint['statusCode'], 
                "headers": {
                    'Access-Control-Allow-Credentials': 'true',
                }
            }
            
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
            endpoint = update_solution(user, user_type)
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
            endpoint = delete_solution(user, user_type)
            return {
                "body": endpoint, 
                "statusCode": endpoint['statusCode'], 
                "headers": {
                    'Access-Control-Allow-Credentials': 'true',
                    'Content-Type': "application/json"
                }
            }