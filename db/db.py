import os
import mysql.connector

def get_connection():
    db_host = os.getenv("DB_HOST", "localhost")
    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("DB_PASSWORD", "")
    db_name = os.getenv("DB_NAME", "chatbot_data")
    db_port = int(os.getenv("DB_PORT", "3306"))

    return mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name,
        port=db_port
    )

def get_colleges_by_marks(marks):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT name, location, course
    FROM colleges
    WHERE cutoff <= %s
    ORDER BY cutoff DESC
    LIMIT 5
    """

    cursor.execute(query, (marks,))
    results = cursor.fetchall()

    conn.close()

    return results   # returns list of tuples

def save_chat(user_msg, bot_res, intent, confidence):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO chat_logs (user_message, bot_response, intent, confidence)
    VALUES (%s, %s, %s, %s)
    """

    cursor.execute(query, (user_msg, bot_res, intent, confidence))
    conn.commit()
    conn.close()