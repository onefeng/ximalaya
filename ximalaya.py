#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import time
from concurrent.futures import ThreadPoolExecutor

import requests

__author__ = 'onefeng'

executor = ThreadPoolExecutor(2)

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s -%(message)s')

ALBUM_ID_LIST = [22963309]  # if you need more video, add album_id to here, e.g.ALBUM_ID_LIST = [22963309, 30890162]


class XimaSpider(object):
    start_url = 'https://m.ximalaya.com/m-revision/common/album/queryAlbumTrackRecordsByPage'
    headers = {
        'Host': 'm.ximalaya.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'
    }

    def get_page(self, album_id, page):
        """

        :param album_id:
        :param page:
        :return:
        """
        params = {
            'albumId': album_id,
            'page': page,
            'pageSize': 10,
            'asc': 'true',
            'countKeys': 'play, comment',
            'v': round(time.time() * 1000),
        }
        try:

            r = requests.get(url=self.start_url, params=params, headers=self.headers)
            if r.status_code == 200:
                return r.json()
        except requests.ConnectionError as e:
            logging.exception(e)

    def get_total_page(self, response):
        """

        :param response:
        :return:
        """
        if response:
            total_num = response.get('data').get('totalCount')
            if total_num:
                return total_num

    def get_detail(self, response):
        """

        :param response:
        :return:
        """
        if response:
            items = response.get('data').get('trackDetailInfos')
            for item in items:
                result = dict()
                play_path = item.get('trackInfo').get('playPath')
                title = item.get('trackInfo').get('title')
                if play_path:
                    result['title'] = title
                    result['play_path'] = play_path
                    yield result

    def save_video(self, result):
        """

        :param result:
        :return:
        """
        r = requests.get(url=result['play_path'], stream=True)
        file = result['title'] + '.m4a'
        with open(file, 'wb') as f:
            for data in r.iter_content(chunk_size=1024):
                f.write(data)

    def start(self):
        """

        :return:
        """
        for album_id in ALBUM_ID_LIST:
            page_result = self.get_page(album_id, 1)
            total_num = self.get_total_page(page_result)
            pages = total_num // 10 + 1
            for page in range(1, pages + 1):
                response = self.get_page(album_id, page)
                items = self.get_detail(response)
                for item in items:
                    logging.info(f"saving video..{item['title']}.")
                    executor.submit(self.save_video, item)


if __name__ == '__main__':
    t = XimaSpider()
    t.start()
