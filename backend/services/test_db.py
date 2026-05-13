from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

driver = GraphDatabase.driver(os.getenv("NEO4J_URI"), auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD")))

def check_connection():
    try:
        driver.verify_connectivity()
        print("Successfully connected to Neo4j!")
    except Exception as e:
        print(f"Failed to connect to Neo4j: {e}")

if __name__ == "__main__":
    check_connection()