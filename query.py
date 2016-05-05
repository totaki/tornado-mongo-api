FIND = 'find'
INSERT = 'insert'
UPDATE = 'update'

def validate_insert(func):
    def wrapper(default=None, blank=True):
        def wrapped(key, value):
            _ = value

            if not value and (not default or not blank):
                error = 'Value {} must be present'.format(key)
                raise ValueError(error)

            if not value and default:
                _ = default
            
            if value:
                _ = func(value)

            return _
        return wrapped
    return wrapper


@validate_insert
def STR(value):
    return str(value)


@validate_insert
def INT(value):
    return int(value)
