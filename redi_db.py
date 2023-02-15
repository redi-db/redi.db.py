import requests

class RediDB:
  def __init__(self, authorization: object = {'login': "root", 'password': "root", 'ip': "localhost", 'port': 5000, 'useSSL': False}):
    if 'login' not in authorization or 'password' not in authorization or 'ip' not in authorization or 'port' not in authorization:
      raise Exception('Incorrect filling of authorization data')
    self.authorization_data = authorization
    self.url = f'{"https" if authorization.get("useSSL") else "http"}://{authorization.get("ip")}:{authorization.get("port")}'
    self.fetch = requests.Session()

  def set_database(self, database: str = 'admin'):
    self.database = database
    self.url += f'/{database}'

    return __Collection__(self)

class __Collection__:
  def __init__(self, data: RediDB = RediDB()):
    if not data.database:
      raise Exception('The database name parameter is invalid')
    self.db = data

  def set_collection(self, collection: str = 'test'):
    self.db.collection = collection
    self.db.url += f'/{collection}'

    return self

  def create(self, *data):
    try:
      response = self.db.fetch.post(f'{self.db.url}/create', json={'login': self.db.authorization_data.get('login'), 'password': self.db.authorization_data.get('password'), 'data': data}).json()
      
      if not hasattr(response, '__len__') and response.get('success', None) == False:
        raise Exception(response.get('message'))
      return response
    except:
      raise Exception(f'Connection to database {self.db.database}/{self.db.collection} failed')

  def search(self, filter = {}):
    try:
      response = self.db.fetch.post(f'{self.db.url}/search', json={'login': self.db.authorization_data.get('login'), 'password': self.db.authorization_data.get('password'), 'filter': filter}).json()
      
      if not hasattr(response, '__len__') and response.get('success', None) == False:
        raise Exception(response.get('message'))
      return response
    except:
      raise Exception(f'Connection to database {self.db.database}/{self.db.collection} failed')

  def search_one(self, filter = {}):
    try:
      response = self.db.fetch.post(f'{self.db.url}/search', json={'login': self.db.authorization_data.get('login'), 'password': self.db.authorization_data.get('password'), 'filter': filter}).json()
      
      if not hasattr(response, '__len__') and response.get('success', None) == False:
        raise Exception(response.get('message'))

      if len(response) == 0:
        raise Exception('Not Found')

      return response[0]
    except:
      raise Exception(f'Connection to database {self.db.database}/{self.db.collection} failed')

  def delete(self, filter = {}):
    try:
      response = self.db.fetch.delete(self.db.url, json={'login': self.db.authorization_data.get('login'), 'password': self.db.authorization_data.get('password'), 'filter': filter}).json()
      
      if not hasattr(response, '__len__') and response.get('success', None) == False:
        raise Exception(response.get('message'))

      return response
    except:
      raise Exception(f'Connection to database {self.db.database}/{self.db.collection} failed')
  
  def update(self, filter = {}, update = {}):
    try:
      response = self.db.fetch.put(self.db.url, json={'login': self.db.authorization_data.get('login'), 'password': self.db.authorization_data.get('password'), 'data': {'filter': filter, 'update': update}}).json()
      
      if not hasattr(response, '__len__') and response.get('success', None) == False:
        raise Exception(response.get('message'))
      if len(response) == 0:
        raise Exception('Not Found')

      return response
    except:
      raise Exception(f'Connection to database {self.db.database}/{self.db.collection} failed')
  
  def search_or_create(self, filter, create = {}):
    try:
      response = self.db.fetch.post(f'{self.db.url}/searchOrCreate', json={'login': self.db.authorization_data.get('login'), 'password': self.db.authorization_data.get('password'), 'filter': filter, 'data': create}).json()
      
      if response.get('success', None) == False:
        raise Exception(response.get('message'))
      return response
    except:
      raise Exception(f'Connection to database {self.db.database}/{self.db.collection} failed')