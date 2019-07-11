<h1 align="center">CoolQ Python Bot</h1>
<p align="center"><b>Work in Progress</b></p>

> 基于酷Q+CQHTTP的多功能QQ机器人

---

## **介绍**  *Introduce*

`CoolQ Python Bot`是一款基于CQHTTP插件提供的HTTP API而工作的QQ机器人项目

## **演示** *Demo*

请联系作者[mnixry](mailto:admin@mnixry.cn)获取演示机器人qq号

## **部署** *Deploy*

**该操作需要全程在程序目录下进行操作**

```shell
git clone https://github.com/mnixry/coolQPythonBot
cd coolQPythonBot
```

### 0. 检查运行环境
- `Asia/Shanghai (GMT+8)`时区
- `Python 3.6` 及以上版本
- 可靠的pypi源([推荐清华tuna镜像](https://mirror.tuna.tsinghua.edu.cn/help/pypi/))
- 齐全的Python标准库

### 1. 安装第三方库
- `pip install -r requirements.txt`
- *(您可能需要将`pip`替换为`pip3`)*

### 2. 设置HTTP代理服务器
- 由于某些原因,本机器人提供的服务国内无法访问,于是采用HTTP代理方法
- 请在本地的`1081`端口架设无验证的HTTP代理服务以便机器人访问国外服务

### 3. 安装CoolQ和CQHTTP插件
- 本机器人大量功能依赖CoolQ Pro,**强烈建议购买CoolQ Pro 以获得更好的使用体验**
- CQHTTP的反向ws端口请设置为`8000`

### 4. 启动机器人
- `python main.py`
- *(您可能需要将`python`替换为`python3`)*

## **当前功能** *Function*

插件名称|功能|完成度
---|---|---
animeImageSearch|基于[trace.moe](https://trace.moe)的以图搜番|基本完成
bilibiliGuide|b站视频/番剧订阅|未完成
illustImageSearch|基于[ascii2d.com](https://ascii2d.com)的以图搜图|基本完成
helper|帮助插件|能用
neteaseGuide|网易云歌曲相关功能|只实现点歌
pixivGuide|p站搜图点图|基本完成
SFWPictures|你猜?|基本完成
getRunTime|获取机器人运行时间|完成
hitokoMan|一言|完成
randomRepeater|随机复读机|基本完成

## **致谢** *Thanks*
>[nonebot](https://none.rclab.tk)框架使得该机器人能够存在

>[Imjad API](https://api.imjad.cn)使得该QQ机器人大部分功能成为可能


<del>又不开源别人又看不到就当练一练写Readme吧</del>