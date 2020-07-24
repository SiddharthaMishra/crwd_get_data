import psycopg2
import os
import json



def get_cursor():
    hostname = os.environ.get("DB_HOST", "localhost")
    port = os.environ.get("DB_PORT", "5432")
    dbname = os.environ.get("DB_NAME", "crwd")
    user = os.environ.get("DB_USER", "user")
    password = os.environ.get("DB_PASSWORD", "password")


    conn = psycopg2.connect(database=dbname, user=user, password=password, host=hostname)
    cursor = conn.cursor()
    return conn, cursor



def is_uploaded_course(title):
    conn, cursor = get_cursor()

    query = cursor.execute(
        "SELECT COUNT(*) FROM course where title=%s", (title,))
    exists = cursor.fetchone()[0]

    if exists != 0:
        print(f"course {title} exists")

    cursor.close()
    conn.close()

    return exists != 0

    

def insert_course(title, link, tags, professor, picture, description):
    conn, cursor = get_cursor()

    cursor.execute(
        "INSERT INTO course(title, link, professor, picture, description, courseinfo) VALUES(%s, %s, %s, %s, %s, %s)",
        (
            title,
            link,
            professor,
            picture,
            description,
            json.dumps({
                "tags": tags,
                "reviews": [],
                "comments": [],
            })
        )
    )
    conn.commit()
    cursor.close()
    conn.close()
