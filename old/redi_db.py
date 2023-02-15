import requests

class RediDB:
  def __init__(self, authorization: object = {'login': "root", 'password': "root", 'ip': "localhost", 'port': 5000}):
    if 'login' not in authorization or 'password' not in authorization or 'ip' not in authorization or 'port' not in authorization:
      raise Exception('Incorrect filling of authorization data')
    self.authorization_data = authorization
    self.url = f'http://{authorization.get("ip")}:{authorization.get("port")}/db'
    self.fetch = requests.Session()

  def test_connect(self):
    try:
      self.fetch.get(f'{self.url}/admin/test/search').json()
    except:
      raise Exception('Authentication error')
    return self

  def set_database(self, database: str = 'admin'):

    self.database = database
    self.url += f'/{database}'

    return __Collection__(self)

class __Collection__:
  def __init__(self, data: RediDB = RediDB()):
    if not data.database:
      raise Exception('The database name parameter is undefined')
    self.db = data

  def set_collection(self, collection: str = 'test'):
    self.db.collection = collection
    self.db.url += f'/{collection}'

    return self

  def create(self, key: str, data = {}):
    try:
      _data = []
      if type(data) is dict:
        _data.append({'value': data})
      else:
        for value in data:
          obj = {}
          if value.get('_key', None):
            obj['key'] = value.get('_key', None)
            del value['_key']
          obj['value'] = value
          _data.append(obj)

      response = self.db.fetch.post(f'{self.db.url}/create', json={'login': self.db.authorization_data.get('login'), 'password': self.db.authorization_data.get('password'), 'data': _data}).json()
      if response.get('success', None) == False:
        raise Exception(response.get('message'))
      return response
    except:
      raise Exception(f'Connection to database {self.db.database}/{self.db.collection} failed')

  def search(self, _filter = {}):
    try:
      response = self.db.fetch.post(f'{self.db.url}/search', json={'login': self.db.authorization_data.get('login'), 'password': self.db.authorization_data.get('password'), 'filter': _filter}).json()
      
      if type(response) != list and response.get('success', None) == False:
        raise Exception(response.get('message'))
      return response
    except:
      raise Exception(f'Connection to database {self.db.database}/{self.db.collection} failed')

  def search_one(self, _filter = {}):
    try:
      response = self.db.fetch.post(f'{self.db.url}/searchOne', json={'login': self.db.authorization_data.get('login'), 'password': self.db.authorization_data.get('password'), 'filter': _filter}).json()
      
      if type(response) != list and response.get('success', None) == False:
        raise Exception(response.get('message'))

      if len(response) == 0:
        raise Exception('Not Found')

      return response[0].get('value')
    except:
      raise Exception(f'Connection to database {self.db.database}/{self.db.collection} failed')

  def delete(self, key: str, _filter = {}):
    try:
      response = self.db.fetch.post(f'{self.db.url}/delete', json={'login': self.db.authorization_data.get('login'), 'password': self.db.authorization_data.get('password'), 'key': key, 'filter': _filter}).json()
      
      if type(response) != list and response.get('success', None) == False:
        raise Exception(response.get('message'))

      return response
    except:
      raise Exception(f'Connection to database {self.db.database}/{self.db.collection} failed')
  
  def update(self, key: str, _update = {}):
    try:
      response = self.db.fetch.post(f'{self.db.url}/update', json={'login': self.db.authorization_data.get('login'), 'password': self.db.authorization_data.get('password'), 'data': [{'key': key, 'value': _update}]}).json()
      
      if type(response) != list and response.get('success', None) == False:
        raise Exception(response.get('message'))
      if len(response) == 0:
        raise Exception('Not Found')

      return response
    except:
      raise Exception(f'Connection to database {self.db.database}/{self.db.collection} failed')
  
  def update_one(self, key: str, _filter = {}, _update = {}):
    try:
      response = self.db.fetch.post(f'{self.db.url}/update', json={'login': self.db.authorization_data.get('login'), 'password': self.db.authorization_data.get('password'), 'data': [{'key': key, 'where': _filter, 'value': _update}]}).json()
      
      if type(response) != list and response.get('success', None) == False:
        raise Exception(response.get('message'))
      if len(response) == 0:
        raise Exception('Not Found')

      return response[0]
    except:
      raise Exception(f'Connection to database {self.db.database}/{self.db.collection} failed')
  
  def find_or_create(self, _filter, _create = {}):
    try:
      return self.search_one(_filter)
    except:
      response = self.create(_create.get('_key', None), _create)

      print(response)
      return self.search_one({'_id': response.get('data')[0].get('key')})