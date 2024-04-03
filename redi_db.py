from requests import Session
from websockets import connect as websocket_connect
from json import dumps, loads
from time import time


class EventManager:
    def __init__(self):
        self.events = {}

    def on(self, event_name, callback):
        if event_name not in self.events:
            self.events[event_name] = []
        self.events[event_name].append(callback)

    async def emit(self, event_name, *args, **kwargs):
        callbacks = self.events.get(event_name, [])
        for callback in callbacks:
            await callback(*args, **kwargs)


class RediDB:
    def __init__(self, authorization: object = {'login': "root", 'password': "root", 'ip': "localhost", 'port': 5000}, websocket: bool = True, useSSL: bool = False):
        if 'login' not in authorization or 'password' not in authorization or 'ip' not in authorization or 'port' not in authorization:
            raise Exception('Incorrect filling of authorization data')

        self.event_manager = EventManager()
        self.authorization_data = authorization

        self.protocol = 'ws' if websocket else 'http'
        self.url = f'{("https" if useSSL else "http") if not websocket else ("wss" if useSSL else "ws")}://{authorization.get("ip")}:{authorization.get("port")}{"/ws?login="+authorization.get("login") + "&password="+authorization.get("password") if websocket else ""}'

        if not websocket:
            self.fetch = Session()
        else:
            self.first_connect = False
            self.ws = None

    def on(self, event_name):
        def decorator(callback):
            async def async_callback(*args, **kwargs):
                await callback(*args, **kwargs)

            self.event_manager.on(event_name, async_callback)
            return callback

        return decorator

    async def connect(self):
        if self.protocol != 'ws':
            raise Exception(
                '.connect() can only be used if you have a websocket protocol')

        await self.initialize_websocket()

    async def initialize_websocket(self):
        try:
            self.ws = await websocket_connect(self.url)
            await self.websocket_request('_', '_', 'search', {'$max': 1}, {}, True)
        except Exception as error:
            if str(error) == 'server rejected WebSocket connection: HTTP 401':
                raise Exception('Bad Authorization (401)')
            elif str(error) == 'The remote computer refused the network connection':
                raise Exception('Failed to connect to the database')
            else:
                raise error

    async def websocket_request(self, database: str, collection: str, method: str, filter: list, data: list, event: bool = False):
        if not self.ws:
            raise Exception(
                'The websocket has not been initialized, you need to use .connect()')

        obj = {
            'database': database,
            'collection': collection,

            'method': method,
            'requestID': int(time() * 1000),
            'filter': filter,
            **data
        }

        try:
            await self.ws.send(dumps(obj))

            response_string = await self.ws.recv()
            response = loads(response_string)

            if response.get('error'):
                raise Exception(response.get('message'))

            if event:
                await self.event_manager.emit('connect')

            return response
        except Exception as error:
            await self.event_manager.emit('disconnect')

            if str(error) == 'no close frame received or sent':
                raise Exception('Cannot get answer from server')
            else:
                raise error

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
        self.distributors = {}

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
        
        if body["distributorID"] is not None:
            return response
        
        if type(response) == dict and response.get('distribute', False):
            _distributorID = response.get('distributorID')
            response = None

            self.distributors[_distributorID] = {
                'documents': [],
                'residue': 1
            }

            while self.distributors[_distributorID].get('residue') > 0:
                distributor = self.distributors.get(_distributorID)
                response = self.req(path, method, { 'distributorID': _distributorID})

                distributor['documents'].extend(response.get('data', []))
                distributor['residue'] = response.get('residue', 0)

            
            documents = self.distributors[_distributorID].get('documents')

            del self.distributors[_distributorID]
            return documents
        
        return response

    def set_collection(self, collection: str = 'test'):
        self.collection = collection
        return self

    async def count(self, filter: object = {}):
        filter['$only'] = ['']
        return len(await self.search(filter))

    async def create(self, *data):
        return await self._create(data)

    async def _create(self, data, distributorID=None):
        if self.db.client.protocol == 'ws':
            data = await self.db.client.websocket_request(
                self.db.database, self.collection, 'create', {}, {'data': data, 'distributorID': distributorID if distributorID is not None else '' })
            if len(data.get('distributorID')) == 0 and distributorID is None:
                    return data.get('data')
            elif distributorID is not None:
                    return data
            else:
                _distributorID = data.get('distributorID')
                self.distributors[_distributorID] = {
                    'documents': [],
                    'residue': 1
                }

                while self.distributors[_distributorID].get('residue') > 0:
                    distributor = self.distributors.get(_distributorID)
                    response = await self._create([], _distributorID)

                    distributor['documents'].extend(response.get('data', []))
                    distributor['residue'] = response.get('residue', 0)

                
                documents = self.distributors[_distributorID].get('documents')

                del self.distributors[_distributorID]
                return documents
                

        return self.req('create', 'post', {
            'data': data,
            'distributorID': distributorID
        })

    async def search(self, filter={}, distributorID = None):
        if self.db.client.protocol == 'ws':
            data = await self.db.client.websocket_request(self.db.database, self.collection, 'search', filter, {'distributorID': distributorID if distributorID is not None else '' })
            
            if len(data.get('distributorID')) == 0 and distributorID is None:
                    return data.get('data')
            elif distributorID is not None:
                    return data
            else:
                _distributorID = data.get('distributorID')
                self.distributors[_distributorID] = {
                    'documents': [],
                    'residue': 1
                }

                while self.distributors[_distributorID].get('residue') > 0:
                    distributor = self.distributors.get(_distributorID)
                    response = await self.search({}, _distributorID)

                    distributor['documents'].extend(response.get('data', []))
                    distributor['residue'] = response.get('residue', 0)

                
                documents = self.distributors[_distributorID].get('documents')

                del self.distributors[_distributorID]
                return documents

        return self.req('search', 'post', {
            'filter': filter,
            'distributorID': distributorID
        })

    async def search_one(self, filter={}):
        filter['$max'] = 1

        response = await self.search(filter)
        if len(response) == 0:
            return None

        return response[0]

    async def delete(self, filter={}, distributorID = None):
        if self.db.client.protocol == 'ws':
            data = await self.db.client.websocket_request(self.db.database, self.collection, 'delete', filter, {'distributorID': distributorID if distributorID is not None else ''})
            
            if len(data.get('distributorID')) == 0 and distributorID is None:
                    return data.get('data')
            elif distributorID is not None:
                    return data
            else:
                _distributorID = data.get('distributorID')
                self.distributors[_distributorID] = {
                    'documents': [],
                    'residue': 1
                }

                while self.distributors[_distributorID].get('residue') > 0:
                    distributor = self.distributors.get(_distributorID)
                    response = await self.delete({}, _distributorID)

                    distributor['documents'].extend(response.get('data', []))
                    distributor['residue'] = response.get('residue', 0)

                
                documents = self.distributors[_distributorID].get('documents')

                del self.distributors[_distributorID]
                return documents

        return self.req('', 'delete', {
            'filter': filter,
            'distributorID': distributorID
        })

    async def update(self, filter={}, update={}, distributorID = None):
        if self.db.client.protocol == 'ws':
            data = await self.db.client.websocket_request(self.db.database, self.collection, 'update', filter, {'data': [update], 'distributorID': distributorID if distributorID is not None else ''})
            
            if len(data.get('distributorID')) == 0 and distributorID is None:
                    return data.get('data')
            elif distributorID is not None:
                    return data
            else:
                _distributorID = data.get('distributorID')
                self.distributors[_distributorID] = {
                    'documents': [],
                    'residue': 1
                }

                while self.distributors[_distributorID].get('residue') > 0:
                    distributor = self.distributors.get(_distributorID)
                    response = await self.update({}, {}, _distributorID)

                    distributor['documents'].extend(response.get('data', []))
                    distributor['residue'] = response.get('residue', 0)

                
                documents = self.distributors[_distributorID].get('documents')

                del self.distributors[_distributorID]
                return documents

        return self.req('', 'patch', {
            'distributorID': distributorID,

            'data': {
                'filter': filter,
                'update': update
            }
        })

    async def instant_update(self, filter={}, update={}, distributorID = None):
        if self.db.client.protocol == 'ws':
            data = await self.db.client.websocket_request(self.db.database, self.collection, 'instantUpdate', filter, {'data': [update], 'distributorID': distributorID if distributorID is not None else ''})
            
            if len(data.get('distributorID')) == 0 and distributorID is None:
                    return data.get('data')
            elif distributorID is not None:
                    return data
            else:
                _distributorID = data.get('distributorID')
                self.distributors[_distributorID] = {
                    'documents': [],
                    'residue': 1
                }

                while self.distributors[_distributorID].get('residue') > 0:
                    distributor = self.distributors.get(_distributorID)
                    response = await self.instant_update({}, {}, _distributorID)

                    distributor['documents'].extend(response.get('data', []))
                    distributor['residue'] = response.get('residue', 0)

                
                documents = self.distributors[_distributorID].get('documents')

                del self.distributors[_distributorID]
                return documents

        return self.req('', 'put', {
            'distributorID': distributorID,
            'data': {
                'filter': filter,
                'update': update
            }
        })

    async def search_or_create(self, filter, create={}):
        if self.db.client.protocol == 'ws':
            data = await self.db.client.websocket_request(self.db.database, self.collection, 'searchOrCreate', filter, {'data': [create]})
            return data.get('data')

        return self.req('searchOrCreate', 'post', {
            'filter': filter,
            'data': create
        })
