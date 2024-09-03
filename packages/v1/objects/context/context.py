import json
import jwt
import os
import uuid
from datetime import datetime as dt, date, time
from sqlalchemy import Table, MetaData, create_engine, insert, update, delete, desc
from sqlalchemy.engine import Row, ResultProxy 
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.sql import text

try:
    Base = declarative_base()
    engine = create_engine(os.environ.get('DATABASE_URL', ''))
    Session = scoped_session(sessionmaker(bind=engine))
    metadata = MetaData()
except Exception as e:
    print("issue initializing database connection:", str(e))

def get_session():
    return Session()



def secured_user(event):
    decoded = decode_jwt_from_event(event)
    # decoded = event['cookie']

    try:
        user_type = decoded['user_type']
        user_id = decoded['sub']
        print("user_type: " + user_type)
        print(f"{user_type}_id: " + user_id)

        if user_type in ['customer', 'admin', 'affiliate', 'system_admin']:
            try:
                # Safely construct the query using fixed table and column names as appropriate
                table_name = f"{user_type}"
                column_name = f"{user_type}_id"
                
                # Constructing a secure text query
                query = text(f"SELECT * FROM {table_name} WHERE {column_name} = :value")
                results = session.execute(query, {'value': user_id})
                rows = results.fetchall()  # Fetch all results

                # Check if there's exactly one matching record
                if len(rows) == 1:
                    row = rows[0]
                    print(type(row))
                    print(row)
                    return user_type, row
                
            except Exception as e:
                print("Error during database operation:", str(e))

        return 200, {'statusCode': 200, 'body': 'Access granted', 'type': "ai_agents_list"}
    except jwt.InvalidTokenError as e:
        return 401, {'statusCode': 401, 'body': 'Invalid or expired token'}
    except Exception as e:
        return 401, {'statusCode': 401, 'body': f'db probably isnt connected well. {str(e)}'}


def path_to_list(path):
    """
    Convert a path string into a list of segments, removing the leading slash.
    
    Parameters:
    path (str): The path string to be converted.

    Returns:
    list: A list of segments from the path.
    """
    # Remove the leading slash if it exists
    if path.startswith('/'):
        path = path[1:]
    
    # Split the path by slashes and return the resulting list
    path_list = path.split('/')
    return [entry for entry in path_list if entry]


def is_valid_uuid(s):
    try:
        uuid.UUID(s, version=4)
        return True
    except ValueError:
        return False

def row_to_dict(row):
    """
    Convert a SQLAlchemy Row object to a dictionary.
    Handles SQLAlchemy engine Row objects specifically and
    converts non-serializable types like datetime to strings.
    """
    if row is None:
        return None
    
    def convert_value(value):
        if isinstance(value, dt):
            return value.isoformat()  # Convert datetime to ISO format string
        elif isinstance(value, date):
            return value.isoformat()  # Convert date to ISO format string
        elif isinstance(value, time):
            return value.isoformat()  # Convert time to ISO format string
        # Add more conversions here if needed
        return value
    
    # Handle SQLAlchemy Row objects
    if isinstance(row, Row):
        return {key: convert_value(getattr(row, key)) for key in row._fields}
    
    # Fallback for dictionary-like rows
    return {key: convert_value(row[key]) for key in row.keys()}



def safe_getattr(obj, attr, default=None):
    """
    Safely get an attribute or key from an object or dictionary.
    
    :param obj: The object, dictionary, or SQLAlchemy result from which to retrieve the attribute.
    :param attr: The attribute or key name to retrieve.
    :param default: The default value to return if the attribute or key is not found.
    :return: The attribute's value if found, otherwise the default value.
    """
    try:
        # Handle CursorResult and similar iterable result objects
        if isinstance(obj, ResultProxy):
            print("result proxy found")
            row = obj.fetchone()  # Fetch the first row if it's a result set
            if row is None:
                return default
            return row[attr] if attr in row else default

        # Handle dictionary-like objects
        if isinstance(obj, dict):
            return obj.get(attr, default)
        
        # Handle regular objects with dot notation
        return getattr(obj, attr, default)
    
    except Exception as e:
        print(f"Error: {attr} is not an available attribute of the {type(obj)} object passed. Default of type {type(default)} returned. Details: {e}")
        return default


def select_from_table(table_name, user=None, user_type=None, filters=None, return_type="all"):
    try:
        # Start with a basic SELECT statement
        query_string = f"SELECT * FROM {table_name} WHERE 1=1"
        query_params = {}

        # Conditionally add user-specific filters if user and user_type are provided
        if user and user_type:
            user_id_column = f"{user_type}_id"
            user_id_value = safe_getattr(user, user_id_column)
            if user_id_value:
                query_string += f" AND {user_id_column} = :{user_id_column}"
                query_params[user_id_column] = user_id_value

        # Add additional filters if provided
        if filters:
            for key, value in filters.items():
                query_string += f" AND {key} = :{key}"
                query_params[key] = value

        # Execute the query
        selected_records = text(query_string)
        results = session.execute(selected_records, query_params)
        
        # Handle the return type
        if return_type == "all":
            rows = results.fetchall()
            if not rows:
                return {"body": "No records found", "statusCode": 404}
            return [row for row in rows]
        elif return_type == "first_or_404":
            row = results.fetchone()
            if not row:
                return {"body": "Resource not found", "statusCode": 404}
            return row

        # Handle unexpected return types
        return {"body": "Invalid return type specified", "statusCode": 400}
    
    except SQLAlchemyError as e:
        session.rollback()
        print("Database query failed:", str(e))
        return {"body": "Internal Server Error", "statusCode": 500}
    except Exception as e:
        print("An error occurred:", str(e))
        return {"body": "Internal Server Error", "statusCode": 500}


