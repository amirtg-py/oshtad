from pymongo import MongoClient
import os

def reset_database():
    try:
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        client = MongoClient(mongo_url)
        client.drop_database('medical_store')
        print('Database medical_store dropped successfully.')
    except Exception as e:
        print(f'Error dropping database: {e}')

if __name__ == '__main__':
    reset_database()