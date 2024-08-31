from context.context import delete_from_table, session
def delete_solution(user, user_type, assistant_type):
    if user_type in ['customer', 'admin', 'system_admin']:
        try:
            deleted_object = delete_from_table('customer_orders_system_products', timestamp_column='created_timestamp')
            if not isinstance(deleted_object, dict):
                print(True)
                return {'success': True, 'statusCode': 200}
            else:
                print('deleted object: ', deleted_object)
                return {'success': False, 'statusCode': 400}
        except Exception as e:
            session.rollback()
            print("Failed to delete AI Agent:", str(e))
            return {"body": "Internal Server Error", "statusCode": 500}

    else:
        return {"body": "Unauthorized to delete AI Agents", "statusCode": 403}