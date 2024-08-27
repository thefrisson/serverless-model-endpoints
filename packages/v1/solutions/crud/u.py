import cloudinary
import cloudinary.uploader
import os
from context.context import session, update_table
def update_solution(event, user, user_type):
    if user_type in ['admin', 'system_admin']:  # Assuming only admins can update
        try:
            headers = event.get('http', {}).get('headers', {})
            content_type = headers.get('content-type', None)
            if content_type.startswith('multipart/form-data'):
                image = event.get('image', None)
                print(image)
                if image is not None:
                    cloudinary.config( 
                        cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'), 
                        api_key = os.environ.get('CLOUDINARY_API_KEY'), 
                        api_secret = os.environ.get('CLOUDINARY_API_SECRET')
                    )
                    # Should get user and stripe_passport here (obviously taking shortcuts)
                    # Don't forget to add the passport_id back into the folder name for cloudinary upload.
                    cdn_response = cloudinary.uploader.upload(image, folder=f'customer_teams/solutions')
                    update_dict = {'cover_image_url': cdn_response['secure_url']}
                updated_solution = update_table("solution", 'public_id', "ff6cb38a-8e34-4efa-b829-5f82039e51bd", update_dict)

                return {"body": {"message": "Solution updated successfully", "agent": ""}, "statusCode": 200}
            else:
                return {"body": "Content-Type incorrect or None", "statusCode": 400}
        except Exception as e:
            session.rollback()
            print("Failed to update Solution:", str(e))
            return {"body": "Internal Server Error", "statusCode": 500}
    else:
        return {"body": "Unauthorized to update Solutions", "statusCode": 403}