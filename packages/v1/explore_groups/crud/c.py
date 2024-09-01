import json
import os
import openai
import cloudinary
import cloudinary.uploader

from datetime import datetime as dt
import time as t
from context.context import select_from_table, insert_into_table, safe_getattr, row_to_dict


def create_solution(event, user, user_type):
    try:
        body_str = event.get('http', {}).get('body', "{}")
        body_dict = json.loads(body_str)

        if user_type not in ['customer', 'admin', 'system_admin']:
            return {
                "error": "Incorrect user type",
                "statusCode": 400,
            }
        else:

            title = body_dict.get('title', None)
            type = body_dict.get('type', None)
            description = body_dict.get('description', None)
            url = body_dict.get('url', None)
            role = body_dict.get('role', None)
            

            
            if any(var is None for var in [title, type, description, url, role]):
                return {
                    "error": "Incorrect Parameters",
                    "statusCode": 400,
                } 
            else:

                cloudinary.config( 
                    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'), 
                    api_key = os.environ.get('CLOUDINARY_API_KEY'), 
                    api_secret = os.environ.get('CLOUDINARY_API_SECRET')
                )

                # Existing logic for creating an AI assistant when assistant_type == "customer"
                stripe_passport = select_from_table(f'{user_type}_stripe_passport', filters={f'{user_type}_passport_id': safe_getattr(user, 'selected_team')}, return_type="first_or_404")
                print(f"{user_type}_stripe_passport selected", stripe_passport)

                team_user_link = select_from_table(f'{user_type}s_stripe_passports', filters={'stripe_passport_id': safe_getattr(user, 'selected_team'), f'{user_type}_id': safe_getattr(user, f'{user_type}_id')},return_type="first_or_404")
                print(f"{user_type}s_stripe_passports selected", team_user_link)

                permission_passport = select_from_table(f'{user_type}s_permissions', return_type="first_or_404", filters={f'{user_type}_id': safe_getattr(user, f'{user_type}_id')})
                print(f"{user_type}s_permissions selected", permission_passport)

                print("all objects selected")

                new_solution = insert_into_table('solution', ['solution_id', 'display_id'],
                    {
                        'title': title,
                        'type': type,
                        'description': description,
                        'url': url,
                        'log_json': json.dumps([{'time': dt.utcnow().strftime("%B %-d, %Y %H:%M:%S"), 'action_type': "create", 'action': f"was created"}]),
                        'timeline_json': json.dumps([{'time': dt.utcnow().strftime("%B %-d, %Y %H:%M:%S"), 'action_type': "create", 'action': f"was created"}])
                    }                        
                )
                print("new_solution: ", new_solution)

                new_solution_user_link = insert_into_table(f'{user_type}s_solutions', ['public_id'], {
                    f'{user_type}_id': safe_getattr(user, f'{user_type}_id'),
                    'solution_id': safe_getattr(new_solution, 'solution_id')
                })
                new_solution_team_link = insert_into_table(f'{user_type}_passports_solutions', ['public_id'], {
                    'passport_id': safe_getattr(stripe_passport, f'{user_type}_passport_id'),
                    'solution_id': safe_getattr(new_solution, 'solution_id')
                })

            print("solution created")

            return {"success": True, 'statusCode': 200}

    except Exception as e:
        print("Failed to create Solution:", str(e))
        return {'success': False, "body": "Internal Server Error", "statusCode": 500}

def create_solution_template_explore_groups(user, user_type, object_user_type, body_dict):
    try:
        if user_type not in ['customer', 'admin', 'system_admin']:
            return {
                "error": "Incorrect user type",
                "statusCode": 400,
            }
        else:
            print(body_dict)
            object_user_id = body_dict.get(f'{object_user_type if object_user_type != "system" else "system_admin"}_id', None)
            title = body_dict.get('title', None)
            description = body_dict.get('description', None)

            
            if any(var is None for var in [object_user_id, title, description]):
                print("body dictionary keys: ", body_dict.keys())
                return {
                    "error": "Incorrect Parameters",
                    "statusCode": 400,
                } 
            else:

                cloudinary.config( 
                    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'), 
                    api_key = os.environ.get('CLOUDINARY_API_KEY'), 
                    api_secret = os.environ.get('CLOUDINARY_API_SECRET')
                )

                # Existing logic for creating an AI assistant when assistant_type == "customer"
                stripe_passport = select_from_table(f'{user_type}_stripe_passport', filters={f'{user_type}_passport_id': safe_getattr(user, 'selected_team')}, return_type="first_or_404")
                print(f"{user_type}_stripe_passport selected", stripe_passport)

                team_user_link = select_from_table(f'{user_type}s_stripe_passports', filters={'stripe_passport_id': safe_getattr(user, 'selected_team'), f'{user_type}_id': safe_getattr(user, f'{user_type}_id')},return_type="first_or_404")
                print(f"{user_type}s_stripe_passports selected", team_user_link)

                permission_passport = select_from_table(f'{user_type}s_permissions', return_type="first_or_404", filters={f'{user_type}_id': safe_getattr(user, f'{user_type}_id')})
                print(f"{user_type}s_permissions selected", permission_passport)

                print("all objects selected")
                object_user_type_key = f'{object_user_type if object_user_type != "system" else "system_admin"}_id'
                new_explore_group = insert_into_table(f'{object_user_type}_solution_template_generic_group', [f'{object_user_type}_solution_template_generic_group_id'],
                    {
                        object_user_type_key: object_user_id,
                        'title': title,
                        'description': description,
                    }                        
                )
                print("new explore group: ", new_explore_group)

            return {"success": True, 'type': "solution_template_explore_group", 'data': row_to_dict(new_explore_group), 'statusCode': 200}

    except Exception as e:
        print("Failed to create Solution:", str(e))
        return {'success': False, "body": "Internal Server Error", "statusCode": 500}

