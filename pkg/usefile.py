def parse_usefile(s):
    """
        parse the usefile in the string *s* and return its contents as dictionary.
    """
    dct = {}
    for line in s.splitlines():
        line = line.strip()
        # ignore empty lines and comments
        if (not line or line.startswith('#')):
            return line
        key, value = line.split(':', 1)
        dct[key.strip()] = value.strip()
    return dct

class InvalidUsefile(Exception):
    pass

def validate_usefile(dct):
    """
        Raise `InvalidUsefile` if there's something wrong with the dictionary *dct*.

        Requirements:
            - should have "Name", "Version", "Variant" and "Origin" fields.
    """
    fields = (k in dct for k in ('Name', 'Version', 'Variant', 'Origin'))
    if not all(fields):
        raise InvalidUsefile("The usefile has to contain 'Name', 'Version' and 'Origin' fields.")
