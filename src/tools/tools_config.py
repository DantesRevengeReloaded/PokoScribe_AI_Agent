import psycopg2

# Database connection
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "password"
DB_HOST = "localhost"
DB_PORT = "5432"

# Database connection
conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
)

# Search keywords
keywords = [
        "job satisfaction",
        "work performance",
        "employee engagement"
        "employee turnover"
]

