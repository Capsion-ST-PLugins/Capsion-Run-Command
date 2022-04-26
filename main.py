from typing import NoReturn
import sublime
import sublime_plugin
import os
from os import path

from .core import shell
from .core.typing import Dict, Optional, List, Generator, Tuple
from .core.history import History


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

HISTORY_PACKAGE_PATH:str = path.join(sublime.packages_path(), __package__)
HISTORY_LOCAL_FILE:str = path.join(sublime.packages_path(), 'User', f'.{__package__}.histroy')

MSG_SELECTIONS_HELP = 'Press "Enter" to enter a custom command'
MSG_SELECTIONS_TITLE = '0.  input custom command'

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
    global PANEL_NAME, HISTORY
    print(f'{PANEL_NAME} run command 加载成功')
    ensure_panel(PANEL_NAME)
    HISTORY = History(HISTORY_LOCAL_FILE)

class CpsUpdatePanelCommand(sublime_plugin.TextCommand):
    """
    @Description 的panel窗体数据。

    - param panel_name :{str} "panel_name":panel_name,

    returns `{type}` {description}

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

    # "$" 或者 ":" 前缀，调用新的shell窗口运行指令
    # 后续cmd窗口会等待15秒后自动关闭
    $npm init

    # 后续cmd窗口需要用户按任意键才能关闭
    :npm init
    ```
    """
    def run(self, edit: sublime.Edit):
        global HISTORY,MSG_SELECTIONS_TITLE

        window = sublime.active_window()
        panel_name = window.active_panel()

        selection_with_index = [ f'{index + 1}.  {HISTORY.data[index]}' for index in range(len(HISTORY.data))]

        if panel_name:
            window.run_command('hide_panel', { 'panel':panel_name })
        else:
            self.show_selection([MSG_SELECTIONS_TITLE] + selection_with_index)

    def show_selection(self, items:List[str]):
        """
        @Description 让用户选择是自己输入还是历史记录

        - param items :{List[str]} {description}
        """
        global MSG_SELECTIONS_HELP
        sublime.active_window().show_quick_panel(
            items=items,
            on_select=self.on_select,
            flags=0,
            selected_index=-1,
            placeholder=MSG_SELECTIONS_HELP
            )

    def show_input_panel(self, placeholder:str=""):
        """
        @Description 输入自定义命令

        - param placeholder :{str} 占位符
        """
        global MSG
        sublime.active_window().show_input_panel(
            caption=MSG,
            initial_text=placeholder,
            on_done=self.on_done,
            on_change=self.on_change,
            on_cancel=self.on_cancel
        )

    def on_select(self, user_select_index:int):
        # custom input
        if user_select_index == -1:
            return
            # self.show_input_panel()

        elif user_select_index == 0:
            self.show_input_panel()

        else:
            self.on_done(HISTORY.data[user_select_index - 1])

    def on_done(self, user_input:int):
        # print("user_input: ", user_input)
        global PANEL_NAME
        sublime.set_timeout_async(self.run_command(user_input, PANEL_NAME))

    def on_change(self, text: str):
        pass

    def on_cancel(self):
        pass

    def run_command(self, user_input:str, panel_name:str=None):
        global RUN_IN_NEW_WINDOW_PREFIX, LINE_END
        global HISTORY, COMMAND_NAME
        global PANEL_NAME

        HISTORY.add(user_input)
        cwd = os.path.dirname(self.view.file_name())

        # run in new shell window
        if user_input[0][0] in RUN_IN_NEW_WINDOW_PREFIX:
            if user_input[0][0] == ':':
                pause = True

            if user_input[0][0] == '$':
                pause = 5

            commands = str(user_input[1:]).split(' ')
            shell.run_command(commands, shell=True, pause=pause, cwd=cwd)

            return

        # running in sublime exec
        commands = str(user_input).split(' ')
        res = shell.run_command(commands, shell=False, pause=False, cwd=cwd)

        if res['success']:
            command_res = res['res']
        else:
            command_res = res['err']

        # command_res += LINE_END
        command_res = f'work_floder: {cwd}\n\n{command_res}\n{LINE_END}'
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
