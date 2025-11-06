from flask import Flask, jsonify
from flask_cors import CORS
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv

app = Flask(__name__)
app = os.getenv("DATABASE_URL")
