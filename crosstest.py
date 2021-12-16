#!/usr/bin/env python3

import re
import os
import sys
import argparse
import subprocess
from tester import main as tester

########################################################################
OTHER_REPOS_DIR = 'crosstest_repos'
ALLOWED_PROG_NAMES = { 'task.py', 'prog.py' }
IGNORED_DIRS = [ '20210909', '20210916' ]
REPOS = [
  {
    "owner": "Дарья Озерова",
    "group": "321",
    "url": "https://github.com/OzerovaDaria/pythonprac"
  },
  {
    "owner": "Павел Шибаев",
    "group": "321",
    "url": "https://git.cs.msu.ru/s02190248/pythonprac"
  },
  {
    "owner": "Вениамин Арефьев",
    "group": "321",
    "url": "https://github.com/Veniamin-Arefev/pythonprac-2021"
  },
  {
    "owner": "Иван Ушаков",
    "group": "321",
    "url": "https://git.cs.msu.ru/s02190226/pythonprac"
  },
  {
    "owner": "Дмитрий Хасанов",
    "group": "321",
    "url": "https://git.cs.msu.ru/s02190234/pythonprac2021"
  },
  {
    "owner": "Илья Савицкий",
    "group": "321",
    "url": "https://github.com/ipsavitsky/pythonprac"
  },
  {
    "owner": "Александр Колесников",
    "group": "321",
    "url": "https://git.cs.msu.ru/s02190290/python-prac-2021"
  },
  {
    "owner": "Александр Фролов",
    "group": "321",
    "url": "https://github.com/sanyavertolet/pythonprac"
  },
  {
    "owner": "Егор Князев",
    "group": "321",
    "url": "https://github.com/KH9IZ/PythonPrac"
  },
  {
    "owner": "Ривзан Зайдуллин",
    "group": "321",
    "url": "https://git.cs.msu.ru/s02190101/pythonprac-2021"
  },
  {
    "owner": "Юрий Лебединский",
    "group": "321",
    "url": "https://git.cs.msu.ru/s02190141/pythonprac-2021"
  },
  {
    "owner": "Илья Федоренко",
    "group": "321",
    "url": "https://github.com/FluFFka/python-prac"
  },
  {
    "owner": "Дмитрий Стамплевский",
    "group": "321",
    "url": "https://github.com/stamplevskiyd/pythonprac-2021"
  },
  {
    "owner": "Геннадий Шутков",
    "group": "321",
    "url": "https://github.com/gen-gematogen/pythonprac"
  },
  {
    "owner": "Максим Порывай",
    "group": "321",
    "url": "https://git.cs.msu.ru/s90190054/pythonprac-2021"
  },
  {
    "owner": "Арий Оконишников",
    "group": "321",
    "url": "https://github.com/Uberariy/pythonprac"
  },
  {
    "owner": "Юлия Задорожная",
    "group": "321",
    "url": "https://git.cs.msu.ru/s02190029/prakpython"
  },
  {
    "owner": "Владислав Рубцов",
    "group": "321",
    "url": "https://git.cs.msu.ru/s02190700/pythonprac"
  },
  {
    "owner": "Дарья Скворцова",
    "group": "321",
    "url": "https://git.cs.msu.ru/s02180534/pythonprac2021"
  },
  {
    "owner": "Виктор Панферов",
    "group": "321",
    "url": "https://git.cs.msu.ru/s02190692/python-prac"
  }
]
########################################################################

class Logger:
    def __init__(self):
        self.debugging = False
        self.colors = True

    def info(self, *args, **kwargs):
        if self.colors: print('[\033[32minfo\033[0m] ', *args, **kwargs)
        else: print('[info] ', *args, **kwargs)

    def warning(self, *args):
        if self.colors: print('[\033[93mwarning\033[0m] ', *args)
        else: print('[warning] ', *args)

    def debug(self, *args):
        if self.debugging:
            if self.colors: print('[\033[96mdebug\033[0m] ', *args)
            else: print('[debug] ', *args)

    def error(self, *args):
        if self.colors: print('[\033[31mERROR\033[0m] ', *args)
        else: print('[ERROR] ', *args)

    def abort(self, *args, exitCode=1):
        if self.colors: print('[\033[91mCRITICAL\033[0m] ', *args)
        else: print('[CRITICAL] ', *args)
        exit(exitCode)

    def debugOn(self): self.debugging = True
    def colorsOff(self): self.colors = False
log = Logger()

########################################################################

argParser = argparse.ArgumentParser()
argParser.add_argument('-w', '--who', default='', type=str,
        help='Names separated with ",". People who you want to take tests from')
# argParser.add_argument('-m', '--me', default='', type=str,
        # help='Your name. It will prevent tester from downloading your own repo with --saveall')
argParser.add_argument('--saveall', action='store_true',
        help='Saves all repos to your drive')
argParser.add_argument('--debug', action='store_true',
        help='Print debug output')
