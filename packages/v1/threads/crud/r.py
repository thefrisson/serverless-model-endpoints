from context.context import select_from_table

def list_threads(user, user_type, assistant_type):
    if user_type in ['customer', 'admin', 'affiliate', 'system_admin', 'end_user']:
        if (user_type == "system_admin" and assistant_type in ['customer', 'admin', 'affiliate', 'system', 'end_user']) or (user_type == "admin" and assistant_type in ['customer', 'admin', 'affiliate', 'end_user']) or (user_type == "customer" and assistant_type in ['customer', 'affiliate', 'end_user']) or (user_type == "affiliate" and assistant_type in ['affiliate', 'end_user']) or (user_type == "end_user" and assistant_type in ['end_user']):
            try:
                table_name = "{0}_assistants_{1}s_threads".format(assistant_type, user_type)
                column_name = "{0}_id".format(user_type)
                
                formatted_list = select_from_table(table_name, user=user, user_type=user_type, filters={}, return_type="all")

                formatted_results = {'type': "ai_agents_list", 'data': formatted_list}
                # Ensure fetching results first
                return {"body": formatted_results, "statusCode": 200}
            except Exception as e:
                print("Listing AI Agents failed:", str(e))
                return {"body": "Internal Server Error", "statusCode": 500}
        else:
            return {"body": "Unauthorized or invalid assistant type", "statusCode": 401}
    else:
        return {"body": "Unauthorized or invalid user type", "statusCode": 401}


def retrieve_thread(user, user_type, assistant_type, public_id):
    if user_type in ['customer', 'admin', 'affiliate', 'system_admin', 'end_user']:
        if (user_type == "system_admin" and assistant_type in ['customer', 'admin', 'affiliate', 'system', 'end_user']) or (user_type == "admin" and assistant_type in ['customer', 'admin', 'affiliate', 'end_user']) or (user_type == "customer" and assistant_type in ['customer', 'affiliate', 'end_user']) or (user_type == "affiliate" and assistant_type in ['affiliate', 'end_user']) or (user_type == "end_user" and assistant_type in ['end_user']):
            try:
                table_name = "{0}_assistants_{1}s_threads".format(assistant_type, user_type)
                column_name = "public_id"
                
                formatted_list = select_from_table(table_name, column_name, user, user_type, "first_or_404", public_id=public_id)

                formatted_results = {'type': "ai_agents_list", 'data': formatted_list}
                # Ensure fetching results first
                return {"body": formatted_results, "statusCode": 200}
            except Exception as e:
                print("Listing AI Agents failed:", str(e))
                return {"body": "Internal Server Error", "statusCode": 500}
        else:
            return {"body": "Unauthorized or invalid assistant type", "statusCode": 401}
    else:
        return {"body": "Unauthorized or invalid user type", "statusCode": 401}