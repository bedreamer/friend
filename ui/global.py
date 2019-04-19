import codecs
import os
import ui.com_autocontrol as ac


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

# 当前文件目录
_current_dir = os.path.dirname(__file__)
# 工程目录
project_dir = os.path.dirname(_current_dir)
# 应用程序目录
programs_dir = _current_dir + '/programs'

# 自动控制程序目录
app_autocontrol_dir = programs_dir + '/autocontrol'
# bmsd程序目录
app_bmsd_dir = programs_dir + '/bmsd'
# modbusd程序目录
app_modbusd_dir = programs_dir + '/modbusd'


def global_var(request):
    content = dict()
    serial_number_file = os.path.dirname(__file__) + '/device-serial-number.txt'

    profile = ac.get_current_profile()
    if profile:
        content = dict(content, **profile)

    content['system'] = system_name
    content['host_name'] = host_name
    content['os_version'] = os_version

    content['project_dir'] = project_dir
    content['programs_dir'] = programs_dir
    content['app_autocontrol_dir'] = app_autocontrol_dir
    content['app_bmsd_dir'] = app_bmsd_dir
    content['app_modbusd_dir'] = app_modbusd_dir

    try:
        with codecs.open(serial_number_file, encoding="utf8") as file:
            content['dev_serial_number'] = file.read().strip()
    except:
        content['dev_serial_number'] = "N/A"

    return content
