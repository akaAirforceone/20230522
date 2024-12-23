# -*- coding:utf-8 -*-
import ssl
import threading

context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE
import time
from PIL import Image, ImageTk
from get_movie_data import movieData
from get_movie_data import get_url_data_in_ranking_list
from get_movie_data import get_url_data_in_keyWord
from tkinter import Tk
from tkinter import ttk
from tkinter import font
from tkinter import LabelFrame
from tkinter import Label
from tkinter import StringVar
from tkinter import Entry
from tkinter import END
from tkinter import Button
from tkinter import Frame
from tkinter import RIGHT
from tkinter import NSEW
from tkinter import NS
from tkinter import NW
from tkinter import N
from tkinter import Y
from tkinter import messagebox
from json import loads
from threading import Thread
from urllib.parse import quote
from webbrowser import open
import urllib
import os
import ssl
import urllib.request
import re
import urllib.parse
from tkinter import DISABLED, NORMAL
import sqlite3



# 此处去掉重复设置默认https上下文的代码，避免重复设置可能带来的潜在问题
# ssl._create_default_https_context = ssl._create_unverified_context #关闭SSL证书验证

# 定义更丰富的请求头信息，模拟浏览器请求
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.205 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
}

def thread_it(func, *args):
    '''
    将函数打包进线程
    '''
    # 创建
    t = Thread(target=func, args=args)
    # 守护
    t.setDaemon(True)
    # 启动
    t.start()


def handlerAdaptor(fun, **kwds):
    '''
    事件处理函数的适配器，相当于中介
    '''
    return lambda event: fun(event, **kwds)



def save_img(img_url, file_name, file_path):
    """
    下载指定url的图片，并保存运行目录下的img文件夹
    :param img_url: 图片地址
    :param file_name: 图片名字
    :param file_path: 存储目录
    :return:
    """
    #保存图片到磁盘文件夹 file_path中，默认为当前脚本运行目录下的img文件夹
    try:
        #判断文件夹是否已经存在
        if not os.path.exists(file_path):
            print('文件夹',file_path,'不存在，重新建立')
            os.makedirs(file_path)
        #获得图片后缀
        file_suffix = os.path.splitext(img_url)[1]
        #拼接图片名（包含路径）
        filename = '{}{}{}{}'.format(file_path,os.sep,file_name,file_suffix)

        #判断文件是否已经存在
        if not os.path.exists(filename):
            print('文件', filename, '不存在，重新建立')
            # 下载图片，并保存到文件夹中
            urllib.request.urlretrieve(img_url, filename=filename)
        return filename

    except IOError as e:
        print('下载图片操作失败',e)
    except Exception as e:
        print('错误:',e)



def resize(w_box, h_box, pil_image):
    """
    等比例缩放图片,并且限制在指定方框内
    :param w_box,h_box: 指定方框的宽度和高度
    :param pil_image: 原始图片
    :return:
    """

    f1 = 1.0 * w_box / pil_image.size[0]  # 1.0 forces float division in Python2
    f2 = 1.0 * h_box / pil_image.size[1]
    factor = min([f1, f2])
    # print(f1, f2, factor) # test
    # use best down-sizing filter
    width = int(pil_image.size[0] * factor)
    height = int(pil_image.size[1] * factor)
    return pil_image.resize((width, height), Image.Resampling.LANCZOS)


def get_mid_str(content, startStr, endStr):
    startIndex = content.find(startStr, 0)  # 定位到起始字符串的首个字符，从起始位置开始查找

    if startIndex >= 0:
        startIndex += len(startStr)
    else:
        return ""

    endIndex = content.find(endStr, startIndex)  # 定位到结束字符串，要从起始字符串开始查找

    if endIndex >= 0 and endIndex >= startIndex:
        return content[startIndex:endIndex]
    else:
        return ""


class uiObject:

    def __init__(self):
        self.jsonData = ""
        self.jsonData_keyword = ""

    def show_GUI_movie_detail(self):
        '''
        显示 影片详情 界面GUI
        '''
        self.label_img['state'] = NORMAL
        self.label_movie_name['state'] = NORMAL
        self.label_movie_rating['state'] = NORMAL
        self.label_movie_time['state'] = NORMAL
        self.label_movie_type['state'] = NORMAL
        self.label_movie_actor['state'] = NORMAL


    def hidden_GUI_movie_detail(self):
        '''
        显示 影片详情 界面GUI
        '''
        self.label_img['state'] = DISABLED
        self.label_movie_name['state'] = DISABLED
        self.label_movie_rating['state'] = DISABLED
        self.label_movie_time['state'] = DISABLED
        self.label_movie_type['state'] = DISABLED
        self.label_movie_actor['state'] = DISABLED

    def combined_show_data_and_update_database(self):
        """
        组合函数，用于执行show_IDMB_rating和update_database函数
        """
        lock=threading.Lock()#获取锁对象

        lock.acquire()
        self.show_IDMB_rating()
        lock.release()

        lock.acquire()
        self.update_database()
        lock.release()

    def show_IDMB_rating(self):
        """
        显示IMDB评分
        """
        self.label_movie_rating_imdb.config(text='')
        self.B_0_imdb['state'] = DISABLED

        item = self.treeview.selection()
        if item:
            item_text = self.treeview.item(item, "values")
            movieName = item_text[0]  # 输出电影名

            for movie in self.jsonData:
                if movie['title'] == movieName:
                    # 创建一个不验证服务器证书的SSLContext，用于绕过SSL证书验证
                    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE

                    req = urllib.request.Request(url=movie['url'], headers=headers)  # 使用定义好的请求头
                    with urllib.request.urlopen(req, context=context) as f:
                        response = f.read().decode()

                    self.clear_tree(self.treeview_play_online)
                    s = response
                    #print(response)

                    # name = re.findall(r'<a class="playBtn" data-cn="(.*?)" data-impression-track', s)
                    # down_url = re.findall(r'data-cn=".*?" href="(.*?)" target=', s)
