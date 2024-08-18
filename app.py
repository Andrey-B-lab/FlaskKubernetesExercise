from flask import Flask, request, jsonify
import psycopg2
import redis

app = Flask(__name__)

# PostgreSQL connection
conn = psycopg2.connect(
    dbname="mydbname",
    user="user",
    password="password",
    host="postgres-service",  # This will be the service name in Kubernetes
    port="5432"
)
cursor = conn.cursor()

# Redis connection
r = redis.Redis(host='redis-service', port=6379)

@app.route('/data', methods=['GET'])
def get_data():
    # Logic to get data from PostgreSQL or Redis cache
    cursor.execute("SELECT * FROM your_table")
    data = cursor.fetchall()
    return jsonify(data)

@app.route('/data', methods=['POST'])
def add_data():
    # Logic to add data to PostgreSQL and Redis cache
    new_data = request.json
    cursor.execute("INSERT INTO your_table (column1, column2) VALUES (%s, %s)", (new_data['column1'], new_data['column2']))
    conn.commit()
    return jsonify({"status": "success"}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
