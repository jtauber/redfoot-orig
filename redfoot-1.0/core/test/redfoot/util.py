from redfoot import util
from redfoot.util import encode_URI, encode_attribute_value, encode_character_data

def run():
    passed, info = (1, '')

    url = "http://test.com:8000/foo#bar"
    expected = "http%3a//test.com%3a8000/foo%23bar"
    # with one arg passed
    if encode_URI(url)!=expected:
        passed, info = (0, info + 'encode_URI failed -- %s!=%s\n' % (encode_URI(url, safe='/'), expected))
    # with one two args passed        
    if encode_URI(url, safe='/')!=expected:
        passed, info = (0, info + 'encode_URI failed -- %s!=%s\n' % (encode_URI(url, safe='/'), expected))

    val = """&"<'"""
    expected = """&amp;&quot;&lt;'"""
    if encode_attribute_value(val)!=expected:
        passed, info = (0, info + 'encode_attribute_value failed -- %s!=%s\n' % (encode_attribute_value(val), expected))        

    val = """&<"""
    expected = """&amp;&lt;"""
    if encode_character_data(val)!=expected:
        passed, info = (0, info + 'encode_attribute_value failed -- %s!=%s\n' % (encode_character_data(val), expected))     
    
    return (passed, info)
