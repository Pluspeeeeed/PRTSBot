import asyncio
import time
from textwrap import dedent

import httpx
from lxml import html
import yaml

from aiowikibot import Bot
from gacha import Gacha
from op import Operator

with open('const.yaml', encoding='utf-8') as f:
    const = yaml.load(f, Loader=yaml.BaseLoader)


async def main():
    with open('setting.yaml', encoding='utf-8') as s:
        setting = yaml.load(s, Loader=yaml.BaseLoader)

    bot = Bot(setting['username'], setting['password'], setting['api_url'])
    await bot.login_wiki()
    tasks = []
    selection = ''
    while selection != 'exit':
        tasks.clear()
        selection = input('Update or write:')
        if selection == 'update':
            # tasks.append(update_op(bot))
            tasks.append(update_gacha(bot))
            try:
                await asyncio.gather(*tasks)
            except httpx.ReadTimeout:
                print("Tine Out")
        elif selection == 'write':
            text = await generate_standard_gacha(bot)
            tasks.append(
                bot.write_wiki('用户:Txrtanzi/sandbox/gacha/full', text, 'Edited by bot.', bot=True, minor=False))
            await asyncio.gather(*tasks)
        elif selection == 'print':
            await print_data()
    await bot.close()


async def print_data():
    gacha = input("rotate or standard:")
    if gacha == 'rotate':
        with open('gacha_rotate.yaml') as g:
            gacha_list = yaml.unsafe_load(g)
            for gacha in gacha_list:
                gacha.show()
    elif gacha == 'standard':
        with open('gacha_standard.yaml') as g:
            gacha_list = yaml.unsafe_load(g)
            for gacha in gacha_list:
                gacha.show()


async def generate_standard_gacha(bot, *, range=None):
    """Generate wikitext for standard gacha page"""
    '''Range of gacha to display in list'''
    gacha_range = range
    '''String to return'''
    text = []
    print('out')
    '''Load gacha and operator data'''
    with open('gacha_standard.yaml') as g:
        gacha_list = yaml.unsafe_load(g)
    with open('operator.yaml') as op:
        op_list = yaml.unsafe_load(op)
    ''''dump operator name and star into a dict for query'''
    op_index = {}
    for op in op_list:
        op_index[op.name] = op.star
    print('out')
    rotate_title = const['standard_gacha_title']

    text.append(dedent(rotate_title))
    '''process range'''
    if gacha_range is None:
        gacha_range = (0, len(gacha_list))
    elif type(range) is int:
        gacha_range = (range, len(gacha_list))
    print(gacha_range)
    t_list = gacha_list[gacha_range[0]: gacha_range[1]]
    t_list.reverse()
    '''generate table'''
    for gacha in t_list:
        time_array = time.localtime(int(gacha.start_time))
        s_time = time.strftime("%Y-%m-%d %H:%M", time_array)
        time_array = time.localtime(int(gacha.end_time))
        e_time = time.strftime("%Y-%m-%d %H:%M", time_array)
        table = f"""
            |-
            |[[{gacha.filename}|400px|link={gacha.link}]]<br/>[[{gacha.link}|{gacha.name}]]
            |{s_time}~<br/>{e_time}"""
        text.append(dedent(table))
        text.append('\n|')
        for op in gacha.shop_op:
            if op_index[op] == 5:
                text.append(f"{{{{干员头像|{op}|shop=1}}}}")
        for op in gacha.pickup_op:
            if op_index[op] == 5:
                text.append(f"{{{{干员头像|{op}}}}}")
        if gacha.comment1 != "":
            text.append(f"\n※{gacha.comment1}")
        text.append('\n|')
        for op in gacha.shop_op:
            if op_index[op] < 5:
                text.append(f"{{{{干员头像|{op}|shop=1}}}}")
        for op in gacha.pickup_op:
            if op_index[op] < 5:
                text.append(f"{{{{干员头像|{op}}}}}")
        if gacha.comment2 != "":
            text.append(f"\n※{gacha.comment2}")
        text.append('')
    text.append('\n|}')

    return ''.join(text)


async def generate_special_gacha(bot, *, range=None):
    return None


