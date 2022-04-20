from typing import NoReturn
import sublime
import sublime_plugin
import os
from os import path

from .core import shell
from .core.typing import Dict, Optional, List, Generator, Tuple

MSG = f'Use the ":" or "$" prefix can make new shell like ":command xxx"'
PANEL_NAME = 'cps'
OUTPUT_PANEL_NAME = f'output.{ PANEL_NAME }'

COMMAND_NAME = {
    "update":f"{PANEL_NAME}_update_panel"
}

# 记录最近一次关闭的窗体名称
LAST_ACTIVE_PANEL = None
RUN_IN_NEW_WINDOW_PREFIX = [':', "$"]
LINE_END = f'\n[done by {PANEL_NAME}]'

# panel 默认配置
DEFAULT_PANEL_SETTINGS = {
    "auto_indent": False,             # 是否自动缩进
    "draw_indent_guides": False,      #
    "draw_unicode_white_space": None, #
    "draw_white_space": None,         #
    "fold_buttons": True,             #
    "gutter": False,                  #
    "is_widget": True,                #
    "line_numbers": False,            #
    "lsp_active": True,               #
    "margin": 0,                      #
    "match_brackets": False,          #
    "rulers": [],                     #
    "scroll_past_end": True,          #
    "show_definitions": False,        #
    "tab_size": 4,                    #
    "translate_tabs_to_spaces": True, #
    "word_wrap": False,               #
}


def ensure_panel(panel_name:str) -> sublime.View:
    window = sublime.active_window()
    panel = window.find_output_panel(panel_name)

    try:
        if panel:
            return panel
        else:
            return create_panel(panel_name)
    except Exception as err:
        return window.find_output_panel('exec')

def create_panel(panel_name:str) -> Optional[sublime.View]:
    global DEFAULT_PANEL_SETTINGS

    window = sublime.active_window()
    panel = window.create_output_panel(panel_name)
    settings = panel.settings()

    [settings.set(key,value) for key, value in DEFAULT_PANEL_SETTINGS]
    return panel


def plugin_loaded():
    global PANEL_NAME
    print(f'{PANEL_NAME} run command 加载成功')
    ensure_panel(PANEL_NAME)


class CpsUpdatePanelCommand(sublime_plugin.TextCommand):
    """
    @Description 更新 名为 output.testt 的panel窗体数据。
    @example
    ```python
    window = sublime.active_window()
    window.run_command('testt_update_panel', {
        "panel_name":panel_name,
        'data':command_res
        })
    ```
    """
    def run(self, edit: sublime.Edit, panel_name:str, data:str):
        global OUTPUT_PANEL_NAME

        window = sublime.active_window()
        panel = window.find_output_panel(panel_name)

        if not panel: return print(f'无法找到 {panel_name} 窗口')

        panel.set_read_only(False)
        panel.replace(edit, sublime.Region(0, panel.size()), data)
        panel.set_read_only(True)

        window.run_command('show_panel', { 'panel':OUTPUT_PANEL_NAME })

class CpsRunCommandsCommand(sublime_plugin.TextCommand):
    """
    @Description 通过快捷键可以在任何时候快捷的输入一些简单的shell命令，不支持大量数据处理和需要交互的指令
    @example
    ```bash
    # 调出输入框
    alt + f1

    # 简单的指令
    npm -v & node -v & yarn -v

    # 简单的安装指令
    npm i -D @types/node12

    # 需要交互的命令前面添加 "$" 或者 ":"
    $npm init
    :npm init
    ```
    """
    def run(self, edit: sublime.Edit):
        window = sublime.active_window()
        panel_name = window.active_panel()

        CWD = os.path.dirname(self.view.file_name())
        print("cwd: ", CWD)


        if panel_name:
            window.run_command('hide_panel', {'panel':panel_name})
        else:
            window.show_input_panel(
                caption=MSG,
                initial_text="",
                on_done=self.on_done,
                on_change=self.on_change,
                on_cancel=self.on_cancel
            )

    def on_done(self, user_input: str):
        global PANEL_NAME
        sublime.set_timeout_async(self.run_command(user_input, PANEL_NAME))

    def on_change(self, text: str):
        pass

    def on_cancel(self):
        pass

    def run_command(self, user_input:str, panel_name:str):
        global RUN_IN_NEW_WINDOW_PREFIX, LINE_END, COMMAND_NAME

        cwd = os.path.dirname(self.view.file_name())

        run_on_new_window = False

        if user_input[0][0] in RUN_IN_NEW_WINDOW_PREFIX:
            run_on_new_window = pause = True
            commands = str(user_input[1:]).split(' ')
        else:
            commands = str(user_input).split(' ')

        command_res = shell.run_command(commands, shell=run_on_new_window, pause=run_on_new_window, cwd=cwd)

        if command_res:
            command_res += LINE_END
            sublime.active_window().run_command(COMMAND_NAME['update'], {
                "panel_name":panel_name,
                'data':command_res
                })



class CpsPanelToggleCommand(sublime_plugin.TextCommand):
    """
    @Description 显示最近一次关闭的消息窗口
    @example
    ```bash
    # 显示/隐藏 最近一次的panel
    alt + f2
    ```
    """
    def run(self, edit: sublime.Edit):
        global LAST_ACTIVE_PANEL, OUTPUT_PANEL_NAME
        active_panel = sublime.active_window().active_panel()
        window = sublime.active_window()

        if active_panel:
            LAST_ACTIVE_PANEL = active_panel
            if active_panel:
                window.run_command('hide_panel', {'panel':active_panel})

        else:
            if LAST_ACTIVE_PANEL in [None, 'console']:
                panel_name = OUTPUT_PANEL_NAME
            else:
                panel_name = LAST_ACTIVE_PANEL

            window.run_command('show_panel', {'panel':panel_name})
