# Redi.DB.py
Library for working with RediDB in Python

**Connect and creating collection:**
```python
from redi_db import RediDB
db = RediDB({
    'login': 'root',
    'password: 'root',
    
    'ip': 'localhost',
    'port': 5000
})#.test_connect()

db.test_connect()
exampleCollection = db.add_database('ExampleProject').set_collection('exampleCollection')
```
<br><br>
**Adding to database**
```py
# exampleCollection.create(key, data)
# The key can be null, in which case the database will automatically generate _id.
# data can be either an array (for example, to fill many elements in one query) or just an object

exampleAnswer = exampleCollection.create(None, {
    'id': 1
})

exampleAnswer2 = exampleCollection.create("user_2", {
    'id': 2
})

exampleAnswer3 = exampleCollection.create(None, [
    {
        'id': 3
    }
])

# If you want to add many items to the database in one query, you can also give them key (_id)
exampleAnswer4 = exampleCollection.create(None, [
    {
        '_key': 'user_4',
        'id': 4
    },

    {
        '_key': 'user_5',
        'id': 5
    }
])
    
# It works just like search_one, but at the same time if there is no search_one it automatically creates it
# exampleCollection.find_or_create(key, filter, toCreateData)
exampleCollection.find_or_create(None, {
    'id': 50
}, {
    'id': 50,
    'isExampleValue': True
})
```

<br><br>
**Search**
```py
search = exampleCollection.search() # It will give out all the data

# It will give out all the data, but with the filter applied.
search1 = exampleCollection.search({
    'id': 1
})

search2 = exampleCollection.search({
    '_id': 'user_4' # _id = key
})
```

<br><br>
**Search one**
```py
# searchOne already outputs a data object from the database
searchOne = exampleCollection.search_one({
    'id': 1
})
```

<br><br>
**Deleting**
```py
_delete = exampleCollection.delete("user_4") # Only key (_id)
_delete2 = exampleCollection.delete(None, {
    'id': 5
}) # Filters

_deleteAll = exampleCollection.delete(None)
```

<br><br>
**Updating**
```py
# Global updating
# exampleCollection.update(key, updateData)

# Updating one or more elements by filter
# exampleCollection.update_one(key, filter, update) # Filter can be null
exampleCollection.update_one(None, {
      'id': 1
  },

  {
      'id': 20
  }
))
```
