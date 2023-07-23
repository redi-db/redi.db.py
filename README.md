# Redi.DB.py

Library for working with RediDB in Python

**Connect and creating collection:**

```python
from redi_db import RediDB
client = RediDB({
    'login': 'root',
    'password': 'root',

    'ip': 'localhost',
    'useSSL': False, # Use True if your protocol uses https
    'port': 5000
})

exampleDatabase = client.set_database('exampleDatabase')
exampleCollection = exampleDatabase.invoke().set_collection('exampleCollection')
```

<br><br>
**Adding to database**

```py
exampleCollection.create({
    'id': 1
})

# It works just like search_one, but at the same time if there is no search_one it automatically creates it
# exampleCollection.search_or_create(filter, create_data)
exampleCollection.search_or_create({}, {
    'id': 2
}, {
    'id': 2,
    'isExampleValue': True
})
```

<br><br>
**Search**

```py
exampleCollection.search({}) # It will give out all the data
```

<br><br>
**Search one**

```py
# searchOne already outputs a data object from the database
exampleCollection.search_one({
    'id': 1
})
```

<br><br>
**Deleting**

```py
exampleCollection.delete({}) # Filter, if empty drop all collection
```

<br><br>
**Updating**

```py
# Updating elements by filter
# exampleCollection.update(filter, update)
exampleCollection.update({'id': 1}, {
      'id': 1
  },

  {
      'isExampleValue': False
  }
)
```

```py
# Instant updating of elements by filter
# exampleCollection.update(filter, update)
exampleCollection.instant_update({'id': 1}, {
      'id': 1
  },

  {
      'isExampleValue': False
  }
)
```
