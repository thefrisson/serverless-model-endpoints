from context.context import select_from_table, safe_getattr, row_to_dict
from scopes.scope import get_scoping_object
from resources.resources import valid_objects, objects_a, objects_b, context_map


def list_objects(user, user_type, obj, object_user_type, filters=None):
    if (user_type == "system_admin" and object_user_type in ['customer', 'admin', 'affiliate', 'system', 'end_user']) or (user_type == "admin" and object_user_type in ['customer', 'admin', 'affiliate', 'end_user']) or (user_type == "customer" and object_user_type in ['customer', 'affiliate', 'end_user']) or (user_type == "affiliate" and object_user_type in ['affiliate', 'end_user']) or (user_type == "end_user" and object_user_type in ['end_user']):
        try:
            table_name = None
            if obj in valid_objects:
                
                pre_table_name = obj[:-1] if obj.endswith('s') else obj

                if pre_table_name in objects_a:
                    table_name = f"{object_user_type}_{obj}"
                    if filters is None:
                        objects = row_to_dict(select_from_table(table_name))
                    else:
                        objects = row_to_dict(select_from_table(table_name, filters=filters))
                    
                    formatted_result = {'type': obj, 'data': objects, "statusCode": 200}
                    # Ensure fetching results first
                    return formatted_result

                
                elif pre_table_name in objects_b:
                    print("objects_b")
                    if filters is None:
                        filters = {}
                    scopes_list = get_scoping_object(user, user_type, context_map[obj][object_user_type]['scope_objects'][user_type]['tablename'])
                    objects = []
                    for scope_object in scopes_list:
                        if context_map[obj][object_user_type]['scope_objects'][user_type]['output'] in scope_object.keys():
                            table_name = context_map[obj][object_user_type]['tablename']

                            object_iter = row_to_dict(select_from_table(table_name, filters=filters))
                            objects.append(object_iter)
                        
                        if table_name is not None:
                            formatted_result = {'type': obj, 'data': objects, "statusCode": 200}
                            # Ensure fetching results first
                            return formatted_result
                        else:
                            return {'type': "error", 'error': "Not a Valid Object or similar error for tembo object.", 'statusCode': 400}
                else:
                    return {'type': "error", 'error': "Not a 3.", 'statusCode': 400}
            else:
                return {'type': "error", 'error': "Not a.", 'statusCode': 400}

        except Exception as e:
            print("Retrieving failed:", str(e))
            return {"body": "Internal Server Error", "statusCode": 500}
    else:
        return {"body": "Unauthorized or invalid user type", "statusCode": 401}