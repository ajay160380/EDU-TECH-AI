import psycopg2
import os
import urllib.parse

db_url = "postgresql://neondb_owner:npg_3iTqUs6IPXAh@ep-shiny-wildflower-aosufft3-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

try:
    print("Connecting to NeonDB...")
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    print("Connected.")
    
    # Get user id
    cursor.execute("SELECT id FROM auth_user WHERE username = %s;", ('aryamaddy_1',))
    row = cursor.fetchone()
    if row:
        user_id = row[0]
        print(f"Found user_id: {user_id}")
        
        # Update user profile
        cursor.execute("UPDATE courses_userprofile SET plan_type = 'pro' WHERE user_id = %s;", (user_id,))
        conn.commit()
        print("Premium access 'pro' granted successfully.")
    else:
        print("User 'aryamaddy_1' not found in database.")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
