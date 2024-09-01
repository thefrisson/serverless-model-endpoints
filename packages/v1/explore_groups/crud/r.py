from context.context import select_from_table, safe_getattr, row_to_dict

def list_solutions(user, user_type):
    if user_type in ['customer', 'admin', 'affiliate', 'system_admin', 'end_user']:
        try:
            table_name = f"{user_type}s_solutions"
            raw_list = select_from_table(table_name, user=user, user_type=user_type, return_type="all")
            solution_list = []
            print(raw_list)
            if not isinstance(raw_list, dict):
            
                for solution_link in raw_list:
                    print('solution: ', safe_getattr(solution_link, 'solution_id'))
                    solution = row_to_dict(select_from_table('solution', filters={'solution_id': safe_getattr(solution_link, 'solution_id')}, return_type="first_or_404"))
                    solution_list.append(solution)

            else:
                if raw_list['statusCode'] != 404:
                    return raw_list
                
            formatted_results = {'type': "solutions_list", 'data': solution_list, "statusCode": 200}
            # Ensure fetching results first
            return formatted_results
        except Exception as e:
            print("Listing Solutions failed:", str(e))
            return {"body": "Internal Server Error", "statusCode": 500}
    else:
        return {"body": "Unauthorized or invalid user type", "statusCode": 401}


def list_solution_template_explore_groups(user, user_type, object_user_type, filters=None):
    if (user_type == "system_admin" and object_user_type in ['customer', 'admin', 'affiliate', 'system', 'end_user']) or (user_type == "admin" and object_user_type in ['customer', 'admin', 'affiliate', 'end_user']) or (user_type == "customer" and object_user_type in ['customer', 'affiliate', 'end_user']) or (user_type == "affiliate" and object_user_type in ['affiliate', 'end_user']) or (user_type == "end_user" and object_user_type in ['end_user']):
        try:
            table_name = f"{object_user_type}_solution_template_explore_group"
            if filters is None:
                explore_groups = row_to_dict(select_from_table(table_name))
            else:
                explore_groups = row_to_dict(select_from_table(table_name, filters=filters))

            formatted_result = {'type': "explore_group_list", 'data': explore_groups, "statusCode": 200}
            # Ensure fetching results first
            return formatted_result
        except Exception as e:
            print("Retrieving failed:", str(e))
            return {"body": "Internal Server Error", "statusCode": 500}
    else:
        return {"body": "Unauthorized or invalid user type", "statusCode": 401}