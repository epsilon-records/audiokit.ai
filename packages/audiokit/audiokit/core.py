import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import requests
from datetime import date
import time
from datetime import datetime
import traceback
import hashlib
from config import cfg  # Directly import the configured instance


