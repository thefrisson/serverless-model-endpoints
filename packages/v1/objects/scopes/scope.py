import os
import json
import requests
from context.context import safe_getattr

def get_scoping_object(user, user_type, scoping_table_name):
    resp = requests.get(
        url=f"https://{os.environ.get('TEMBO_DATA_DOMAIN')}/restapi/v1/dev.{scoping_table_name}",
        headers={"Authorization": f"Bearer {os.environ.get('TEMBO_TOKEN')}"},
        params={
            f'{user_type}_id': safe_getattr(user, f"{user_type}_id")
        }
    )

    response_dict = resp.json()

    print("response from tembo postgrest: ", response_dict)

    return response_dict