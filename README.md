# 简介|Introductions

因为组内的项目都是我搭建的，特意写一个脚手架，可以快速生成一些项目结构，快速添加一些常用脚本到项目中。

<div>
    <img flex="left" src="https://img.shields.io/badge/python-%3E%3D3.8.0-3776AB"/>
    <img flex="left" src="https://img.shields.io/badge/Sublime%20Text-FF9800?style=flat&logo=Sublime%20Text&logoColor=white"/>
    <img flex="left" src="https://img.shields.io/github/license/caoxiemeihao/electron-vite-vue?style=flat"/>
</div>


# 使用|Usage

- **`Alt + f1` 调出命令输入框，直接执行`cmd`的命令**
```bash
# 调出输入框
alt + f1

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
- **便捷的快速输入常用命令**
![](screenshot/step1.gif)



- **历史记录功能**
默认记录100条，最高500条
![](screenshot\step2.gif)


- **快速的搜索历史记录**
![](screenshot\step3.gif)
![](screenshot\step4.gif)

- **插件配置**

```json
// Packages/User/cps.sublime-settings
{
  "name": "tett 插件",
  "author": "CPS",
  "mail": "373704015@qq.com",
  
  "cps_run_commands": {      // 所有配置都在这个字段内
    "default_workspace":".", // 默认的工作目录
    "history_count":100,     // 历史记录数量
  }
}

```





# 联系方式|Contact

- **373704015 (qq、wechat、email)**
