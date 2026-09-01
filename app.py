# app.py
import os
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from flask import Flask, request, jsonify

app = Flask(__name__)

db_pool = SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    host=os.environ["DB_HOST"],
    dbname=os.environ["DB_NAME"],
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
)

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

@app.route("/hang", methods=["GET"])
def hang():
    """
    Celowo blokujący endpoint: wykonuje zapytanie SQL, które
    'wisi' 120 sekund, bez żadnego timeoutu po stronie backendu.
    Służy do zasymulowania kontenera, który 'żyje', ale nie odpowiada.
    """
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT pg_sleep(120);")  # blokuje ten wątek/proces na 120s
        return jsonify({"status": "finally responded"}), 200
    finally:
        db_pool.putconn(conn)

@app.route("/check", methods=["POST", "OPTIONS"])
def check():
    if request.method == "OPTIONS":
        return "", 204

    data = request.get_json(silent=True) or {}
    password_hash = data.get("hash")

    app.logger.info(f"Checking password hash: {password_hash}")

    if not password_hash:
        return jsonify({"error": "missing 'hash' field"}), 400

    conn = db_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM leaked_passwords WHERE hash = %s", (password_hash,)
            )
            compromised = cur.fetchone() is not None
    finally:
        db_pool.putconn(conn)

    return jsonify({"compromised": compromised})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)