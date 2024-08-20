from flask import Flask, request, jsonify
import psycopg2
import redis

app = Flask(__name__)

# PostgreSQL connection setup
def get_db_connection():
    conn = psycopg2.connect(
        dbname="mydbname",
        user="user",
        password="password",
        host="postgres-service",  # Service name in Kubernetes
        port="5432"
    )
    return conn

# Initialize Redis connection
r = redis.Redis(host='redis-service', port=6379)

@app.route('/data', methods=['GET'])
def get_data():
    # Check if data is in cache
    cached_data = r.get('data')
    if cached_data:
        return jsonify(eval(cached_data))  # Convert string back to Python list

    # If not in cache, retrieve from PostgreSQL
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM your_table")
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    # Store the data in Redis cache
    r.set('data', str(data))

    return jsonify(data)

@app.route('/data', methods=['POST'])
def add_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    new_data = request.json
    cursor.execute("INSERT INTO your_table (column1, column2) VALUES (%s, %s)", 
                   (new_data['column1'], new_data['column2']))
    conn.commit()

    # Invalidate the cache
    r.delete('data')

    cursor.close()
    conn.close()
    return jsonify({"status": "success"}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
