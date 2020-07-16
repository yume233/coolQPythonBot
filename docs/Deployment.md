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

    这一步网上教程很多，我不太想讲

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

- 咕了咕了

### 运行程序

- 这个我也不想讲`py main,py`就完事了