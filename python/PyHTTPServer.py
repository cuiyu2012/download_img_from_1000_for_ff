__author__ = 'knightingal'

from BaseHTTPServer import HTTPServer
from CGIHTTPServer import CGIHTTPRequestHandler
import json
import urllib2
import os
from threading import Thread
import Queue

rootDirString = '/home/knightingal/Downloads/.mix/1000/'


def str_cmp(str1, str2):
    if len(str1) < len(str2):
        return -1
    elif len(str1) > len(str2):
        return 1
    else:
        return str1 > str2 and 1 or -1


class RequestHandler(CGIHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write("hello world")

    def do_POST(self):
        content_length = self.headers.dict["content-length"]
        content = self.rfile.read(int(content_length))

        path = self.path
        resp_body = ""
        if path == '/testExist/':
            print content
            try:
                os.mkdir(rootDirString + content)
                resp_body = "True"
            except OSError:
                print rootDirString + content + "exists"
                resp_body = "False"
            finally:
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(resp_body)
                return

        #print content
        json_obj_total = json.loads(content)
        print json_obj_total
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write("ok")

        thread_list = []
        for jsonObj in json_obj_total:
            #jsonObj = json.loads(jsonObjStr)
            title = jsonObj["title"]
            print title
            try:
                os.mkdir(rootDirString + jsonObj["title"])
            except OSError:
                print rootDirString + jsonObj["title"] + "exists"
            for url in jsonObj["imgSrcArray"]:
                thread = MyThread(url, jsonObj["href"], jsonObj["title"])
                #thread.start()
                thread_list.append(thread)

        for thread_item in thread_list:
            thread_item.start()

        for thread_item in thread_list:
            thread_item.join()
        print "all task succ"
        for root, dirs, files in os.walk(rootDirString + json_obj_total[0]["title"]):
            if root == rootDirString + json_obj_total[0]["title"]:
                pagefd = open(root + "/page.html", "w")
                pagefd.write("<html><head></head><body>")
                files.sort(str_cmp)
                for picname in files:
                    pagefd.write('<img src="' + picname + '"></img>')
                pagefd.write("</body></html>")
                pagefd.close()

        for thread_item in thread_list:
            if not thread_item.is_succ:
                print "%s is not succ" % thread_item.img_url


class MyThread(Thread):
    def __init__(self, img_url, web_age_url, title_str):
        Thread.__init__(self)
        self.img_url = img_url
        self.web_age_url = web_age_url
        self.title_str = title_str
        self.is_succ = False

    def run(self):
        que.get()
        download_img(self.img_url, self.web_age_url, self.title_str)
        self.is_succ = True
        que.put(1)


def download_img(img_url, web_age_url, title_str):
    while True:
        print "downloading %s" % img_url
        try:
            request = urllib2.Request(img_url)
            request.add_header("Referer", web_age_url)
            request.add_header(
                "User-Agent",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.31 "
                "(KHTML, like Gecko) Chrome/26.0.1410.63 Safari/537.31"
            )
            request.add_header("Connection", "keep-alive")
            request.add_header("Accept", "*/*")
            request.add_header("Accept-Encoding", "gzip,deflate,sdch")
            request.add_header("Accept-Language", "zh-CN,zh;q=0.8")
            request.add_header("Accept-Charset", "GBK,utf-8;q=0.7,*;q=0.3")
            picfd = urllib2.urlopen(request)
            picstring = picfd.read()
            picfd.close()
            picfd = open(rootDirString + title_str + '/' + img_url.split('/')[-1], 'wb')
            picfd.write(picstring)
            picfd.close()
        except Exception, e:
            print e
        if os.path.exists(rootDirString + title_str + '/' + img_url.split('/')[-1]):
            print "%s download succ" % img_url
            break
        else:
            print "%s download erro, try again" % img_url

if __name__ == "__main__":
    que = Queue.Queue()
    for i in range(10):
        que.put(1)

    server_addr = ('', 8081)
    server = HTTPServer(server_addr, RequestHandler)
    server.serve_forever()
