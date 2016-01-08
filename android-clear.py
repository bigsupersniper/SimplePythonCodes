# -*- coding: utf-8 -*-
#run as root

import os
import shutil

def list_child_dir(d , **kwargs):
    child_dirs = []
    if os.path.isdir(d):
        entities = os.listdir(d)
        if(len(entities) > 0):
            for entity in entities:
                fullpath = os.path.join(d , entity)
                if os.path.isdir(fullpath):
                    match = True
                    if kwargs.has_key('expression'):
                        expr = kwargs['expression']
                        if hasattr(expr, '__call__'):
                            match = expr(fullpath)
                    if match == True:
                        child_dirs.append(fullpath)
    return child_dirs

def is_dir_contains_file(d , ext):
    if os.path.isdir(d):
        entities = os.listdir(d)
        if len(entities) > 0 :
            for entity in entities:
                fullpath = os.path.join(d , entity)
                if os.path.isfile(fullpath):
                    _name , _ext = os.path.splitext(fullpath)
                    if (_ext == ext):
                        return True
    return False

def stats_dir_size(d):
    _total = 0L
    if os.path.isdir(d):
        entities = os.listdir(d)
        if len(entities) > 0 :
            for entity in entities:
                _path = d + os.path.sep + entity
                if  os.path.isdir(_path) :
                    _total += stats_dir_size(_path)
                elif  os.path.isfile(_path) :
                    _total += os.path.getsize(_path)
    return _total

def list_child_dir_size(d):
    _dirs = []
    child_dirs = list_child_dir(d)
    if len(child_dirs) > 0 :
        for subdir in child_dirs:
            total = stats_dir_size(subdir)
            _dirs.append((subdir , total))
    return _dirs

def list_filter_system_dir():
    for p in ['/system/app' , '/system/priv-app' , '/system/delapp']:
        print '\n===== {} child empty dir =====\n'.format(p)
        for d in list_child_dir(p , expression = lambda d : stats_dir_size(d) == 0L):
            print d
        print '\n===== {} child dir without apk file =====\n'.format(p)
        for d in list_child_dir(p , expression = lambda d : is_dir_contains_file(d , '.apk') == False):
            print d

def rm_filter_system_dir():
    for p in ['/system/app' , '/system/priv-app' , '/system/delapp']:
        print '\n===== rm {} child empty dir =====\n'.format(p)
        for d in list_child_dir(p , expression = lambda d : stats_dir_size(d) == 0L):
            print d
            shutil.rmtree(d)

def list_or_rm_sdcard_empty_dir(rm = False):
    p = '/storage/emulated/0/'
    if rm :
        print '\n===== rm {} child empty dir =====\n'.format(p)
    else:
        print '\n===== {} child empty dir =====\n'.format(p)
    for d in list_child_dir(p , expression = lambda d : stats_dir_size(d) == 0L):
        print d
        if rm:
            shutil.rmtree(d)
