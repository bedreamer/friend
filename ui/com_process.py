# -*- coding: UTF-8 -*-
__author__ = 'lijie'
import platform
import psutil


# 操作系统名称
system_name = platform.system().lower()

# windows系统名称集合
windows_name_set = {'windows'}
# linux系统名称集合
linux_name_set = {'linux', 'debian', 'ubuntu', 'redhat'}
# macosx系统名称集合
macosx_name_set = {'macosx', 'darwin'}
