from requests import Session


class RediDB:
    def __init__(self, authorization: object = {'login': "root", 'password': "root", 'ip': "localhost", 'port': 5000, 'useSSL': False}):
        if 'login' not in authorization or 'password' not in authorization or 'ip' not in authorization or 'port' not in authorization:
            raise Exception('Incorrect filling of authorization data')

        self.authorization_data = authorization
        self.url = f'{"https" if authorization.get("useSSL") else "http"}://{authorization.get("ip")}:{authorization.get("port")}'
        self.fetch = Session()

    def set_database(self, database: str = 'admin'):
        return __Database__(self, database)


class __Database__:
    def __init__(self, client: RediDB, database: str):
        self.client = client
        self.database = database

    def invoke(self):
        return __Collection__(self)


class __Collection__:
    def __init__(self, data: __Database__):
        if not data.database:
            raise Exception('The database name parameter is invalid')
        self.db = data

    def req(self, path: str, method, body: object):
        response = None
        try:
            body['database'] = self.db.database
            body['collection'] = self.collection
            body['login'] = self.db.client.authorization_data.get('login')
            body['password'] = self.db.client.authorization_data.get(
                'password')

            response = eval(
                f"""self.db.client.fetch.{method}(f'{self.db.client.url}/{path}', json=body).json()""")
        except:
            raise Exception(
                f'Connection to database {self.db.database}/{self.collection} failed')

        if type(response) != list and response.get('success', None) == False:
            raise Exception(response.get('message'))
        return response

    def set_collection(self, collection: str = 'test'):
        self.collection = collection
        return self

    def count(self, filter: object = {}):
        filter['$only'] = ['']
        return len(self.search(filter))

    def create(self, *data):
        return self.req('create', 'post', {
            'data': data
        })

    def search(self, filter={}):
        return self.req('search', 'post', {
            'filter': filter
        })

    def search_one(self, filter={}):
        filter['$max'] = 1
        response = self.search(filter)
        if len(response) == 0:
            return None

        return response[0]

    def delete(self, filter={}):
        return self.req('', 'delete', {
            'filter': filter
        })

    def update(self, filter={}, update={}):
        return self.req('', 'patch', {
            'data': {
                'filter': filter,
                'update': update
            }
        })

    def instant_update(self, filter={}, update={}):
        return self.req('', 'put', {
            'data': {
                'filter': filter,
                'update': update
            }
        })

    def search_or_create(self, filter, create={}):
        return self.req('searchOrCreate', 'post', {
            'filter': filter,
            'data': create
        })
