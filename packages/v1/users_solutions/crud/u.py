from context.context import session
def update_run(user, user_type, assistant_type, agent_id, update_data):
    if user_type in ['admin', 'system_admin']:  # Assuming only admins can update
        try:
            table_name = "{0}_assistants_{1}s_threads".format(assistant_type, user_type)
            update_query = (f"UPDATE {table_name} SET ... WHERE id = :id RETURNING *")
            results = session.execute(update_query, {"id": agent_id, **update_data})
            session.commit()
            updated_agent = results.fetchone()
            return {"body": {"message": "AI Agent updated successfully", "agent": dict(updated_agent)}, "statusCode": 200}
        except Exception as e:
            session.rollback()
            print("Failed to update AI Agent:", str(e))
            return {"body": "Internal Server Error", "statusCode": 500}
    else:
        return {"body": "Unauthorized to update AI Agents", "statusCode": 403}