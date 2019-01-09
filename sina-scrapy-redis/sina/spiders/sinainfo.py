# -*- coding: utf-8 -*-
import scrapy
import os
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from sina.items import SinaItem
from scrapy_redis.spiders import RedisSpider

#1.访问主页，获取大标题，大标题链接，小标题，小标题链接，保存至item中
#2.访问小标题页面，获取文章链接，保存至item中
#3.访问文章页面，获取标题和内容，保存至item中，yield给pipeline

class SinainfoSpider(RedisSpider):
    name = 'sinainfo'
    allowed_domains = ['sina.com.cn']
    start_urls = ["http://news.sina.com.cn/guide/"]
    redis_key = "SinainfoSpider:start_urls"
    #建立根目录文件夹

    #处理大标题页面内容,生成以小标题为单位的item，保存到列表中
    def parse(self, response):
        #根结点
        pre_root = response.xpath("//div[@id='tab01']/div[@class='clearfix']")[:19]
        for seed in pre_root:
            #第一层循环,取大标题的名称并创建文件夹
            preTitle = seed.xpath("./h3[@class='tit02']/a/text()").extract()[0]
            preUrl = seed.xpath("./h3[@class='tit02']/a/@href").extract()[0]

            #第二层循环,取大标题下的li标签为列表做迭代,以小标题为单位生成item
            li_list = seed.xpath("./ul[@class='list01']/li")
            for li in li_list:
                #创建item
                item = SinaItem()
                #大标题取值
                item["preTitle"] = preTitle
                item["preUrl"] = preUrl
                #小标题取值
                item["subTitle"] = li.xpath("./a/text()").extract()[0]
                subUrl = li.xpath("./a/@href").extract()[0]
                #判断小标题链接开头是否是大标题链接，如果是则存储
                #if subUrl.startswith(item["preUrl"]):
                item["subUrl"] = subUrl
                #else:
                    #continue
                #保存小标题文件夹路径,用于存储文章内容，同时创建小标题文件夹
                item["subFilepath"] = './sinainfo/' + item["preTitle"] + '/' + item["subTitle"]
                yield scrapy.Request(item["subUrl"], meta = {"meta_item" : item}, callback = self.parse_info)

    #处理小标题页面信息,获取文章链接
    def parse_info(self, response):
        url_list = response.xpath("//a/@href").extract()
        #获取item
        meta_item = response.meta["meta_item"]
        for url in url_list:
            if url[-5:] == "shtml" and url.startswith(meta_item["preUrl"]):              
                #针对每一个符合条件的url，新建一个item保存
                item = SinaItem()
                item["preTitle"] = meta_item["preTitle"]
                item["preUrl"] = meta_item["preUrl"]
                item["subTitle"] = meta_item["subTitle"]
                item["subUrl"] = meta_item["subUrl"]
                item["subFilepath"] = meta_item["subFilepath"]
                #加入新字段textUrl               
                item["textUrl"] = url
                print url
                yield scrapy.Request(item["textUrl"], meta = {"meta_item" : item}, callback = self.parse_text)
            else:
                continue
            


    #处理文章页面信息，获取标题和文章内容
    def parse_text(self, response):
        if response:
            item = response.meta["meta_item"]
            try:
                item["textHead"] = response.xpath("//h1/text()").extract()[0]
            except:
                item["textHead"] = ' '


            item["textContent"] = ''
            try:
                for data in response.xpath("//div[@class='article']/p/text()|//div[@id='artibody']/p/text()").extract():
                    item["textContent"] += data
            except:
                item["textContent"] = ''            
            yield item

        else:
            item["textHead"] = ''
            item["textContent"] = ''
            yield item








            


