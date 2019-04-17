import codecs
import os

try:
    uname = os.uname()
    # Linux am335x 3.2.0 #464 Thu Dec 29 15:28:17 CST 2016 armv7l unknown
    # ('Linux', 'am335x', '3.2.0', '#464 Thu Dec 29 15:28:17 CST 2016', 'armv7l')
    system_name = uname[0]
    host_name = uname[1]
    os_version = uname[2]
except:
    system_name = 'windows'
    host_name = 'windows'
    os_version = '10'


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