def insert_into_table(table_name, generate_uuid_list, parameters):
    try:
        # Load the table metadata dynamically
        table = Table(table_name, metadata, autoload_with=engine)

        # Retrieve valid column names from the table
        columns = {column.name for column in table.columns}

        # Generate UUIDs for specified columns
        for uuid_key in generate_uuid_list:
            parameters[uuid_key] = str(uuid.uuid4())

        # Provide default values for missing columns
        default_values = {
            'log_json': json.dumps([{'time': dt.utcnow().strftime("%B %-d, %Y %H:%M:%S"), 'action_type': "create", 'action': "was created"}]),
            'public_id': str(uuid.uuid4()),
            'created_timestamp': dt.utcnow(),
            'last_updated_timestamp': dt.utcnow(),
            'status': os.environ.get('ACTIVE_STATUS'),
        }

        for col in default_values:
            if col in columns and col not in parameters:
                parameters[col] = default_values[col]

        # Filter parameters to keep only valid columns for insertion
        valid_parameters = {k: v for k, v in parameters.items() if k in columns}

        # Identify any unconsumed columns (if any)
        unconsumed_columns = set(parameters.keys()) - set(valid_parameters.keys())
        if unconsumed_columns:
            print(f"Unconsumed column names: {', '.join(unconsumed_columns)}")
            raise ValueError(f"Unconsumed column names: {', '.join(unconsumed_columns)}")

        # Perform the insert operation
        insert_stmt = insert(table).values(**valid_parameters)
        result = session.execute(insert_stmt)
        session.commit()

        # Retrieve the primary key value of the inserted row
        primary_key_value = result.inserted_primary_key[0]
        select_stmt = text(f"SELECT * FROM {table_name} WHERE id = :pk")
        inserted_row = session.execute(select_stmt, {'pk': primary_key_value}).fetchone()

        return inserted_row

    except Exception as e:
        session.rollback()
        print(e)
        return {'body': f"Failed to insert into {table_name}: {str(e)}", 'statusCode': 400}

def update_table(table_name, key_column, key_value, update_data):
    try:
        table = Table(table_name, metadata, autoload_with=engine)
        
        # Ensure that the key column is part of the table
        if key_column not in table.columns:
            return {"body": f"Invalid key column: {key_column}", "statusCode": 400}

        # Build the update statement
        update_stmt = (
            update(table)
            .where(table.c[key_column] == key_value)
            .values(**update_data)
            .returning(*table.columns)
        )
        
        # Execute the update and commit the transaction
        result = session.execute(update_stmt)
        session.commit()

        updated_row = result.fetchone()

        if not updated_row:
            return {"body": "No record found to update", "statusCode": 404}

    except Exception as e:
        session.rollback()
        print(f"Failed to update record in {table_name}: {e}")
        return {"body": "Internal Server Error", "statusCode": 500}



def delete_from_table(table_name, key_column=None, key_value=None, timestamp_column=None):
    try:
        table = Table(table_name, metadata, autoload_with=engine)

        # Ensure that the key column or timestamp column is part of the table
        if key_column and key_column not in table.columns:
            return {"body": f"Invalid key column: {key_column}", "statusCode": 400}
        if timestamp_column and timestamp_column not in table.columns:
            return {"body": f"Invalid timestamp column: {timestamp_column}", "statusCode": 400}

        if key_column and key_value:
            # Delete based on a specific key column and value
            delete_stmt = delete(table).where(table.c[key_column] == key_value)
        elif timestamp_column:
            # Delete the most recent record based on the specified timestamp column
            subquery = session.query(table).order_by(desc(table.c[timestamp_column])).limit(1).subquery()
            delete_stmt = delete(table).where(table.c[table.primary_key.columns.keys()[0]] == subquery.c[table.primary_key.columns.keys()[0]])
        else:
            return {"body": "Must specify either key_column and key_value, or timestamp_column", "statusCode": 400}

        # Execute the delete and commit the transaction
        result = session.execute(delete_stmt)
        session.commit()

        if result.rowcount > 0:
            return result
        else:
            return {"body": "No record found to delete", "statusCode": 404}

    except Exception as e:
        session.rollback()
        print(f"Failed to delete record in {table_name}: {e}")
        return {"body": "Internal Server Error", "statusCode": 500}


def check_for_error(sql_result):
    if isinstance(sql_result, dict):
        return sql_result
    

def default_converter(o):
    if isinstance(o, dt):
        return o.isoformat()
    return o

def decode_jwt_from_event(event):
    actual_headers = event['__ow_headers']
    cookies = actual_headers.get('cookie', '')
    if cookies == "":
        return {
            "body": {"error": "No cookies received. Probably trying to access this function from a local development scope, which is not allowed due to CORS Policies."},
            "statusCode": 400,
            "headers": {
                'Access-Control-Allow-Credentials': 'true',
            }
        }
    token = extract_jwt_from_cookies(cookies)
    SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.exceptions.ExpiredSignatureError as e:
        return {
            "body": {"error": "Expired JWT."},
            "statusCode": 400,
            "headers": {
                'Access-Control-Allow-Credentials': 'true',
            }
        }

    return decoded

def extract_jwt_from_cookies(cookie_string):
    # This function parses the cookie string to find the JWT.
    cookies_dict = dict(x.split('=') for x in cookie_string.split('; '))
    return cookies_dict.get('access_token_cookie', '')


def close_session(session):
    session.close()
    print("made it to here")

session = get_session()