argParser.add_argument('--nocolors', action='store_true',
        help='Disabels colors in logger')
# argParser.add_argument('--upgrade', action='store_true',
        # help='Redownloads repos')
argParser.add_argument('repo', default='.', type=str,
        help='Path to repository for test')

########################################################################

args = argParser.parse_args()
args.who = [ *map(str.strip, args.who.split(',')) ]
ownrepo = args.repo

#######################

if not os.path.isdir(ownrepo):
    log.critical('Path to own repo is not valid')

if args.debug: log.debugOn()
if args.nocolors: log.colorsOff()

if not sys.stdout.isatty(): log.colorsOff()

log.debug(args)

#######################

if args.saveall:
    choosenRepos = REPOS
else:
    choosenRepos = []
    for who in args.who:
        chosen = None
        bestMatch = ''
        regex = f'(?:{"|".join(who.split())})'

        for repo in REPOS:
            match = ' '.join(re.findall(regex, repo['owner'], flags=re.I))
            if len(match) == 0: continue
            if len(bestMatch) < len(match):
                chosen = repo
                bestMatch = match
            elif len(bestMatch) == len(match):
                log.warning(f'Same owner name for {who} ({repo["owner"]}), using {chosen["owner"]}')

        if chosen:
            choosenRepos.append(chosen)
        else:
            log.warning('No repo found for', who)

#######################

if os.path.exists(OTHER_REPOS_DIR) and not os.path.isdir(OTHER_REPOS_DIR):
    log.abort(f'Unable to open {OTHER_REPOS_DIR}: file with this name already exists')
else:
    log.info('Updating REPOS storage')

    uptodate = True

    for repo in choosenRepos:
        repo['dir'] = os.path.join(OTHER_REPOS_DIR, repo['url'].split("/")[3])
        if not os.path.exists(repo['dir']):
            uptodate = False
            subprocess.run(['git', 'clone', repo['url'], repo['dir']])

    if uptodate: log.info('Repos are up to date')

#######################

stat = {
    "ok": 0,
    "error": 0,
    "mismatch": 0,
    "unknown": 0,
}

errorTests = []
mismTests = []

dirs = sorted([ *filter(lambda x: re.match('^2021\d+$', x), os.listdir(ownrepo)) ])
for dir in dirs:
    if dir in IGNORED_DIRS: continue

    condir = os.path.join(ownrepo, dir)
    tasks = sorted([ *filter(lambda x: re.match('^\d+$', x), os.listdir(condir)) ])
    log.debug('condir - ', condir, ':', tasks)

    for task in tasks:
        taskdir = os.path.join(condir, task)
        pyfiles = { *filter(lambda x: re.match('.*\.py$', x), os.listdir(taskdir)) }
        log.debug('taskdi - ', taskdir, ':', pyfiles)

        taskfile = [ *(pyfiles & ALLOWED_PROG_NAMES) ]
        if len(taskfile) == 0:
            log.warning(f'No python program found for {dir}/{task}, skiping...')
            continue
        elif len(taskfile) > 1:
            log.warning(f'Too many python programs to choose from: {taskfile}, using {taskfile[0]}')
        taskfile = os.path.join(ownrepo, dir, task, taskfile[0])

        for repo in choosenRepos:
            testsdir = os.path.join(repo['dir'], dir, task, 'tests')
            log.debug('testdir - ', testsdir)

            if not os.path.exists(testsdir):
                log.warning(f'No tests for {dir}/{task} give by {repo["owner"]}')
            else:
                log.info('='*10)
                log.info(f'Testing {dir}/{task} on {repo["owner"]} tests:')
                log.debug('test on - ', taskfile, testsdir)
                try:
                    res = tester(taskfile, testsdir)
                except Exception as e:
                    log.error('Tester failed to complete test')
                    log.error(e)

                if res == 0:
                    log.info('Tests completed successfully')
                    stat['ok'] += 1
                elif res == 1:
                    log.info('Tests weren\'t completed due to some errors')
                    stat['error'] += 1
                    errorTests.append(': '.join([repo['owner'], os.path.join(dir, task)]))
                elif res == 3:
                    log.info('Tests completed but results are not matching')
                    stat['mismatch'] += 1
                    mismTests.append(': '.join([repo['owner'], os.path.join(dir, task)]))
                else:
                    log.info('Test completed with exit code', res)
                    stat['unknown'] += 1

print('======== Statistic ========')
print('ok:       ', stat['ok'])
print('errors    ', stat['error'])
print('mismatchs:', stat['mismatch'])
print('unknown:  ', stat['unknown'])
print('total:    ', stat['ok'] + stat['error'] + stat['mismatch'] + stat['unknown'])

if len(errorTests):
    print()
    print('========= Errors =========')
    print(*errorTests, sep='\n')

if len(mismTests):
    print()
    print('======== Mismatch ========')
    print(*mismTests, sep='\n')