import json
import os
import openai

from datetime import datetime as dt
import time as t
from context.context import select_from_table, insert_into_table, safe_getattr


def create_thread(event, user, user_type, assistant_type):
    try:
        if assistant_type == "customer":
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

                thread = openai.beta.threads.create()
                new_thread = insert_into_table('customer_assistant_thread',
                    ['customer_assistant_thread_id'],
                    {
                        'openai_id': thread.id,
                        'team_link_id': safe_getattr(team_user_link, 'customer_passport_link_id'),
                        'log_json': json.dumps([{'time': dt.utcnow().strftime("%B %-d, %Y %H:%M:%S"), 'action_type': "create", 'action': f"was created"}])
                    }
                )

                print("thread created. ", thread)
                print("creating user - assistant object")

                assistant_thread_comp = insert_into_table('customer_assistants_customers_threads',
                    ['customer_assistant_customer_thread_id'],
                    {
                        'customer_id': safe_getattr(user, 'customer_id'),
                        'assistant_id': safe_getattr(new_assistant, 'customer_assistant_id'),
                        'thread_id': safe_getattr(new_thread, 'customer_assistant_thread_id')
                    }
                )
                
                print("thread created")

                thread_message = openai.beta.threads.messages.create(
                    thread.id,
                    role="user",
                    content=message,
                )
                print("message created in thread")

                run = openai.beta.threads.runs.create(
                    thread_id=thread.id,
                    assistant_id=assistant.id
                )
                new_run = insert_into_table('customer_assistant_run',
                    ['customer_assistant_run_id'],
                    {
                        'assistant_id': safe_getattr(new_assistant, 'customer_assistant_id'),
                        'thread_id': safe_getattr(new_thread, 'customer_thread_id'),
                        'openai_id': run.id
                    }
                )

                assistant_run_comp = insert_into_table('customer_assistants_customers_runs',
                    ['customer_assistant_customer_run_id'],
                    {
                        'customer_id': safe_getattr(user, 'customer_id'),
                        'assistant_id': safe_getattr(new_assistant, 'customer_assistant_id'),
                        'run_id': safe_getattr(new_run, 'customer_assistant_run_id')
                    }
                )

                print("run created for messages in thread")
                print(run)

                run_status = run.status

                while run_status == "queued" or (run_status != "completed" and run_status != "failed" and run_status != "canceled"):
                    t.sleep(1)
                    print(run_status)
                    retrieve_run = openai.beta.threads.runs.retrieve(
                        thread_id=thread.id,
                        run_id=run.id
                    )
                    run_status = retrieve_run.status

                print("run status:")
                print(run_status)

                messages = openai.beta.threads.messages.list(
                    thread_id=thread.id
                )

                print("Resulting message feed:")
                print(messages)
                return {
                    "success": True, 
                    "messages": messages,
                    "statusCode": 200,
                    "headers": {
                        'Access-Control-Allow-Credentials': 'true',
                    }
                }
        elif assistant_type == "expert":
            pass
        else:
            # Handle other assistant types if necessary
            return {
                "body": {"error": "Unsupported assistant type"},
                "statusCode": 400,
                "headers": {
                    'Access-Control-Allow-Credentials': 'true',
                }
            }
    except Exception as e:
        print("Failed to create AI Agent:", str(e))
        return {'success': False, "body": "Internal Server Error", "statusCode": 500}

