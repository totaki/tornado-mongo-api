from query import *

test_collection = {
    INSERT: {
        'field_1': STR(),
        'field_2': INT(blank=False)
    },
    FIND: {
        'field_2': int 
    },
    UPDATE : {
        'field_1': lambda key, value: {'$set': {key: value}}
    }
}