#####################################################################################################################
                    # # 匹配爱奇艺链接
                    # iqiyi_url = re.findall(r'<a href="//www.igiyi.com".*?>', s)
                    # # 如果想提取 <a> 标签里的文本内容（这里示例文本可能是类似显示的文字等）
                    # iqiyi_name = re.findall(r'<a href="//www.igiyi.com.*?>(.*?)</a>', s)
                    #
                    # # 提取腾讯链接（根据提供的id和class等标识更准确匹配）
                    # tencent_url = re.findall(r'<a id="header-logo".*?href="(.*?)".*?>', s)
                    # # 提取对应的文本内容（比如腾讯这里可能有对应的显示文字等）
                    # tencent_name = re.findall(r'<a id="header-logo".*?>(.*?)</a>', s)
                    #
                    # # 提取优酷链接
                    # youku_url = re.findall(r'<a href="https://www.youku.com/channel/webhome".*?>', s)
                    # # 提取对应的文本内容（比如“首页”等字样）
                    # youku_name = re.findall(r'<a href="https://www.youku.com/channel/webhome".*?>(.*?)</a>', s)
                    # res_list=[]
                    # res_list.append("res_list item:",[iqiyi_name,"限VIP免费",iqiyi_url])

#######################################################################################################################

                    res_list = []
                    #for i in range(len(name)):
                    res_list.append(["腾讯视频","限VIP免费","https://v.qq.com/"])
                    res_list.append(["爱奇艺视频", "限VIP免费", "https://www.iqiyi.com/"])
                    res_list.append(["优酷视频", "限VIP免费", "https://www.youku.com/"])


                     #print("res_list item:", [name[i], "限VIP免费", down_url[i]])  #测试

                    self.add_tree(res_list, self.treeview_play_online)

                    self.clear_tree(self.treeview_save_cloud_disk)
                    res_list = []
                    res_list.append(
                        ["56网盘搜索", "有效",
                         "https://www.56wangpan.com/search/o2kw" + urllib.parse.quote(movie['title'])])
                    res_list.append(
                        ["爱搜资源", "有效",
                         "https://www.aisouziyuan.com/?name=" + urllib.parse.quote(movie['title']) + "&page=1"])
                    res_list.append(
                        ["盘多多", "有效",
                         "http://www.panduoduo.net/s/comb/n-" + urllib.parse.quote(movie['title']) + "&f-f4"])
                    res_list.append(
                        ["小白盘", "有效",
                         "https://www.xiaobaipan.com/list-" + urllib.parse.quote(movie['title']) + "1.html"])
                    res_list.append(["云盘精灵", "有效", "https://www.yunpanjingling.com/search/" + urllib.parse.quote(
                        movie['title']) + "?sort=size.desc"])
                    self.add_tree(res_list, self.treeview_save_cloud_disk)

                    self.clear_tree(self.treeview_bt_download)
                    res_list = []
                    res_list.append(
                        ['19影视', '有效',
                         'https://www.19kan.com/vodsearch.html?wd=' + urllib.parse.quote(movie['title'])])
                    res_list.append(['2TU影院', '有效',
                                     'http://www.82tu.cc/search.php?submit=%E6%90%9C+%E7%B4%A2&searchword=' + urllib.parse.quote(
                                         movie['title'])])
                    res_list.append(['4K电影', '有效', 'https://www.dygc.org/?s=' + urllib.parse.quote(movie['title'])])
                    res_list.append(
                        ['52 Movie', '有效',
                         'http://www.52movieba.com/search.htm?keyword=' + urllib.parse.quote(movie['title'])])
                    res_list.append(
                        ['592美剧', '有效', 'http://www.592meiju.com/search/?wd=' + urllib.parse.quote(movie['title'])])
                    res_list.append(
                        ['97电影网', '有效', 'http://www.55xia.com/search?q=' + urllib.parse.quote(movie['title'])])
                    res_list.append(['98TVS', '有效', 'http://www.98tvs.com/?s=' + urllib.parse.quote(movie['title'])])
                    res_list.append(
                        ['9去这里', '有效',
                         'http://9qzl.com/index.php?s=/video/search/wd/' + urllib.parse.quote(movie['title'])])
                    res_list.append(
                        ['CK电影', '有效', 'http://www.ck180.net/search.html?q=' + urllib.parse.quote(movie['title'])])
                    res_list.append(
                        ['LOL电影', '有效',
                         'http://www.993dy.com/index.php?m=vod-search&wd=' + urllib.parse.quote(movie['title'])])
                    res_list.append(
                        ['MP4Vv', '有效',
                         'http://www.mp4pa.com/search.php?searchword=' + urllib.parse.quote(movie['title'])])
                    res_list.append(
                        ['MP4电影', '有效',
                         'http://www.domp4.com/search/' + urllib.parse.quote(movie['title']) + "1.html"])
                    res_list.append(['TL95', '有效', 'http://www.tl95.com/?s=' + urllib.parse.quote(movie['title'])])
                    res_list.append(
                        ['比特大雄', '有效', 'https://www.btdx8.com/?s=' + urllib.parse.quote(movie['title'])])
                    res_list.append(
                        ['比特影视', '有效', 'https://www.bteye.com/search/' + urllib.parse.quote(movie['title'])])
                    res_list.append(['春晓影视', '有效',
                                     'http://search.chunxiao.tv/?keyword=' + urllib.parse.quote(movie['title'])])
                    res_list.append(
                        ['第一电影网', '有效', 'https://www.001d.com/?s=' + urllib.parse.quote(movie['title'])])
                    res_list.append(
                        ['电影日志', '有效', 'http://www.dyrizhi.com/search?s=' + urllib.parse.quote(movie['title'])])
                    res_list.append(
                        ['高清888', '有效',
                         'https://www.gaoqing888.com/search?kw=' + urllib.parse.quote(movie['title'])])
                    res_list.append(
                        ['高清MP4', '有效',
                         'http://www.mp4ba.com/index.php?m=vod-search&wd=' + urllib.parse.quote(movie['title'])])
                    res_list.append(
                        ['高清电台', '有效', 'https://gaoqing.fm/s.php?q=' + urllib.parse.quote(movie['title'])])
                    res_list.append(
                        ['高清控', '有效', 'http://www.gaoqingkong.com/?s=' + urllib.parse.quote(movie['title'])])
                    res_list.append(
                        ['界绍部', '有效', 'http://www.jsb456.com/?s=' + urllib.parse.quote(movie['title'])])
                    res_list.append(['看美剧', '有效',
                                     'http://www.kanmeiju.net/index.php?s=/video/search/wd/' + urllib.parse.quote(
                                         movie['title'])])
                    res_list.append(
                        ['蓝光网', '有效', 'http://www.languang.co/?s=' + urllib.parse.quote(movie['title'])])
                    res_list.append(
                        ['老司机电影', '有效', 'http://www.lsjdyw.net/search/?s=' + urllib.parse.quote(movie['title'])])
                    res_list.append(
                        ["乐赏电影", '有效',
                         'http://www.gscq.me/search.htm?keyword=' + urllib.parse.quote(movie['title'])])
                    res_list.append(["美剧汇", '有效',
                                     'http://www.meijuhui.net/search.php?q=' + urllib.parse.quote(movie['title'])])
                    res_list.append(['美剧鸟', '有效',
                                     'http://www.meijuniao.com/index.php?s=vod-search-wd-' + urllib.parse.quote(
                                         movie['title'])])
                    res_list.append(['迷你MP4', '有效', 'http://www.minimp4.com/search?q=' + urllib.parse.quote(movie['title'])])
                    res_list.append(
                        ['泡饭影视', '有效', 'http://www.chapaofan.com/search/' + urllib.parse.quote(movie['title'])])
                    res_list.append(
                        ['片吧', '有效', 'http://so.pianbar.com/search.aspx?q=' + urllib.parse.quote(movie['title'])])
                    res_list.append(
                        ['片源网', '有效', 'http://pianyuan.net/search?q=' + urllib.parse.quote(movie['title'])])
                    res_list.append(['飘花资源网', '有效',
                                     'https://www.piaohua.com/plus/search.php?kwtype=0&keyword=' + urllib.parse.quote(
                                         movie['title'])])
                    res_list.append(['趣味源', '有效', 'http://quweiyuan.cc/?s=' + urllib.parse.quote(movie['title'])])
                    res_list.append(
                        ['人生05', '有效', 'http://www.rs05.com/search.php?s=' + urllib.parse.quote(movie['title'])])
                    res_list.append(['贪玩影视', '有效',
                                     'http://www.tanwanyingshi.com/movie/search?keyword=' + urllib.parse.quote(
                                         movie['title'])])
                    res_list.append(['新片网', '有效',
                                     'http://www.91xinpian.com/index.php?m=vod-search&wd=' + urllib.parse.quote(
                                         movie['title'])])
                    res_list.append(
                        ['迅雷影天堂', '有效', 'https://www.xl720.com/?s=' + urllib.parse.quote(movie['title'])])
                    res_list.append(
                        ['迅影网', '有效', 'http://www.xunyingwang.com/search?q=' + urllib.parse.quote(movie['title'])])
                    res_list.append(
                        ['一只大榴莲', '有效', 'http://www.llduang.com/?s=' + urllib.parse.quote(movie['title'])])
                    res_list.append(
                        ['音范丝', '有效', 'http://www.yinfans.com/?s=' + urllib.parse.quote(movie['title'])])
                    res_list.append(
                        ['影海', '有效',
                         'http://www.yinghub.com/search/list.html?keyword=' + urllib.parse.quote(movie['title'])])
                    res_list.append(
                        ['影视看看', '有效',
                         'http://www.yskk.tv/index.php?m=vod-search&wd=' + urllib.parse.quote(movie['title'])])
                    res_list.append(['云播网', '有效',
                                     'http://www.yunbowang.cn/index.php?m=vod-search&wd=' + urllib.parse.quote(
                                         movie['title'])])
                    res_list.append(
                        ['中国高清网', '有效', 'http://gaoqing.la/?s=' + urllib.parse.quote(movie['title'])])
                    res_list.append(
                        ['最新影视站', '有效', 'http://www.zxysz.com/?s=' + urllib.parse.quote(movie['title'])])
                    self.add_tree(res_list, self.treeview_bt_download)

                    imdb_num = get_mid_str(response, 'IMDb:</span>', '<br>').strip()
                    imdb_url = "https://www.imdb.com/title/{}/".format(imdb_num)
                    print("电影名:{}, IMDb:{}".format(movie['title'], imdb_num))

                    req_imdb = urllib.request.Request(url=imdb_url, headers=headers)  # 针对IMDb请求也使用定义好的请求头
                    time.sleep(2)
                    with urllib.request.urlopen(req_imdb, context=context) as f:
                        data_imdb = f.read().decode()
                    rating_imdb = get_mid_str(data_imdb, '{"@type":"AggregateRating"', '}')
                    rating_imdb = rating_imdb.split(":")[-1]

                    #self.label_movie_rating_imdb.config(text='IMDB评分:' + rating_imdb + '分')

            self.B_0_imdb['state'] = NORMAL

    def project_statement_show(self, event):
        open("https://i.chaoxing.com/base?vflag=true&fid=&backUrl=")

    def project_statement_get_focus(self, event):
        self.project_statement.config(fg="blue", cursor="hand1")

    def project_statement_lose_focus(self, event):
        self.project_statement.config(fg="#FF0000")


    def show_movie_data(self, event):
        '''
        显示某个被选择的电影的详情信息
        '''

        # self.hidden_GUI_movie_detail()

        self.B_0_imdb['state'] = NORMAL
        self.label_movie_rating_imdb.config(text = '')
        self.clear_tree(self.treeview_play_online)
        self.clear_tree(self.treeview_save_cloud_disk)
        self.clear_tree(self.treeview_bt_download)

        item = self.treeview.selection()
        if item:
            item_text = self.treeview.item(item, "values")
            movieName = item_text[0] # 输出电影名
            for movie in self.jsonData:
                if(movie['title'] == movieName):
                    img_url = movie['cover_url']
                    movie_name = movie['title']
                    file_name = save_img(img_url, movie_name, 'img') #下载网络图片
                    self.show_movie_img(file_name)
                    self.label_movie_name.config(text=movie['title'])
                    if(isinstance(movie['actors'],list)):
                        string_actors = "、".join(movie['actors'])
                    else:
                        string_actors = movie['actors']
                    self.label_movie_actor.config(text=string_actors)
                    self.label_movie_rating.config(text=str(movie['rating'][0]) + '分 ' + str(movie['vote_count']) + '人评价')
                    self.label_movie_time.config(text=movie['release_date'])
                    self.label_movie_type.config(text=movie['types'])

                    break

        # self.show_GUI_movie_detail()

    def update_database(self):
        """
        创建数据库表（如果不存在），并从show_movie_data函数获取的信息中提取影片相关信息插入表中
        """
        # 创建数据库连接，若不存在则创建名为movies.db的数据库文件
        conn = sqlite3.connect('movies.db')
        cursor = conn.cursor()

        # 创建表的SQL语句（如果表不存在则创建）
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS movies (
            movie_name TEXT NOT NULL PRIMARY KEY,
            movie_rating REAL DEFAULT 0.0,
            movie_date TEXT,
            movie_type TEXT,
            movie_actors TEXT
        );
        """
        cursor.execute(create_table_sql)

        item = self.treeview.selection()
        if item:
            item_text = self.treeview.item(item, "values")
            movieName = item_text[0]  # 获取电影名

            # 检查电影名称是否已存在于数据库中
            check_sql = "SELECT movie_name FROM movies WHERE movie_name =?"
            cursor.execute(check_sql, (movieName,))
            existing_movie = cursor.fetchone()
            if existing_movie:
                print(f"电影 {movieName} 已存在于数据库中，无需重复插入")
                return  # 直接返回，不进行后续插入操作

            for movie in self.jsonData:
                if movie['title'] == movieName:
                    movie_info = []
                    # 获取影片名字
                    movie_info.append(movie['title'])
                    # 获取影片评价，将评分数值和投票人数拼接成字符串形式（你可根据实际需求调整存储格式）
                    movie_info.append(float(movie['rating'][0]))
                    # 获取影片日期
                    movie_info.append(movie['release_date'])
                    # 获取影片类型，处理类型为列表的情况
                    movie_types = movie['types']
                    if isinstance(movie_types, list):
                        movie_type_str = ', '.join(movie_types)  # 将列表转换为逗号分隔的字符串
                    else:
                        movie_type_str = movie_types
                    movie_info.append(movie_type_str)
                    # 获取影片演员信息
                    if isinstance(movie['actors'], list):
                        string_actors = "、".join(movie['actors'])
                    else:
                        string_actors = movie['actors']
                    movie_info.append(string_actors)

                    # 插入数据的SQL语句，使用?作为占位符防止SQL注入
                    insert_sql = """
                    INSERT INTO movies (movie_name, movie_rating, movie_date, movie_type, movie_actors)
                    VALUES (?,?,?,?,?)
                    """
                    try:
                        cursor.execute(insert_sql, tuple(movie_info))
                        conn.commit()
                        print(f"成功将电影 {movie['title']} 的信息插入数据库")
                    except sqlite3.Error as e:
                        print(f"插入电影信息到数据库时出错: {e}")
                    finally:
                        pass

        cursor.close()
        conn.close()

    def show_movie_img(self, file_name):
        '''
        更新图片GUI
        :param file_name: 图片路径
        :return:
        '''
        img_open = Image.open(file_name) #读取本地图片
        pil_image_resized = resize(160, 230, img_open) #等比例缩放本地图片
        img = ImageTk.PhotoImage(pil_image_resized) #读入图片
        self.label_img.config(image=img, width = pil_image_resized.size[0], height = pil_image_resized.size[1])
        self.label_img.image = img

    def center_window(self, root, w, h):
        """
        窗口居于屏幕中央
        :param root: root
        :param w: 窗口宽度
        :param h: 窗口高度
        :return:
        """
        # 获取屏幕 宽、高
        ws = root.winfo_screenwidth()
        hs = root.winfo_screenheight()

        # 计算 x, y 位置
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)

        root.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def clear_tree(self, tree):
        '''
        清空表格
        '''
        x = tree.get_children()
        for item in x:
            tree.delete(item)

    def add_tree(self,list, tree):
        '''
        新增数据到表格
        '''
        i = 0
        for subList in list:
            tree.insert('', 'end', values=subList)
            i = i + 1
        tree.grid()

    def searh_movie_in_rating(self):
        """
        从排行榜中搜索符合条件的影片信息
        """

        # 按钮设置为灰色状态
        self.clear_tree(self.treeview)  # 清空表格
        self.B_0['state'] = DISABLED
        self.C_type['state'] = DISABLED
        self.T_count['state'] = DISABLED
        self.T_rating['state'] = DISABLED
        self.T_vote['state'] = DISABLED
        self.B_0_keyword['state'] = DISABLED
        self.T_vote_keyword['state'] = DISABLED
        self.B_0['text'] = '正在努力搜索'
        self.jsonData = ""

        jsonMovieData = loads(movieData)
        for subMovieData in jsonMovieData:
            if(subMovieData['title'] == self.C_type.get()):
                res_data = get_url_data_in_ranking_list(subMovieData['type'], self.T_count.get(), self.T_rating.get(), self.T_vote.get())  # 返回符合条件的电影信息
                if len(res_data) == 2:
                    # 获取数据成功
                    res_list = res_data[0]
                    jsonData = res_data[1]

                    self.jsonData = jsonData
                    self.add_tree(res_list, self.treeview)  # 将数据添加到tree中

                else:
                    # 获取数据失败，出现异常
                    err_str = res_data[0]
                    messagebox.showinfo('提示', err_str[:1000])

        # 按钮设置为正常状态
        self.B_0['state'] = NORMAL
        self.C_type['state'] = 'readonly'
        self.T_count['state'] = NORMAL
        self.T_rating['state'] = NORMAL
        self.T_vote['state'] = NORMAL
        self.B_0_keyword['state'] = NORMAL
        self.T_vote_keyword['state'] = NORMAL
        self.B_0['text'] = '从排行榜搜索'

    def keyboard_T_vote_keyword(self, event):
        """
        在搜索框中键入回车键后触发相应的事件
        :param event:
        :return:
        """
        thread_it(self.searh_movie_in_keyword)

    def searh_movie_in_keyword(self):
        """
        从关键字中搜索符合条件的影片信息
        """
        # 按钮设置为灰色状态
        self.clear_tree(self.treeview)  # 清空表格
        self.B_0['state'] = DISABLED
        self.C_type['state'] = DISABLED
        self.T_count['state'] = DISABLED
        self.T_rating['state'] = DISABLED
        self.T_vote['state'] = DISABLED
        self.B_0_keyword['state'] = DISABLED
        self.T_vote_keyword['state'] = DISABLED
        self.B_0_keyword['text'] = '正在努力搜索'
        self.jsonData = ""


        res_data = get_url_data_in_keyWord(self.T_vote_keyword.get())
        if len(res_data) == 2:
            # 获取数据成功
            res_list = res_data[0]
            jsonData = res_data[1]

            self.jsonData = jsonData
            self.add_tree(res_list, self.treeview)  # 将数据添加到tree中
        else:
            # 获取数据失败，出现异常
            err_str = res_data[0]
            messagebox.showinfo('提示', err_str[:1000])

        # 按钮设置为正常状态
        self.B_0['state'] = NORMAL
        self.C_type['state'] = 'readonly'
        self.T_count['state'] = NORMAL
        self.T_rating['state'] = NORMAL
        self.T_vote['state'] = NORMAL
        self.B_0_keyword['state'] = NORMAL
        self.T_vote_keyword['state'] = NORMAL
        self.B_0_keyword['text'] = '从关键字搜索'

    def open_in_browser_douban_url(self, event):
        """
        从浏览器中打开指定网页
        :param
        :return:
        """
        item = self.treeview.selection()
        if item:
            item_text = self.treeview.item(item, "values")
            movieName = item_text[0]
            for movie in self.jsonData:
                if(movie['title'] == movieName):
                    open(movie['url'])

    def open_in_browser(self, event):
        """
        从浏览器中打开指定网页
        :param
        :return:
        """
        item = self.treeview_play_online.selection()
        if(item):
            item_text = self.treeview_play_online.item(item, "values")
            url = item_text[2]
            open(url)


    def open_in_browser_cloud_disk(self, event):
        """
        从浏览器中打开指定网页
        :param
        :return:
        """
        item = self.treeview_save_cloud_disk.selection()
        if(item):
            item_text = self.treeview_save_cloud_disk.item(item, "values")
            url = item_text[2]
            open(url)

    def open_in_browser_bt_download(self, event):
        """
        从浏览器中打开指定网页
        :param
        :return:
        """
        item = self.treeview_bt_download.selection()
        if(item):
            item_text = self.treeview_bt_download.item(item, "values")
            url = item_text[2]
            open(url)

    def ui_process(self):
        """
        Ui主程序
        :param
        :return:
        """
        root = Tk()
        self.root = root
        # 设置窗口位置
        root.title("lcy的豆瓣电影小助手")
        self.center_window(root, 1000, 565)
        root.resizable(0, 0)  # 框体大小可调性，分别表示x,y方向的可变性

        # 从排行榜 电影搜索布局开始
        # 容器控件
        labelframe = LabelFrame(root, width=660, height=300, text="搜索电影")
        labelframe.place(x=5, y=5)
        self.labelframe = labelframe

        # 电影类型
        L_typeId = Label(labelframe, text='电影类型')
        L_typeId.place(x=0, y=10)
        self.L_typeId = L_typeId

        #下拉列表框
        comvalue = StringVar()
        C_type = ttk.Combobox(labelframe, width=5, textvariable=comvalue, state='readonly')
        # 将影片类型输入到下拉列表框中
        jsonMovieData = loads(movieData) #json数据
        movieList = []
        for subMovieData in jsonMovieData: #对每一种类的电影题材进行操作
            movieList.append(subMovieData['title'])
        C_type["values"] = movieList #初始化
        C_type.current(9)  # 选择第一个
        C_type.place(x=65, y=8)
        self.C_type = C_type

        # 欲获取的电影数量
        L_count = Label(labelframe, text='获取数量=')
        L_count.place(x=150, y=10)
        self.L_count = L_count

        # 文本框
        T_count = Entry(labelframe, width=5)
        T_count.delete(0, END)
        T_count.insert(0, '100')
        T_count.place(x=220, y=7)
        self.T_count = T_count

        # 评分
        L_rating = Label(labelframe, text='影片评分>')
        L_rating.place(x=280, y=10)
        self.L_rating = L_rating

        # 文本框
        T_rating = Entry(labelframe, width=5)
        T_rating.delete(0, END)
        T_rating.insert(0, '8.0')
        T_rating.place(x=350, y=7)
        self.T_rating = T_rating

        # 评价人数
        L_vote = Label(labelframe, text='评价人数>')
        L_vote.place(x=410, y=10)
        self.L_vote = L_vote

        # 文本框
        T_vote = Entry(labelframe, width=7)
        T_vote.delete(0, END)
        T_vote.insert(0, '100000')
        T_vote.place(x=480, y=7)
        self.T_vote = T_vote



        # 查询按钮
        #lambda表示绑定的函数需要带参数，请勿删除lambda，否则会出现异常
        #thread_it表示新开启一个线程执行这个函数，防止GUI界面假死无响应
        B_0 = Button(labelframe, text="从排行榜搜索")
        B_0.place(x=560, y=10)
        self.B_0 = B_0



        # 框架布局，承载多个控件
        frame_root = Frame(labelframe, width=400)
        frame_l = Frame(frame_root)
        frame_r = Frame(frame_root)
        self.frame_root = frame_root
        self.frame_l = frame_l
        self.frame_r = frame_r


        # 表格
        columns = ("影片名字", "影片评分", "同类排名", "评价人数")
        treeview = ttk.Treeview(frame_l, height=10, show="headings", columns=columns)

        treeview.column("影片名字", width=210, anchor='center')  # 表示列,不显示
        treeview.column("影片评分", width=210, anchor='center')
        treeview.column("同类排名", width=100, anchor='center')
        treeview.column("评价人数", width=100, anchor='center')

        treeview.heading("影片名字", text="影片名字")  # 显示表头
        treeview.heading("影片评分", text="影片评分")
        treeview.heading("同类排名", text="同类排名")
        treeview.heading("评价人数", text="评价人数")



        #垂直滚动条
        vbar = ttk.Scrollbar(frame_r, command=treeview.yview)
        treeview.configure(yscrollcommand=vbar.set)

        treeview.pack()
        self.treeview = treeview
        vbar.pack(side=RIGHT, fill=Y)
        self.vbar = vbar

        # 框架的位置布局
        frame_l.grid(row=0, column=0, sticky=NSEW)
        frame_r.grid(row=0, column=1, sticky=NS)
        frame_root.place(x=5, y=70)

        # 从排行榜 电影搜索布局结束










        # 输入关键字 电影搜索布局开始

        # 影片名称
        L_vote_keyword = Label(labelframe, text='影片名称')
        L_vote_keyword.place(x=0, y=40)
        #L_vote_keyword.grid(row=0,column=0)
        self.L_vote_keyword = L_vote_keyword

        # 文本框
        T_vote_keyword = Entry(labelframe, width=53)
        T_vote_keyword.delete(0, END)
        T_vote_keyword.insert(0, '')
        T_vote_keyword.place(x=66, y=37)
        self.T_vote_keyword = T_vote_keyword


        # 查询按钮
        #lambda表示绑定的函数需要带参数，请勿删除lambda，否则会出现异常
        #thread_it表示新开启一个线程执行这个函数，防止GUI界面假死无响应
        B_0_keyword = Button(labelframe, text="从关键字搜索")
        B_0_keyword.place(x=560, y=40)
        self.B_0_keyword = B_0_keyword

        # 输入关键字 电影搜索布局结束










        # 电影详情布局开始
        # 容器控件
        labelframe_movie_detail = LabelFrame(root, text="影片详情")
        labelframe_movie_detail.place(x=670, y=5)
        self.labelframe_movie_detail = labelframe_movie_detail


        # 框架布局，承载多个控件
        frame_left_movie_detail = Frame(labelframe_movie_detail, width=160,height=280)
        frame_left_movie_detail.grid(row=0, column=0)
        self.frame_left_movie_detail = frame_left_movie_detail


        frame_right_movie_detail = Frame(labelframe_movie_detail, width=160,height=280)
        frame_right_movie_detail.grid(row=0, column=1)
        self.frame_right_movie_detail = frame_right_movie_detail


        #影片图片
        label_img = Label(frame_left_movie_detail, text="", anchor=N)
        label_img.place(x=0,y=0) #布局
        self.label_img = label_img

        # IMDB评分
        ft_rating_imdb = font.Font(weight=font.BOLD)
        label_movie_rating_imdb = Label(frame_left_movie_detail, text="IMDB评分", fg='#7F00FF', font=ft_rating_imdb, anchor=NW)
        label_movie_rating_imdb.place(x=0, y=250)
        self.label_movie_rating_imdb = label_movie_rating_imdb

        # 查询按钮
        B_0_imdb = Button(frame_left_movie_detail, text="查询")
        B_0_imdb.place(x=125, y=250)
        self.B_0_imdb = B_0_imdb


        #影片名字
        ft = font.Font(size=15, weight=font.BOLD)
        label_movie_name = Label(frame_right_movie_detail, text="影片名字", fg='#FF0000', font=ft,anchor=NW)
        label_movie_name.place(x=0, y=0)
        self.label_movie_name = label_movie_name

        #影片评分
        ft_rating = font.Font(weight=font.BOLD)
        label_movie_rating = Label(frame_right_movie_detail, text="影片评价", fg='#7F00FF', font=ft_rating, anchor=NW)
        label_movie_rating.place(x=0, y=30)
        self.label_movie_rating = label_movie_rating

        #影片年代
        ft_time = font.Font(weight=font.BOLD)
        label_movie_time = Label(frame_right_movie_detail, text="影片日期", fg='#666600', font=ft_time, anchor=NW)
        label_movie_time.place(x=0, y=60)
        self.label_movie_time = label_movie_time

        #影片类型
        ft_type = font.Font(weight=font.BOLD)
        label_movie_type = Label(frame_right_movie_detail, text="影片类型", fg='#330033', font=ft_type, anchor=NW)
        label_movie_type.place(x=0, y=90)
        self.label_movie_type = label_movie_type

        #影片演员
        label_movie_actor = Label(frame_right_movie_detail, text="影片演员", wraplength=135, justify = 'left', anchor=NW)
        label_movie_actor.place(x=0, y=120)
        self.label_movie_actor = label_movie_actor

        # 电影详情布局结束









        # 在线播放布局开始

        labelframe_movie_play_online = LabelFrame(root, width=324, height=230, text="在线观看")
        labelframe_movie_play_online.place(x=5, y=305)
        self.labelframe_movie_play_online = labelframe_movie_play_online

        # 框架布局，承载多个控件
        frame_root_play_online = Frame(labelframe_movie_play_online, width=324)
        frame_l_play_online = Frame(frame_root_play_online)
        frame_r_play_online = Frame(frame_root_play_online)
        self.frame_root_play_online = frame_root_play_online
        self.frame_l_play_online = frame_l_play_online
        self.frame_r_play_online = frame_r_play_online

        # 表格
        columns_play_online = ("来源名称", "是否免费","播放地址")
        treeview_play_online = ttk.Treeview(frame_l_play_online, height=15, show="headings", columns=columns_play_online)
        treeview_play_online.column("来源名称", width=90, anchor='center')
        treeview_play_online.column("是否免费", width=80, anchor='center')
        treeview_play_online.column("播放地址", width=120, anchor='center')
        treeview_play_online.heading("来源名称", text="来源名称")
        treeview_play_online.heading("是否免费", text="是否免费")
        treeview_play_online.heading("播放地址", text="播放地址")

        #垂直滚动条
        vbar_play_online = ttk.Scrollbar(frame_r_play_online, command=treeview_play_online.yview)
        treeview_play_online.configure(yscrollcommand=vbar_play_online.set)

        treeview_play_online.pack()
        self.treeview_play_online = treeview_play_online
        vbar_play_online.pack(side=RIGHT, fill=Y)
        self.vbar_play_online = vbar_play_online

        # 框架的位置布局
        frame_l_play_online.grid(row=0, column=0, sticky=NSEW)
        frame_r_play_online.grid(row=0, column=1, sticky=NS)
        frame_root_play_online.place(x=5, y=0)

        # 在线播放布局结束










        # 保存到云盘布局开始

        labelframe_movie_save_cloud_disk = LabelFrame(root, width=324, height=230, text="云盘搜索")
        labelframe_movie_save_cloud_disk.place(x=340, y=305)
        self.labelframe_movie_save_cloud_disk = labelframe_movie_save_cloud_disk

        # 框架布局，承载多个控件
        frame_root_save_cloud_disk = Frame(labelframe_movie_save_cloud_disk, width=324)
        frame_l_save_cloud_disk = Frame(frame_root_save_cloud_disk)
        frame_r_save_cloud_disk = Frame(frame_root_save_cloud_disk)
        self.frame_root_save_cloud_disk = frame_root_save_cloud_disk
        self.frame_l_save_cloud_disk = frame_l_save_cloud_disk
        self.frame_r_save_cloud_disk = frame_r_save_cloud_disk

        # 表格
        columns_save_cloud_disk = ("来源名称", "是否有效","播放地址")
        treeview_save_cloud_disk = ttk.Treeview(frame_l_save_cloud_disk, height=10, show="headings", columns=columns_save_cloud_disk)
        treeview_save_cloud_disk.column("来源名称", width=90, anchor='center')
        treeview_save_cloud_disk.column("是否有效", width=80, anchor='center')
        treeview_save_cloud_disk.column("播放地址", width=120, anchor='center')
        treeview_save_cloud_disk.heading("来源名称", text="来源名称")
        treeview_save_cloud_disk.heading("是否有效", text="是否有效")
        treeview_save_cloud_disk.heading("播放地址", text="播放地址")

        #垂直滚动条
        vbar_save_cloud_disk = ttk.Scrollbar(frame_r_save_cloud_disk, command=treeview_save_cloud_disk.yview)
        treeview_save_cloud_disk.configure(yscrollcommand=vbar_save_cloud_disk.set)

        treeview_save_cloud_disk.pack()
        self.treeview_save_cloud_disk = treeview_save_cloud_disk
        vbar_save_cloud_disk.pack(side=RIGHT, fill=Y)
        self.vbar_save_cloud_disk = vbar_save_cloud_disk

        # 框架的位置布局
        frame_l_save_cloud_disk.grid(row=0, column=0, sticky=NSEW)
        frame_r_save_cloud_disk.grid(row=0, column=1, sticky=NS)
        frame_root_save_cloud_disk.place(x=5, y=0)

        # 保存到云盘布局结束









        # BT下载布局开始

        labelframe_movie_bt_download = LabelFrame(root, width=324, height=230, text="影视下载")
        labelframe_movie_bt_download.place(x=670, y=305)
        self.labelframe_movie_bt_download = labelframe_movie_bt_download

        # 框架布局，承载多个控件
        frame_root_bt_download = Frame(labelframe_movie_bt_download, width=324)
        frame_l_bt_download = Frame(frame_root_bt_download)
        frame_r_bt_download = Frame(frame_root_bt_download)
        self.frame_root_bt_download = frame_root_bt_download
        self.frame_l_bt_download = frame_l_bt_download
        self.frame_r_bt_download = frame_r_bt_download

        # 表格
        columns_bt_download = ("来源名称", "是否有效","播放地址")
        treeview_bt_download = ttk.Treeview(frame_l_bt_download, height=10, show="headings", columns=columns_bt_download)
        treeview_bt_download.column("来源名称", width=90, anchor='center')
        treeview_bt_download.column("是否有效", width=80, anchor='center')
        treeview_bt_download.column("播放地址", width=120, anchor='center')
        treeview_bt_download.heading("来源名称", text="来源名称")
        treeview_bt_download.heading("是否有效", text="是否有效")
        treeview_bt_download.heading("播放地址", text="播放地址")

        #垂直滚动条
        vbar_bt_download = ttk.Scrollbar(frame_r_bt_download, command=treeview_bt_download.yview)
        treeview_bt_download.configure(yscrollcommand=vbar_bt_download.set)

        treeview_bt_download.pack()
        self.treeview_bt_download = treeview_bt_download
        vbar_bt_download.pack(side=RIGHT, fill=Y)
        self.vbar_bt_download = vbar_bt_download

        # 框架的位置布局
        frame_l_bt_download.grid(row=0, column=0, sticky=NSEW)
        frame_r_bt_download.grid(row=0, column=1, sticky=NS)
        frame_root_bt_download.place(x=5, y=0)

        # BT下载布局结束





        #项目的一些信息
        ft = font.Font(size=14, weight=font.BOLD)
        project_statement = Label(root, text="2204010418-刘程宇", fg='#FF0000', font=ft,anchor=NW)
        project_statement.place(x=5, y=540)
        self.project_statement = project_statement



        #绑定事件
        treeview.bind('<<TreeviewSelect>>', self.show_movie_data)  # 表格绑定选择事件
        treeview.bind('<Double-1>', self.open_in_browser_douban_url)  # 表格绑定鼠标左键事件
        treeview_play_online.bind('<Double-1>', self.open_in_browser)  # 表格绑定左键双击事件
        treeview_save_cloud_disk.bind('<Double-1>', self.open_in_browser_cloud_disk)  # 表格绑定左键双击事件
        treeview_bt_download.bind('<Double-1>', self.open_in_browser_bt_download)  # 表格绑定左键双击事件
        B_0.configure(command=lambda:thread_it(self.searh_movie_in_rating)) #按钮绑定单击事件
        B_0_keyword.configure(command=lambda:thread_it(self.searh_movie_in_keyword)) #按钮绑定单击事件

        #########################有问题待解决
        #B_0_imdb.configure(command=lambda: thread_it(self.show_IDMB_rating))  # 按钮绑定单击事件
        #B_0_imdb.configure(command=lambda: thread_it(self.update_database)) #按钮绑定单击事件
        #########################有问题待解决
        #使用线程锁解决并发问题
        B_0_imdb.configure(command=lambda: thread_it(self.combined_show_data_and_update_database()))

        T_vote_keyword.bind('<Return>', handlerAdaptor(self.keyboard_T_vote_keyword))  # 文本框绑定选择事件
        project_statement.bind('<ButtonPress-1>', self.project_statement_show)  # 标签绑定鼠标单击事件
        project_statement.bind('<Enter>', self.project_statement_get_focus)  # 标签绑定获得焦点事件
        project_statement.bind('<Leave>', self.project_statement_lose_focus)  # 标签绑定失去焦点事件

        root.mainloop()