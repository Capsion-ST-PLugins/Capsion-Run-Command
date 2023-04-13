## 简介|Introductions

<div>
    <img flex="left" src="https://img.shields.io/badge/python-%3E%3D3.8.0-3776AB"/>
    <img flex="left" src="https://img.shields.io/badge/Sublime%20Text-FF9800?style=flat&logo=Sublime%20Text&logoColor=white"/>
    <img flex="left" src="https://img.shields.io/github/license/caoxiemeihao/electron-vite-vue?style=flat"/>
</div>
ST 在项目中直接执行 shell 是前天性的功能不足，不像 vscode 的集成的 shell 那么强大。而老牌的 `sublimeREPL` 在中文环境中使用奇奇怪怪的 BUG，而且更新也不及时，为了提高团队和自己的调式效率，特意开发了一个带历史记录简易版，原理是直接调用 `SublimeText`的原生搜索框来直接调用 `cmd`或者 `powershell`来执行一些指令。

> - 本插件为团队内部打造使用，不对外更新负责，
> - 2023年了，前端建议采用**VSCode**。



## 功能|Feature

![screenshot](/screenshot/cps-Run-Command.gif "screenshot")
![cps-Run-Command](http://localhost:45462/image/cps-Run-Command.gif)

- 快捷调出命令输入窗口，自动关闭
- 自定义条数的保留历史记录，支持管理
- 自动读取项目的 **scripts** 到命令列表快捷调用，当前支持：
  - 所有 **node** 项目 `package.json`文件对应的 scripts 字段
  - 所有 **python** 项目的 `poetry.toml` 对应的 scripts 字段
- 支持内置调用（阻塞），外置调用（非阻塞）两种方式



## 安装|Install

```bash
# 打开 SublimeText3的插件目录，并在该目录下打开shell
菜单栏 > Preferences > Browse Packages...

# 在插件目录运行shell，下载插件
# gitee
git clone --depth=1 git@gitee.com:Capsion-ST-PLugins/Run-Command.git cps_run_command
# or github
git clone --depth=1 git@github.com:Capsion-ST-PLugins/Run-Command.git cps_run_command

# 重启ST 通过快捷键调用（前提要打开一个有效文件）
ctrl + f1 
```



## 使用|Usage

**快捷键：**

- `alt + f1`：调出插件面板（前提要打开一个有效文件）

```bash
# 支持单条命令
npm i

# 支持组合命令
git add . & git cz
mkdir projectName & cd projectName & npm init -y

# 使用 ":" 前缀会创建一个独立的cmd窗口来执行命令
:npm init -y

# 使用  "$" 前缀执行的命令不会记入历史记录，并且命令成功后，窗口自动关闭
$npm init -y

# 不使用任何后缀，会使用sublime内置的命令面板执行命令，无法进行交互
npm init
```



## 配置文件|Configure

### 插件配置

- `Packages/User/cps.sublime-settings`

```javascript
// 配置文件
{
  "name": "tett 插件",
  "author": "CPS",
  "mail": "373704015@qq.com",

  "cps_run_commands": { // 所有配置都在这个字段内
    "default_workspace": ".", // 默认的工作目录
    "history_count": 100      // 历史记录数量
      
    "mode_scripts_enable":true,           // 读取py和node项目的script字段
    "mode_scripts_run_in_new_shell":true, // 脚本通过独立的shell运行，不阻塞sublimetext
  }
}
```

### 快捷键

- `Packages/User/Default.sublime-keymap`

```js
[
  {
    "keys": ["alt+f1"],
    "command": "cps_run_commands"   // 打开调用窗体
  },
  {
    "keys": ["alt+f2"],
    "command": "cps_panel_toggle"   // 过往历史信息
  },
]
```



## 项目架构|Tree

```basic
DIR:cps-Run-Command                 # root
   |-- .github/                     #
   |   |-- workflows/               # 「workflows」
   |   |   |-- test.yaml            #
   |   |   `-- relese.yaml          #
   |-- .sublime/                    # 「.sublime」默认配置文件存放
   |   |-- Default.sublime-keymap   # 快捷键
   |   |-- Default.sublime-commands # 默认配置【只读】
   |   `-- Context.sublime-menu     # 右键菜单
   |-- core/                        # 「core」核心代码
   |   |-- __init__.py              #
   |   |-- utils.py                 #
   |   |-- typing.py                #
   |   |-- shell.py                 #
   |   |-- settingManager.py        #
   |   |-- scriptsParser.py         #
   |   |-- history.py               #
   |   `-- .histroy                 #
   |-- screenshot/                  # 「screenshot」
   |   |-- Usage.png                #
   |   |-- step4.gif                #
   |   |-- step3.gif                #
   |   |-- step2.gif                #
   |   |-- step1.gif                #
   |   `-- cps-Run-Command.gif      #
   |-- scripts/                     # 「scripts」
   |   `-- test.py                  #
   |-- yarn.lock                    #
   |-- README.md                    #
   |-- pyproject.toml               #
   |-- main.py                      # 入口代码
   |-- .python-version              #
   `-- .gitignore                   #

```



## 联系方式|Contact

- **373704015 (qq、wechat、email)**
