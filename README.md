# 爬取豆瓣排行榜电影数据(含GUI界面版)


## 项目简介

该项目爬取的是豆瓣排行榜电影数据，其中加入了 GUI设计、多线程技术、数据库、网络请求协议、文件读写操作  等等


## 如何运行

1. 打开Chrome浏览器，在网址栏输入chrome://version/查询当前Chrome版本
2. 打开[http://chromedriver.storage.googleapis.com/index.html][1]，下载对应版本的chromedriver驱动，**下载完成后务必解压**，如果找不到对应的版本，可以上CSDN查找一下相关操作
3. 打开当前目录下的文件`getMovieInRankingList.py`，定位到第`123行`，将`executable_path=./chromedriver.exe`修改为你的chromedriver驱动路径
4. 执行命令`pip install -r requirement.txt`安装程序所需的依赖包
5. 执行命令`python main.py`运行程序，也可以使用pycharm运行

其中需要注意的是，数据库编写使用的是sqlite3


## 包含功能

- [x] 根据关键字搜索电影
- [x] 根据排行榜(TOP250)搜索电影
- [x] 显示IMDB评分及其他基本信息
- [x] 提供多个在线视频站点，无需vip
- [x] 提供多个云盘站点搜索该视频，以便保存到云盘
- [x] 提供多个站点下载该视频

## License
[The MIT License (MIT)][6]


[1]:http://chromedriver.storage.googleapis.com/index.html
[5]:https://github.com/shengqiangzhang/examples-of-web-crawlers
[6]:http://opensource.org/licenses/MIT

