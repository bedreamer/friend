import codecs
import os

uname = os.uname()

system_name = uname[0]
host_name = uname[1]
os_version = uname[2]


def global_var(request):
    content = dict()
    serial_number_file = os.path.dirname(__file__) + '/device-serial-number.txt'

    content['system'] = system_name
    content['host_name'] = host_name
    content['os_version'] = os_version

    try:
        with codecs.open(serial_number_file, encoding="utf8") as file:
            content['dev_serial_number'] = file.read().strip()
    except:
        content['dev_serial_number'] = "N/A"

    return content
