from context.context import secured_user, path_to_list, is_valid_uuid
from crud.c import create_solution
from crud.r import list_solutions, retrieve_solution
from crud.u import update_solution
from crud.d import delete_solution


def main(event):
    method = event['http']['method']
    print(method)
    path_list = path_to_list(event['http']['path'])
    
    
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
            if len(path_list) > 0:
                public_id = path_list[0]
    
                endpoint = retrieve_solution(user, user_type, public_id=public_id)
                return {
                    "body": endpoint, 
                    "statusCode": endpoint['statusCode'], 
                    "headers": {
                        'Access-Control-Allow-Credentials': 'true',
                    }
                }
            else:
    
                endpoint = list_solutions(user, user_type)

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
            endpoint = create_solution(event, user, user_type)
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
        if not path_list or not is_valid_uuid(path_list[0]):
            return {
                'body': "Method requires id",
                "statusCode": 401, 
                "headers": {
                    'Access-Control-Allow-Credentials': 'true',
                }
            }

        public_id = path_list[0]
        user_type, user = secured_user(event)
        if not isinstance(user, dict):

            endpoint = update_solution(user, user_type)
            return {
                "body": endpoint, 
                "statusCode": endpoint['statusCode'], 
                "headers": {
                    'Access-Control-Allow-Credentials': 'true',
                }
            }
        
    elif method == "DELETE":
        if not path_list or not is_valid_uuid(path_list[0]):
            return {
                'body': "Method requires id",
                "statusCode": 401, 
                "headers": {
                    'Access-Control-Allow-Credentials': 'true',
                }
            }

        public_id = path_list[0]
        user_type, user = secured_user(event)
        if not isinstance(user, dict):

            endpoint = delete_solution(user, user_type)
            return {
                "body": endpoint, 
                "statusCode": endpoint['statusCode'], 
                "headers": {
                    'Access-Control-Allow-Credentials': 'true',
                    'Content-Type': "application/json"
                }
            }