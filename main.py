import sublime
import sublime_plugin
import os
from os import path

from .core import shell
from .core import utils
from .core.typing import Optional, List
from .core.history import History


MSG = f'Use the ":" or "$" prefix can make new shell like ":command xxx"'
PANEL_NAME = 'cps'
PLUGIN_NAME = 'cps_run_commands'
DEFAULT_SETTINGS = "cps.sublime-settings"
OUTPUT_PANEL_NAME = f'output.{ PANEL_NAME }'
SETTINGS = None

COMMAND_NAME = {
    "update":f"{PANEL_NAME}_update_panel"
}

# 记录最近一次关闭的窗体名称
LAST_ACTIVE_PANEL = None
LAST_COMMAND_PLACEHOLDER = True
LAST_COMMAND_STR = ""
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


# histroy settings
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
        print(err)
        return window.find_output_panel('exec')

def create_panel(panel_name:str) -> Optional[sublime.View]:
    global DEFAULT_PANEL_SETTINGS

    window = sublime.active_window()
    panel = window.create_output_panel(panel_name)
    settings = panel.settings()

    [settings.set(key,value) for key, value in DEFAULT_PANEL_SETTINGS]
    return panel

class CpsEditSettingCommand(sublime_plugin.TextCommand):
    def run(self, edit:sublime.Edit, base_file:str, package_name:str):
        sublime.active_window().run_command('edit_settings', {
                "base_file": os.path.join(sublime.packages_path(), __package__, '.sublime', base_file),
                "default": '{\n  \"' + package_name + '\":{\n    /*请在插件名称内选项内添加自定义配置*/\n    \n  }\n}'
            })

class SettingManager:
    def __init__(self, package_name:str, default_settings:str):
        self.package_name = package_name
        self.default_settings = default_settings

        self.data = {}

        self.file_paths = self.get_setting_file_path()
        self.get_setting_file_path()

        sublime.set_timeout_async(self.plugin_loaded_async)

    def __getitem__(self, target):
        if target in self.data:
            return self.data[target]

    def get_setting_file_path(self) -> dict:
        return {
            'user_path':os.path.join(sublime.packages_path(),'User'),
            'default_settings':os.path.join(sublime.packages_path(), __package__, '.sublime', self.default_settings),
            'user_settings':os.path.join(sublime.packages_path(),'User', self.default_settings),
        }

    def plugin_loaded_async(self):
        """
        @Description 监听用户配置文件
        """
        with open(self.file_paths['default_settings'], 'r', encoding='utf8') as f:

            self.data = sublime.decode_value(f.read()).get(self.package_name, {})

            if len(list(self.data.keys())) == 0:
                raise Exception('读取配置失败 ~~~ 请确保一下文件真实存在： ', self.file_paths['default_settings'])

        user_settings = sublime.load_settings(self.default_settings)
        utils.recursive_update(self.data, user_settings.to_dict()[self.package_name])
        user_settings.add_on_change(self.default_settings, self._on_settings_change)

    def _on_settings_change(self):
        tmp = sublime.load_settings(self.default_settings).get(self.package_name, None)

        if not tmp or not isinstance(tmp, dict): return

        utils.recursive_update(self.data, tmp)

        print('count: ', self.data)

        return



def plugin_loaded():
    global PANEL_NAME, HISTORY, DEFAULT_SETTINGS, SETTINGS
    print(f'{PANEL_NAME} run command 加载成功')
    ensure_panel(PANEL_NAME)

    SETTINGS = SettingManager(PLUGIN_NAME, DEFAULT_SETTINGS)
    HISTORY = History(HISTORY_LOCAL_FILE, max_count=50)




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
        global HISTORY, MSG_SELECTIONS_TITLE, SETTINGS

        window = sublime.active_window()
        panel_name = window.active_panel()

        if SETTINGS and SETTINGS['history_count']:
            commands_count = SETTINGS['history_count']
        else:
            commands_count = len(HISTORY.data)

        commands_list = HISTORY.data[0:commands_count]
        # print("commands_count: ", commands_count)

        selection_with_index = [ f'{index + 1}.  {HISTORY.data[index]}' for index in range(len(commands_list))]

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
        global MSG, HISTORY
        global LAST_COMMAND_PLACEHOLDER, LAST_COMMAND_STR

        if LAST_COMMAND_PLACEHOLDER:
            placeholder = LAST_COMMAND_STR

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
        global LAST_COMMAND_STR

        LAST_COMMAND_STR = user_input

        HISTORY.add(user_input)

        cwd = os.path.dirname(self.view.file_name())

        # run in new shell window
        run_with_new_window = False
        if user_input[0][0] in RUN_IN_NEW_WINDOW_PREFIX:
            if user_input[0][0] == ':':
                run_with_new_window = True

            if user_input[0][0] == '$':
                run_with_new_window = 5

            commands = str(user_input[1:]).split(' ')
            shell.run_command(commands, shell=bool(run_with_new_window), pause=run_with_new_window, cwd=cwd)

            return

        # running in sublime exec
        commands = str(user_input).split(' ')
        res = shell.run_command(commands, shell=run_with_new_window, pause=run_with_new_window, cwd=cwd)

        if res['success']:
            command_res = res['res']
        else:
            command_res = res['err']

        # command_res += LINE_END
        command_res = f'WORK_SPACE: {cwd}\n\n{command_res}\n{LINE_END}'
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
