# -*- coding: utf-8 -*-
#
# @Author: CPS
# @email: 373704015@qq.com
# @Date: 2022-04-25 09:18:42.957356
# @Last Modified by: CPS
# @Last Modified time: 2022-04-25 09:18:42.958260
# @file_path "W:\CPS\IDE\SublimeText\JS_SublmieText\Data\Packages\cps_run_commands\core"
# @Filename "historyManager.py"
# @Description: 功能描述
#
import os

from typing import *
from dataclasses import *
from os import path

class History:
    def __init__(self, file_path:str, max_count:int=10):
        self.file_path = file_path
        self.max_count = max_count - 1
        self.data = []

        self.check_file_path()
        print('init History: ', self.data)

    def check_file_path(self):
        try:
            if not os.path.exists(self.file_path):
                with open(self.file_path, 'w') as f:
                    f.write("")
            else:
                with open(self.file_path, 'r') as f:
                    self.data = f.read().split('\n')
            return self

        except Exception as err:
            raise FileExistsError

    def add(self, histroy:Any):
        while len(self.data) > self.max_count:
            self.data.pop()

        self.data.insert(0, histroy)
        self.dump()
        return self

    def dump(self):
        with open(self.file_path, 'w') as f:
            f.write('\n'.join(self.data))
        return self

    def __str__(self):
        return ','.join(self.data)

    # def __getitem__(self, target):
    #     if isinstance(target, int) and target -1 <= self.max_count:
    #         return self.data[target - 1]

if ( __name__ == "__main__"):
    import sys
    print(sys.path)

