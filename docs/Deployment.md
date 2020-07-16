# 部署

## 注意事项

1. 部署本项目需要一定的计算机基础，包括但不限于以下技能
    1. 熟练使用搜索引擎解决已知问题
    2. 成熟的阅读文档能力
    3. (可选)英文阅读能力

2. 如果部署过程中出现任何错误和疑问，请按照以下步骤进行确认

    1. 是否按照教程的指示进行完整的安装？

    2. 是否跳过了某些步骤？

        如果以上步骤已经确认完毕，你可以通过[联系作者](mailto:admin@yami,im)来取得帮助

3. 性能要求

    |              | Linux(最低) | Linux(推荐)      | Windows(最低) | Windows(推荐) |
    | :----------: | ----------- | ---------------- | :------------ | :------------ |
    |     CPU      | 1核         | 1核              | 1核           | 2核           |
    |   内存大小   | 1GiB        | 2GiB + 1GiB Swap | 2GiB          | 4GiB          |
    |   网络带宽   | 10Mbps      | 30Mbps           | 10Mbps        | 30Mbps        |
    | 硬盘剩余空间 | 5GiB        | 10GiB            | 2GiB          | 4GiB          |



## 开始部署

### 准备本程序代码以及运行环境

1. 下载本程序代码

|                           下载方式                           | 优势                                           | 劣势                   |
| :----------------------------------------------------------: | :--------------------------------------------- | :--------------------- |
| **推荐**[从Release处下载](https://github.com/mnixry/coolQPythonBot/releases/latest) | 稳定、快捷                                     | 无法得到最新的功能更新 |
| [下载master分支源码](https://github.com/mnixry/coolQPythonBot/archive/master.zip) | 较为稳定、新功能多                             | 不一定十分稳定         |
|                        从Git仓库clone                        | 快捷(对于某些用户而言)、能够获得最新更新、灵活 | 稳定性差               |

2. 安装Python环境

    - **必须`Python3.8 `以及以上**
    - **包含完整的Python标准库(包括`sqlite`等)**

    *对于某些Linux发行版(例如`CentOS7`)来讲，以上要求意味着你需要自行编译安装Python运行环境*

    这一步网上教程很多，就不细讲了

### 准备QQ机器人框架

| 框架名称 | 优势               | 劣势                   |
| :------: | ------------------ | ---------------------- |
|   酷Q    | 稳定性好，社区广阔 | 需要付费，部署较为复杂 |
|  Mirai   | 免费开源，部署简单 | 稳定性差，社区较小     |

#### 使用酷Q Pro

**注意！因为本机器人的大量功能依赖图片发送功能，所以请使用需要付费的酷Q Pro**

1. [下载酷Q Pro](https://dlsec.cqp.me/cqp-full)

2. 请参考[CQHTTP文档](https://cqhttp.cc/docs/)下载安装CQHTTP插件

    - 如果你的windows不是最新版，可能无法启动CQHTTP插件，请安装[Visual C++ 可再发行软件包](https://aka.ms/vs/16/release/vc_redist.x86.exe)

3. 进行配置

    - 可参考[CQHTTP 文档/配置](https://cqhttp.cc/docs/#/Configuration)

    - **一定要记得打开拓展名显示**

        

    1. 打开`<酷Q运行目录>\data\app\io.github.richardchien.coolqhttpapi\config\`文件夹

    2. 删除该文件夹下所有文件

    3. 新建一个文件，名为`general.json`内容如下

        ```json
        {
            "use_http": false,
            "use_ws": false,
            "use_ws_reverse": true,
            "ws_reverse_use_universal_client": true,
            "ws_reverse_url": "ws://127.0.0.1:8080/ws/",
            "serve_data_files": false
        }
        ```

    4. 重启或者启动酷Q Pro

#### 使用Mirai

1. 前往miraiOK地址，根据你对应的平台下载[miraiOK](https://github.com/LXY1226/miraiOK#%E4%B8%8B%E8%BD%BD%E5%9C%B0%E5%9D%80)

2. 将miraiOK放置到一个你喜欢的目录，运行该文件

    - 首次运行因为需要下载一些环境依赖，需要较长时间

3. 安装`CQHTTPmirai`插件

    - [下载地址](https://github.com/yyuueexxiinngg/cqhttp-mirai/releases)
    - 参考[配置方式](https://github.com/yyuueexxiinngg/cqhttp-mirai#%E5%BC%80%E5%A7%8B%E4%BD%BF%E7%94%A8)

    - 参考配置文件`setting.yml`如下

        ```yaml
        # 要进行配置的QQ号 (Mirai支持多帐号登录, 故需要对每个帐号进行单独设置)
        '<你的机器人QQ号>':
            # 可选，反向客户端服务
            ws_reverse:
                # 可选，是否启用反向客户端，默认不启用
                enable: true
                # 上报消息格式，string 为字符串格式，array 为数组格式, 默认为string
                postMessageFormat: string
                # 反向Websocket主机
                reverseHost: 127.0.0.1
                # 反向Websocket端口
                reversePort: 8080
                # 反向Websocket路径
                reversePath: /ws
                # 访问口令, 默认为null, 即不设置Token
                accessToken: null
                # 反向 WebSocket 客户端断线重连间隔，单位毫秒
                reconnectInterval: 3000
        ```

4. 运行`miraiOK`，按照指引登录账号并进行验证

### 运行程序

为了保证程序运行的依赖不被破坏，**本程序极度建议采用virtualenv管理虚拟环境**

1. 打开本程序目录

2. 在命令行中进行进行依赖安装工作

    - 对于Windows

        ```
        python3 -m pip install pip -U
        pip3 install virtualenv
        virtualenv .venv
        .venv\Scripts\activate.bat
        pip install -r requirements
        ```

    - 对于Linux

        ```shell
        python3 -m pip install pip -U #升级pip
        pip3 install virtualenv #安装虚拟环境virtualenv
        python3 -m virtualenv .venv #创建虚拟环境
        source .venv/bin/activate #激活虚拟环境
        pip install -r requirements.txt #安装依赖
        ```

3. 在保持虚拟环境激活的情况下，运行`python3 main.py`即可启动程序

## 下一步该做什么？

在以上步骤都已经成功完成后

请移步[配置](Configuration.md)对机器人程序进行最基础的配置