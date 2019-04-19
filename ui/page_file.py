# -*- coding: utf8 -*-
from django.urls import *
from django.shortcuts import render
from django.http import *
from django.utils.datastructures import MultiValueDictKeyError
import codecs


def file_readline_iter(full_path):
    with codecs.open(full_path, encoding='utf8') as file:
        while True:
            line = file.readline()
            if line:
                yield line
            else:
                raise StopIteration


def save_file(request, path):
    upload = request.POST['file']
    with codecs.open(path, mode='w', encoding='utf8') as file:
        file.write(upload)


def show_file_context(request):
    try:
        path = request.GET['path']
        return render(request, "02-文本编辑器/01-查看文件.html", {'file_readline_iter': file_readline_iter(path)})
    except MultiValueDictKeyError as e:
        return render(request, "02-文本编辑器/03-文件编辑器错误.html", {'error': e})
    except FileNotFoundError as e:
        return render(request, "02-文本编辑器/03-文件编辑器错误.html", {'error': e})


def view_file_context(request):
    try:
        path = request.GET['path']
        return render(request, "02-文本编辑器/00-只读文件.html", {'file_readline_iter': file_readline_iter(path)})
    except MultiValueDictKeyError as e:
        return render(request, "02-文本编辑器/03-文件编辑器错误.html", {'error': e})
    except FileNotFoundError as e:
        return render(request, "02-文本编辑器/03-文件编辑器错误.html", {'error': e})



def edit_file_context(request):
    try:
        path = request.GET['path']
        if request.method == 'GET':
            return render(request, "02-文本编辑器/02-编辑文件.html", {'file_readline_iter': file_readline_iter(path)})
        else:
            save_file(request, path)
            return HttpResponseRedirect(reverse('file_reader') + "?path=" + path)
    except MultiValueDictKeyError as e:
        return render(request, "02-文本编辑器/03-文件编辑器错误.html", {'error': e})
    except FileNotFoundError as e:
        return render(request, "02-文本编辑器/03-文件编辑器错误.html", {'error': e})



urlpatterns = [
    path('view/', view_file_context, name="file_viewer"),
    path('read/', show_file_context, name="file_reader"),
    path('edit/', edit_file_context, name="file_editor"),
]
urls = (urlpatterns, 'file', 'file')
