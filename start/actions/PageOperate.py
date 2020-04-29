# -*- coding: utf-8 -*-
from runtime.Action import Action
import asyncio


class Pagetype(Action):
    """通过pyppeteer的page对象 找到输入框并输入文本"""
    _id = '573050c6-eb03-11e9-9543-8cec4bd887f3'
    node_info = {"args": [['page_str', 'String', 'ce698bd1-f3a7-11e9-98af-8cec4bd887f3'],
                          ['type_css_str', 'String', 'ce698bd2-f3a7-11e9-917f-8cec4bd887f3'],
                          ['content_str', 'String', 'ce698bd3-f3a7-11e9-9100-8cec4bd887f3'],
                          ['In', 'Event', 'ce698bd4-f3a7-11e9-b27d-8cec4bd887f3']],
                 "returns": [['page_str', 'String', 'ce698bd5-f3a7-11e9-a115-8cec4bd887f3'],
                             ['Out', 'Event', 'ce698bd6-f3a7-11e9-83e5-8cec4bd887f3']]}

    # async def pagetype(self, args, io):
    #     await asyncio.sleep(1)
    #     page = args['page_str']
    #     type_css = args['type_css_str']
    #     content = args['content_str']
    #     while not await page.querySelector(type_css):
    #         pass
    #     await page.type(type_css, content)
    #     io.set_output('page_str', page)

    # def __call__(self, args, io):
    #     asyncio.get_event_loop().run_until_complete(
    #         self.pagetype(args, io))
    #
    #     io.push_event('Out')


class Pageclick(Action):
    """通过pyppeteer的page对象 找到输入框并输入文本"""
    _id = 'd84b0266-ebc9-11e9-a303-8cec4bd887f3'
    node_info = {"args": [['page_str', 'String', 'ce698bd7-f3a7-11e9-88ce-8cec4bd887f3'],
                          ['click_css_str', 'String', 'ce698bd8-f3a7-11e9-bf86-8cec4bd887f3'],
                          ['yes_or_no_str', 'String', 'e1a69ef3-f951-11e9-9cff-8cec4bd887f3'],
                          ['In', 'Event', 'ce698bd9-f3a7-11e9-bbac-8cec4bd887f3']],
                 "returns": [['page_str', 'String', 'ce698bda-f3a7-11e9-88a1-8cec4bd887f3'],
                             ['Out', 'Event', 'ce698bdb-f3a7-11e9-8b19-8cec4bd887f3']]}

    # async def pagetype(self, args, io, isurlchange):
    #     page = args['page_str']
    #     click_css = args['click_css_str']
    #     while not await page.querySelector(click_css):
    #         pass
    #     if isurlchange == 'yes':
    #         await asyncio.gather(
    #             page.click(click_css),
    #             page.waitForNavigation(),
    #         )
    #     else:
    #         await page.click(click_css)
    #         await asyncio.sleep(2)
    #     io.set_output('page_str', page)

    # def __call__(self, args, io):
    #     isurlchange = args['yes_or_no_str']
    #     """判断 click()是否会触发网页跳转"""
    #     asyncio.get_event_loop().run_until_complete(
    #         self.pagetype(args, io, isurlchange))
    #     io.push_event('Out')
    #

class Pagecookie(Action):
    """通过page登录后，获取当前登录页面的cookie值"""
    _id = 'ee8e7f58-eb30-11e9-8551-8cec4bd887f3'
    node_info = {"args": [['page_str', 'String', 'ce698bdc-f3a7-11e9-bb00-8cec4bd887f3'],
                          ['In', 'Event', 'ce698bdd-f3a7-11e9-b23e-8cec4bd887f3']],
                 "returns": [['cookie_list', 'List', 'ce698bde-f3a7-11e9-bb1e-8cec4bd887f3'],
                             ['page_str', 'String', 'ce698bdf-f3a7-11e9-8458-8cec4bd887f3'],
                             ['Out', 'Event', 'ce698be0-f3a7-11e9-8efb-8cec4bd887f3']]}
    #
    # async def pagecookie(self, args, io):
    #     page = args['page_str']
    #     cookie = await page.cookies()
    #
    #     io.set_output('cookie_list', cookie)
    #     io.set_output('page_str', page)
    #
    # def __call__(self, args, io):
    #     asyncio.get_event_loop().run_until_complete(
    #         self.pagecookie(args, io))
    #
    #     io.push_event('Out')


class Pagecontent(Action):
    """通过page，获取页面源代码"""
    _id = 'a639d25a-eb3d-11e9-a625-8cec4bd887f3'
    node_info = {"args": [['page_str', 'String', 'ce698be1-f3a7-11e9-ae0e-8cec4bd887f3'],
                          ['In', 'Event', 'ce698be2-f3a7-11e9-8ef7-8cec4bd887f3']],
                 "returns": [['doc_str', 'String', 'ce698be3-f3a7-11e9-8570-8cec4bd887f3'],
                             ['Out', 'Event', 'ce698be4-f3a7-11e9-b559-8cec4bd887f3']]}

    # async def pagecontent(self, args, io):
    #     page = args['page_str']
    #     doc = await page.content()
    #     io.set_output('doc_str', doc)
    #
    # def __call__(self, args, io):
    #     asyncio.get_event_loop().run_until_complete(
    #         self.pagecontent(args, io))
    #     io.push_event('Out')


class Pagepulldown(Action):
    """通过page，将页面滚动到页面底部"""
    _id = '484da1a2-ebef-11e9-898d-8cec4bd887f3'
    node_info = {"args": [['page_str', 'String', 'ce698be5-f3a7-11e9-8ca1-8cec4bd887f3'],
                          ['In', 'Event', 'ce698be6-f3a7-11e9-a157-8cec4bd887f3']],
                 "returns": [['page_str', 'String', 'ce698be7-f3a7-11e9-8ee0-8cec4bd887f3'],
                             ['Out', 'Event', 'ce698be8-f3a7-11e9-bb8d-8cec4bd887f3']]}

    # async def pagepulldown(self, args, io):
    #     page = args['page_str']
    #     await page.evaluate('window.scrollBy(0, document.body.scrollHeight)')
    #     # await asyncio.sleep(1)
    #     io.set_output('page_str', page)
    #
    # def __call__(self, args, io):
    #     asyncio.get_event_loop().run_until_complete(
    #         self.pagepulldown(args, io))
    #     io.push_event('Out')


class Pageclose(Action):
    _id = 'effc5424-ec0c-11e9-921c-8cec4bd887f3'
    node_info = {"args": [['broswer_str', 'String', 'ce698be9-f3a7-11e9-89e4-8cec4bd887f3'],
                          ['In', 'Event', 'ce698bea-f3a7-11e9-b997-8cec4bd887f3']],
                 "returns": []}

    # async def pageclose(self, args):
    #     page = args['broswer_str']
    #     await page.close()
    #
    # def __call__(self, args, io):
    #     asyncio.get_event_loop().run_until_complete(
    #         self.pageclose(args))
