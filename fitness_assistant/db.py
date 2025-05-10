import os 
import psycopg2 
from psycopg2.extras import DictCursor
from zoneinfo import ZoneInfo
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# enviroment variable setup 
Tz_info =os.getenv('Tz_inf','Africa/Cairo')

tz =ZoneInfo(Tz_info)

# database connection function
def get_db_connection():
    return psycopg2.connect(
        host =os.getenv('POSTGRES_HOST') ,
        database=os.getenv('POSTGRES_DB')  ,
        user =os.getenv('POSTGRES_USER')   ,
        password =os.getenv('POSTGRES_PASSWORD')
    )

def init_db():
    connection =get_db_connection()
    try:
       with connection.cursor() as cur:
           cur.execute("drop table if exists feedback") 
           cur.execute("drop table if exists conversations")

           cur.execute("""
            create table conversations(
                    Id text primary key,
                    question text not null ,
                    answer text not null,
                    relevance text not null,
                    relevance_explination text not null,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
                    )
                    """)
           cur.execute("""
                CREATE TABLE feedback (
                    id serial primary key,
                    conversation_id text REFERENCES conversations(Id),
                    feedback integer not null,
                    timestamp TIMESTAMP WITH TIME ZONE not null
                )
            """)
           
           connection.commit() # save changes to database
    finally:
           connection.close()


def save_conversation(conversation_id,question,answer_data,timestamp=None):
    
    if timestamp ==None :
            timestamp =datetime.now(tz)
    
    conn =get_db_connection()
    try:
        with conn.cursor() as cur:
                cur.execute("""
                insert into conversations 
                (Id,question,answer,
                relevance,relevance_explination, 
                timestamp)
                
                values(%s, %s, %s, %s, %s, %s)
                
                """,
                (
                    conversation_id,
                    question,
                    answer_data['answer'],
                    answer_data["relevance"],
                    answer_data["relevance_explanation"],
                    timestamp
                    
                )
            )
        conn.commit()
    finally:
        conn.close()


def save_feedback(conversation_id,feedback,timestamp=None):
    if timestamp ==None:
            timestamp =datetime.now(tz)

    conn =get_db_connection()
    try:
        with conn.cursor as cur:
            cur.excute("""
               insert into feedback(conversation_id,feedback,timestamp)
               values(%s,%s,%s)
            """,
            (
                conversation_id,
                feedback,
                timestamp
            )
            )
        conn.commit()
    finally:
        conn.close()



def get_recent_conversation(limit=5,relevance=None):
    conn =get_db_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            query ="""
               select c.* ,f.feedback 
               from conversations as c
               left join feedback as f
               on f.conversation_id = c.Id
            """
            if relevance:
                 query +=f"""where c.relevance ='{relevance}'"""

            query +="order by c.timestamp desc limit %s"

            cur.execute(query,(limit,))

            return cur.fetchall()
    finally:
         conn.close()


def get_feedback_satuts():
    'calcualte total number of positve and negative feedbacks'
    conn =get_db_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("""
             select
                 sum(case when feedback >0 then 1 else 0 end) as thumbs_up,
                 sum(case when feedback < 0 then 1 else 0 end) as thumbs_down
             from feedback
             """)
            
            cur.fetchall()
    finally:
        cur.close()


 