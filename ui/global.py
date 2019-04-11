import codecs
import os


def global_var(request):
    content = dict()
    serial_number_file = os.path.dirname(__file__) + '/device-serial-number.txt'

    try:
        with codecs.open(serial_number_file, encoding="utf8") as file:
            content['dev_serial_number'] = file.read().strip()
    except:
        content['dev_serial_number'] = "N/A"

    return content
