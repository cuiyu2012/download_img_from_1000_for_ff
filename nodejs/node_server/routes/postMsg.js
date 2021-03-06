var express = require('express');
var router = express.Router();
var http = require("http");
var fs = require("fs");
var url = require('url');
var path = require('path');

var reqs = {};
var bufferArray = {};

var RootDirString = '/home/knightingal/Downloads/.mix/1000/';

function ReqHeadersTemp(pageHref) {
    this["Referer"] = pageHref;
    this["User-Agent"]= "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.63 Safari/537.31";
    this["Connection"]= "keep-alive";
    this["Accept"]= "*/*";
    this["Accept-Encoding"]= "gzip,deflate,sdch";
    this["Accept-Language"]= "zh-CN,zh;q=0.8";
    this["Accept-Charset"]= "GBK,utf-8;q=0.7,*;q=0.3";
}

var gImgCount = 0;
var gSuccCount = 0;

router.post('/', function(req, res) {
    console.log(req.body);
    res.send('ok');
    for (j = 0; j < req.body.length; j++) {
        gImgCount += req.body[j].imgSrcArray.length;
    }
    var dirName = RootDirString + req.body[0].title;
    fs.mkdir(dirName, function() {
        for (j = 0; j < req.body.length; j++) {
            console.log(req.body[j].imgSrcArray);
            console.log(req.body[j].href);

            var imgSrcArray = req.body[j].imgSrcArray;
            var pageHref = req.body[j].href;
            for (i = 0; i < imgSrcArray.length; i++) {
                
                var urlObj = url.parse(imgSrcArray[i]);
                var fileName = path.basename(imgSrcArray[i]);
                var options = {
                    host: urlObj.host,
                    path: urlObj.path,
                    headers: new ReqHeadersTemp(pageHref)
                };
                reqs[fileName] = http.request(options, (function(fileName) {
                    return function (res) {
                        var contentLength = res.headers['content-length'];
                        bufferArray[fileName] = [];
                        res.on('data', (function(fileName) {
                            return function (chunk) {
                                var buffer = new Buffer(chunk);
                                bufferArray[fileName].push(buffer);
                            };
                        })(fileName));
                        res.on('end', (function(fileName) {
                            return function() {
                                var totalBuff = Buffer.concat(bufferArray[fileName]);
                                fs.appendFile(dirName + "/" + fileName, totalBuff, function(err){});
                                gSuccCount += 1;
                                console.log("(" + gSuccCount + "/" + gImgCount + ")" + fileName + " download succ!");

                                if (gSuccCount == gImgCount) {
                                    console.log("all task succ!");
                                    gImgCount = gSuccCount = 0;
                                    router.initCb();
                                }
                            };
                        })(fileName));
                    };
                })(fileName));
                reqs[fileName].end();
            }
        }
    });

});

module.exports = router;
