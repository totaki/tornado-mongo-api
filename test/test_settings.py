from query import *


test_collection = {
    INSERT: {
        'field_1': STR(),
        'field_2': STR(blank=False)
    },
    FIND: {
        'field_1': find_text,
        'field_2': find_cap
    },
    UPDATE : {
        'field_1': lambda key, value: {'$set': {key: value}}
    }
}