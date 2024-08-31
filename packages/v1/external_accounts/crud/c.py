import json
import os
import openai
import cloudinary
import cloudinary.uploader
from google.cloud import secretmanager
from google.oauth2 import service_account


from datetime import datetime as dt
import time as t
from context.context import select_from_table, insert_into_table, safe_getattr


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



def generate_google_secret(secret_key, secret_value, folder_name):
    # Get the service account JSON from environment variables
    service_account_info = json.loads(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON'))
    
    # Authenticate using the service account JSON key
    credentials = service_account.Credentials.from_service_account_info(service_account_info)
    
    # Initialize the Secret Manager client with the credentials
    client = secretmanager.SecretManagerServiceClient(credentials=credentials)

    # Replace with your Google Cloud Project ID
    project_id = "orangeisbetter-general"  # Change to your actual project ID

    # Define the name and payload of the secret
    secret_id = secret_key
    secret_payload = secret_value

    # Create the parent resource
    parent = folder_name

    # Create a new secret
    try:
        secret = client.create_secret(
            request={
                "parent": parent,
                "secret_id": secret_id,
                "secret": {
                    "replication": {"automatic": {}},
                },
            }
        )
        print(f"Created secret: {secret.name}")

        # Add a new version with the secret data
        response = client.add_secret_version(
            request={
                "parent": secret.name,
                "payload": {
                    "data": secret_payload.encode("UTF-8"),
                },
            }
        )
        print(f"Added secret version: {response.name}")
        return {
            "statusCode": 200,
            "body": f"Secret {secret_id} created successfully"
        }
    except Exception as e:
        print(f"Error creating secret: {e}")
        return {
            "statusCode": 500,
            "body": f"Error creating secret: {str(e)}"
        }