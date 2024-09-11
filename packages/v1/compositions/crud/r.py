from context.context import select_from_table, safe_getattr, row_to_dict
from resources import valid_objects, composition_a, composition_b



def list_two_object_composition(user, user_type, object1, object2, object_user_type, filters=None):
    if (user_type == "system_admin" and object_user_type in ['customer', 'admin', 'affiliate', 'system', 'end_user']) or (user_type == "admin" and object_user_type in ['customer', 'admin', 'affiliate', 'end_user']) or (user_type == "customer" and object_user_type in ['customer', 'affiliate', 'end_user']) or (user_type == "affiliate" and object_user_type in ['affiliate', 'end_user']) or (user_type == "end_user" and object_user_type in ['end_user']):
        try:
            table_name = None
            if object1 in valid_objects and object2 in valid_objects:
                
                pre_table_name = f"{object1}_{object2}"

                if pre_table_name in composition_a:
                    table_name = f"{object_user_type}_{object1}_{object2}"
                elif pre_table_name in composition_b:
                    table_name = f"{object1}_{object_user_type}_{object2}"
            if table_name is not None:
                if filters is None:
                    compositions = row_to_dict(select_from_table(table_name))
                else:
                    compositions = row_to_dict(select_from_table(table_name, filters=filters))
                
                formatted_result = {'type': "composition", 'data': compositions, "statusCode": 200}
                # Ensure fetching results first
                return formatted_result
            
            else:
                return {'type': "error", 'error': "Not a Valid Object or similar error.", 'statusCode': 400}

            
        except Exception as e:
            print("Retrieving failed:", str(e))
            return {"body": "Internal Server Error", "statusCode": 500}
    else:
        return {"body": "Unauthorized or invalid user type", "statusCode": 401}