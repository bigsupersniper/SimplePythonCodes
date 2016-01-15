# -*- coding: utf-8 -*-

import os

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

def is_git_dir(d):
    if os.path.isdir(d):
        if os.path.exists(os.path.join(d , ".git")):
            return True
    return False

def is_remote_git_dir(d):
    if os.path.isdir(d):
        if os.path.exists(os.path.join(d , ".git")):
            cfg = os.path.join(d , ".git" , "config")
            if os.path.exists(os.path.join(d , ".git" , "config")):
                with open(cfg , 'r') as f:
                    for line in f:
                        if '[remote "origin"]' in line:
                            return True
    return False

def git_pull_child_dir(d):
    cwd = os.getcwd()
    if os.path.isdir(d):
        remote_gits = list_child_dir(d , expression=is_remote_git_dir)
        for git in remote_gits:
            os.chdir(git)
            print '\ngit pull' , git
            os.system('git pull')

if __name__ == '__main__':
    d = raw_input('please input git repository location!\n')
    while True :
        d = str(d)
        if os.path.isdir(d):
            git_pull_child_dir(d)
            break
        else:
            d = raw_input('please input git repository location!\n')