async def generate_rotate_gacha(bot, *, range=None):
    """Generate wikitext for rotate gacha page"""
    '''Range of gacha to display in list'''
    gacha_range = range
    '''String to return'''
    text = []
    print('out')
    '''Load gacha and operator data'''
    with open('gacha_rotate.yaml') as g:
        gacha_list = yaml.unsafe_load(g)
    with open('operator.yaml') as op:
        op_list = yaml.unsafe_load(op)
    ''''dump operator name and star into a dict for query'''
    op_index = {}
    for op in op_list:
        op_index[op.name] = op.star
    print('out')
    rotate_title = const['rotate_gacha_title']

    text.append(dedent(rotate_title))
    '''process range'''
    if gacha_range is None:
        gacha_range = (0, len(gacha_list))
    elif type(range) is int:
        gacha_range = (range, len(gacha_list))
    print(gacha_range)
    t_list = gacha_list[gacha_range[0]: gacha_range[1]]
    t_list.reverse()
    '''generate table'''
    for gacha in t_list:
        time_array = time.localtime(int(gacha.start_time))
        s_time = time.strftime("%Y-%m-%d %H:%M", time_array)
        time_array = time.localtime(int(gacha.end_time))
        e_time = time.strftime("%Y-%m-%d %H:%M", time_array)
        table = f"""
            |-
            |{gacha_list.index(gacha) + 1}
            |[[{gacha.filename}|400px|link={gacha.link}]]
            |{s_time}~<br/>{e_time}"""
        text.append(dedent(table))
        text.append('\n|')
        for op in gacha.shop_op:
            if op_index[op] == 5:
                text.append(f"{{{{干员头像|{op}|shop=1}}}}")
        for op in gacha.pickup_op:
            if op_index[op] == 5:
                text.append(f"{{{{干员头像|{op}}}}}")
        text.append('\n|')
        for op in gacha.shop_op:
            if op_index[op] < 5:
                text.append(f"{{{{干员头像|{op}|shop=1}}}}")
        for op in gacha.pickup_op:
            if op_index[op] < 5:
                text.append(f"{{{{干员头像|{op}}}}}")
        text.append('')
    text.append('\n|}')
    
    return ''.join(text)


async def update_op(bot):
    print('op')
    ask_string = const['ask_op']
    tasks = [bot.ask(ask_string)]
    results = await asyncio.gather(*tasks)
    print('op')
    op = []
    for result in results[0]['results']:
        for data in result.values():
            op.append(Operator(
                data['printouts']['干员名'][0],
                int(data['printouts']['稀有度'][0]),
                data['printouts']['干员序号'][0]
            ))
    with open('operator.yaml', 'w') as op_file:
        yaml.dump(op, op_file)
    print("Operator data updated.")


async def update_gacha(bot):
    print("gacha")
    ask_string = [const['ask_rotate_gacha'], const['ask_standard_gacha']]
    tasks = [bot.ask(ask_string[0]), bot.ask(ask_string[1])]
    print(ask_string[1])
    results = await asyncio.gather(*tasks)
    print("gacha")
    gacha = []
    for result in results[0]['results']:
        for file, data in result.items():
            gacha.append(Gacha(
                data['printouts']['寻访开启时间cn'][0]['timestamp'],
                data['printouts']['寻访关闭时间cn'][0]['timestamp'],
                file,
                data['printouts']['出率提升干员'],
                shop_op=data['printouts']['商店兑换干员'],
                link=data['printouts']['卡池名'][0]
            ))
    with open('gacha_rotate.yaml', 'w') as rotate_file:
        yaml.dump(gacha, rotate_file)
    gacha = []
    for result in results[1]['results']:
        for file, data in result.items():
            g_result = Gacha(
                data['printouts']['寻访开启时间cn'][0]['timestamp'],
                data['printouts']['寻访关闭时间cn'][0]['timestamp'],
                file,
                data['printouts']['出率提升干员'],
                link=data['printouts']['卡池名'][0],
                name=data['printouts']['寻访名cn'][0]
            )
            try:
                g_result.comment1 = data['printouts']['备注1'][0]
            except IndexError:
                pass
            else:
                print('Found comment 1')
            try:
                g_result.comment2 = data['printouts']['备注2'][0]
            except IndexError:
                pass
            else:
                print('Found comment 2')
            gacha.append(g_result)
    with open('gacha_standard.yaml', 'w') as standard_file:
        yaml.dump(gacha, standard_file)
    print("Gacha data updated.")


async def copy_text(bot):
    # title = 'User:txrtanzi/sandbox/auto'
    title = '卡池一览/常驻标准寻访/2019'
    tasks = [bot.read_parsed('User:Txrtanzi/榛名')]
    results = await asyncio.gather(*tasks)

    tree = html.fromstring(results[0])
    # with open('result.txt', 'w', encoding='utf-8') as result_file:
    #     result_file.write(results[0])
    tasks = [bot.write_wiki(title, tree.text_content().rstrip(), 'Edited by bot', bot=True)]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    # asyncio.set_event_loop_policy(None)
    loop = asyncio.get_event_loop()
    start = time.perf_counter()
    loop.run_until_complete(main())
    end = time.perf_counter()
    print(f"用时{end - start}s")
