import sys
import subprocess
from subprocess import Popen, PIPE
import platform
import os

from typing import *

COMMANDS = {
    'node':['node','-v'],
    'npm':['npm','-v'],
    'yarn':['yarn','-v'],
    'ts-node':['ts-node','-v'],
    "tsc":['tsc', '--version']
}

def check_command(target:str) -> bool:
    res = False
    global COMMANDS
    if target in COMMANDS.keys():
        res = run_command(COMMANDS[target]).strip()
        print(res)
    return True if res else False

class TRun_command(TypedDict):
    success:bool
    res:Any
    err:Any


def run_command(
    command:list,
    strBuffer:str=None,
    shell:bool=False,
    decode:str='utf-8',
    cwd=None,
    pause:bool=False) -> TRun_command:
    """
    @Description {description}

    - param command   :{list} 通过列表将需要输入的shell命令传入
    - param strBuffer :{str}  需要传输的数据
    - param shell     :{bool} 是否开启一个独立的shell执行指令
    - param decode    :{str}  对返回的结果指定编码方式
    - param pause     :{bool} 是否暂停
    - panam cwd       :{str}  指定工作目录

    @example
    ```python
    command = ['node', '-v']

    # 简单单向指令
    run_command(command)

    # 复杂交互指令
    res = run_command(command, decode='gb2312', shell=True, pause=True)
    if res['success']:
        print(res['res'])
    else:
        print(res['err'])
    ```
    @returns `{str}` {description}

    """

    os_type = platform.system().lower()
    if os_type == 'windows':
        new_shell = 'cmd'
    else:
        new_shell = 'bash'

    # 指定工作目录
    if cwd: os.chdir(cwd)
    try:
        # run with inside
        if shell:
            is_pause = ' & pause' if pause else ''
            _command = f'start {new_shell} /c \"{" ".join(command)}{is_pause}\"'
            Popen(_command, shell=True)
            # return True
            return { "success":True }

        # run with outside
        child_process = Popen(command, stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=True)

        # 过来一遍 strBuffer
        if strBuffer != None:
            if isinstance(strBuffer, str):
                strBuffer = strBuffer.encode(decode)

        # 执行 command
        stdout, stderr = child_process.communicate(input=strBuffer, timeout=10000)

        if stdout:
            if decode:
                return { "res":stdout.decode(decode), "success":True }
            return { "res":stdout, "success":True }
            # return stdout.decode('utf-8')

        if stderr:
            # raise Exception('run_command() 结果出错:', stderr)
            print('run_command() 结果出错:', stderr)
            return { "err":stderr, "success":False }

        return { "success":False, "err":"nothing change" }

    except Exception as err:
        print('run_command() 运行出错:', command)
        # raise Exception('run_command() 运行出错:', command)
        return { "err":err, "success":False }

if ( __name__ == "__main__"):
    res = run_command(['npm', 'init'], decode='gb2312', shell=True, pause=True, cwd="i:/SteamLibrary")

    # res = run_command(['npm', 'i', '-D', '@types/node12'], decode='gb2312')
    # res = subprocess.Popen('start cmd /c \"npm init\"', shell=True)
    # res = subprocess.Popen('npm -v')

    print(res)
