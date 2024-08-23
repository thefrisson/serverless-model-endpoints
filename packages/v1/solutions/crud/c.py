import json
import os
import openai

from datetime import datetime as dt
import time as t
from context.context import select_from_table, insert_into_table, safe_getattr


def create_solution(event, user, user_type, assistant_type):
    try:
        body_str = event.get('http', {}).get('body', "{}")
        body_dict = json.loads(body_str)

        order_id = body_dict.get('order_id')
        print(order_id)

        if not order_id:
            return {
                "body": {"error": "Missing order ID"},
                "statusCode": 400,
                "headers": {
                    'Access-Control-Allow-Credentials': 'true',
                }
            }
        if user_type in ['customer', 'admin', 'system_admin']:
            # Existing logic for creating an AI assistant when assistant_type == "customer"
            stripe_passport = select_from_table(f'{user_type}_stripe_passport', filters={f'{user_type}_passport_id': safe_getattr(user, 'selected_team')}, return_type="first_or_404")
            print(f"{user_type}_stripe_passport selected", stripe_passport)

            team_user_link = select_from_table(f'{user_type}s_stripe_passports', filters={'stripe_passport_id': safe_getattr(user, 'selected_team'), f'{user_type}_id': safe_getattr(user, f'{user_type}_id')},return_type="first_or_404")
            print(f"{user_type}s_stripe_passports selected", team_user_link)

            permission_passport = select_from_table(f'{user_type}s_permissions', return_type="first_or_404", filters={f'{user_type}_id': safe_getattr(user, f'{user_type}_id')})
            print(f"{user_type}s_permissions selected", permission_passport)

            order = select_from_table(f'{user_type}_cart_system_order', filters={'public_id': order_id}, return_type="first_or_404")
            print(f"{user_type}_cart_system_order selected", order)

            product_links = select_from_table('system_products_customer_carts', filters={'cart_id': safe_getattr(order, 'cart_id') }, return_type="all")
            print(f"{user_type}_orders_system_products selected", product_links)
        
        else:
            return {
                "error": "Incorrect user type",
                "statusCode": 400,
                "headers": {
                    'Access-Control-Allow-Credentials': 'true',
                }
            }
        assistants_to_create = []
        ai_agent_product_id = os.environ.get('AIAGENT_PRODUCT_ID')

        for product_link in product_links:
            if safe_getattr(product_link, 'product_id') == ai_agent_product_id:
                # product = select_from_table('system_stripe_product', filters={'system_product_instance_id': safe_getattr(product_link, 'product_id')}, return_type='first_or_404')

                assistants_to_create.append(product_link)
            
        

        print("all objects selected")
        print(assistants_to_create)
        
        for assistant_link in assistants_to_create:
            assistant_data = json.loads(safe_getattr(assistant_link, 'more_info'))

            instructions = assistant_data.get('instructions')
            message = "What is 9*9*9*9?"
            print("creating assistant with openai")
            assistant = openai.beta.assistants.create(
                instructions=instructions,
                name=assistant_data.get('name'),
                tools=[{"type": "code_interpreter"}],
                model="gpt-4",
            )
            print("saving assistant to db")
            # Add new assistant to the database using the helper function
            new_assistant = insert_into_table(
                f'{assistant_type}_assistant',
                [f'{assistant_type}_assistant_id'],    
                {
                    'openai_id': assistant.id,
                    'stripe_passport_id': stripe_passport.customer_passport_id,
                    'meta_json': json.dumps(assistant_data),
                    'confine_threads': "team",
                    'log_json': json.dumps([{'time': dt.utcnow().strftime("%B %-d, %Y %H:%M:%S"), 'action_type': "create", 'action': f"was created"}])
                }
            )

            print(f"creating {assistant_type} assistant - {user_type} permissions composition object")

            
            # Creating links in the database
            assistant_permission_comp = insert_into_table(
                f'{assistant_type}_assistants_{user_type}s_permissions',
                [f'{assistant_type}_assistant_{user_type}_permissions_id'],
                {
                    f'{user_type}_id': safe_getattr(user, f'{user_type}_id'),
                    'assistant_id': safe_getattr(new_assistant, f'{assistant_type}_assistant_id')
                }
            )

            print("creating user - permission object")
            permissions_link = insert_into_table(f'{user_type}s_permissions', [],
                {
                    f'{user_type}_id': safe_getattr(user, f'{user_type}_id'),
                    f'{user_type}_permission_id': safe_getattr(permission_passport, f'{user_type}_permission_id'),
                    f'{user_type}_assistant_link_id': safe_getattr(assistant_permission_comp, f'{assistant_type}_assistant_{user_type}_permissions_id'),
                    'log_json': json.dumps([{'time': dt.utcnow().strftime("%B %-d, %Y %H:%M:%S"), 'user': {'id': safe_getattr(user, 'public_id')}, 'action_type': "create", 'action': f"was created"}])
                }
            )

            print("assistant created")

            return {"success": True, 'statusCode': 200}

    except Exception as e:
        print("Failed to create AI Agent:", str(e))
        return {'success': False, "body": "Internal Server Error", "statusCode": 500}

