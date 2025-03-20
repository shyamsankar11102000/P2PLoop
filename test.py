from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
# Database connection details
DATABASE_CONFIG = {
    'dbname': 'P2PLoop',
    'user': 'postgres',
    'password': '1313',
    'host': 'localhost',
    'port': '5432'
}
conn = psycopg2.connect(**DATABASE_CONFIG)
cursor = conn.cursor()
cursor.execute("SELECT 1;")
print(cursor.fetchone())
cursor.close()
conn.close()
