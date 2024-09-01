import json
from context.context import secured_user, path_to_list, is_valid_uuid
from crud.c import create_solution_template_explore_groups
from crud.r import list_solutions, list_solution_template_explore_groups
from crud.u import update_solution
from crud.d import delete_solution


def main(event):
    method = event['http']['method']
    print(method)

    path_list = path_to_list(event['http']['path'])
    print('path list: ', path_list)

    is_valid_request = False
    
    group_type = None
    object_user_type = None
    public_id = None

    group_type = path_list[0]
    if group_type in ['solution_templates', 'external_account_types']:
        object_user_type = path_list[1]
        if object_user_type in ['system', 'admin', 'customer']:
            is_valid_request = True

            if len(path_list) == 3:
                public_id = path_list[2]


        
    print("Valid Request: ", is_valid_request)
    if not is_valid_request:
        return {
            "statusCode": 400,
            "headers": {
                'Access-Control-Allow-Credentials': 'true'
            },
            "body": {'error': "Invalid Request"}
        }
    else:
        if group_type == "solution_templates":
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
                    filters = None
                    if 'filters' in event.keys() and isinstance(event['filters'], dict):
                        filters = event['filters']
                        print("filters found")
                    if public_id is None:
                        endpoint = list_solution_template_explore_groups(user, user_type, object_user_type, filters=filters)
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
                    print()
                    body_str = event.get('body', "{}")
                    body_dict = json.loads(body_str)
                    
                    endpoint = create_solution_template_explore_groups(user, user_type, object_user_type, body_dict)
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