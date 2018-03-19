import re

def compiled_image_regex(image_text):
    text = ".*?{}.*?".format(image_text)
    regex = re.compile(text)
    return regex
