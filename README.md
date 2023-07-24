# Redi.DB.py

Library for working with RediDB in Python

**Connect and creating collection:**

```python
from redi_db import RediDB
import asyncio

client = RediDB(authorization={
    'login': 'root',
    'password': 'root',
    'ip': 'localhost',
    'port': 5001
}, websocket=True, useSSL=False)


@client.on('connect')
async def on_connect():
    print('Connected!')


@client.on('disconnect')
async def on_disconnect():
    print('Disconnected!')

exampleDatabase = client.set_database('exampleDatabase')
exampleCollection = exampleDatabase.invoke().set_collection('exampleCollection')


async def main():
    await client.connect() # If websocket protocol

    count = await exampleCollection.count()
    print(count)


if __name__ == '__main__':
    asyncio.run(main())
```

<br><br>
**Adding to database**

```py
await exampleCollection.create({
    'id': 1
})

# It works just like search_one, but at the same time if there is no search_one it automatically creates it
# exampleCollection.search_or_create(filter, create_data)
await exampleCollection.search_or_create({
    'id': 2
}, {
    'id': 2,
    'isExampleValue': True
})
```

<br><br>
**Search**

```py
await exampleCollection.search({}) # It will give out all the data
```

<br><br>
**Search one**

```py
# searchOne already outputs a data object from the database
await exampleCollection.search_one({
    'id': 1
})
```

<br><br>
**Deleting**

```py
await exampleCollection.delete({}) # Filter, if empty drop all collection
```

<br><br>
**Updating**

```py
# Updating elements by filter
# exampleCollection.update(filter, update)
await exampleCollection.update({
      'id': 1
  },

  {
      'isExampleValue': False
  })
```

```py
# Instant updating of elements by filter
# exampleCollection.instant_update(filter, new_document)
await exampleCollection.instant_update({
      'id': 1
  },

  {
      'overwrite': True
  }
)
```
