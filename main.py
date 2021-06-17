import asyncio
import time
from textwrap import dedent

import httpx
import yaml
from aiowikibot import Bot

from gacha import Gacha

with open('data/const.yaml', encoding='utf-8') as f:
    const = yaml.load(f, Loader=yaml.BaseLoader)


async def main():
    with open('data/setting.yaml', encoding='utf-8') as s:
        setting = yaml.load(s, Loader=yaml.BaseLoader)

    bot = Bot(setting['username'], setting['password'], setting['api_url'])
    await bot.login_wiki()
    tasks = []
    selection = ''
    while selection != 'exit':
        tasks.clear()
        selection = input('Update or write:')
        if selection == 'update':
            tasks.append(update_op(bot))
            tasks.append(update_gacha(bot))
            try:
                await asyncio.gather(*tasks)
            except httpx.ReadTimeout:
                print("Time Out")
        elif selection == 'write':
            tasks += await write_gacha_page(bot)
            await asyncio.gather(*tasks)
    await bot.close()


async def write_gacha_page(bot):
    """generate write task"""
    tasks = []
    '''卡池一览/限时寻访'''
    text = ['==非标准寻访==\n', await generate_gacha_table(category='special'),
            '\n==标准寻访==\n', await generate_gacha_table()]
    page_text = ''.join(text)
    tasks.append(
        bot.write_wiki('卡池一览/限时寻访', page_text, 'Edited by bot.', bot=True, minor=False))
    '''卡池一览'''
    text = [const['gacha_header'], await generate_gacha_table(range=33, category='overview'),
            '\n==常驻标准寻访==\n', await generate_gacha_table(range=44, category='rotate'), const['seo_text']]
    page_text = ''.join(text)
    tasks.append(
        bot.write_wiki('卡池一览', page_text, 'Edited by bot.', bot=True, minor=False))
    '''卡池一览/常驻标准寻访'''
    text = await generate_gacha_table(range=44, category='rotate')
    tasks.append(
        bot.write_wiki('卡池一览/常驻标准寻访/2021', text, 'Edited by bot.', bot=True, minor=False))
    return tasks


async def generate_gacha_table(*, range=None, category='standard'):
    """Generate wikitext for gacha overview page"""
    '''Range of gacha to display in list'''
    gacha_range = range
    '''String to return'''
    text = []
    print('out')
    '''Load gacha and operator data'''
    with open('data/gacha.yaml') as g:
        full_list = yaml.unsafe_load(g)
    with open('data/operator.yaml') as op:
        op_dict = yaml.unsafe_load(op)
    print('out')

    gacha_list = []
    if category != 'overview':
        for gacha in full_list:
            if gacha.category == category:
                gacha_list.append(gacha)
    else:
        for gacha in full_list:
            if gacha.category != 'rotate':
                gacha_list.append(gacha)

    if category == "rotate":
        gacha_title = const['rotate_gacha_title']
    else:
        gacha_title = const['standard_gacha_title']
    text.append(dedent(gacha_title))
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
        '''convert time'''
        time_array = time.localtime(int(gacha.start_time))
        s_time = time.strftime("%Y-%m-%d %H:%M", time_array)
        time_array = time.localtime(int(gacha.end_time))
        e_time = time.strftime("%Y-%m-%d %H:%M", time_array)
        limit_text = ''

        text.append(f"\n|-")
        if category == 'rotate':
            text.append(f"\n|{gacha_list.index(gacha) + 1}")
        text.append(f"\n|[[{gacha.filename}|400px|link={gacha.link}]]")
        if category != 'rotate':
            if gacha.series == '':
                text.append(f"<br/>[[{gacha.link}|{gacha.name}]]")
            else:
                text.append(f"<br/>[[{gacha.link}|【限定寻访·{gacha.series}】{gacha.name}]]")
        text.append(f"\n|{s_time}~<br/>{e_time}\n|")

        for op in gacha.shop_op:
            if op_dict[op]['star'] == 5:
                text.append(f"{{{{干员头像|{op}|shop=1}}}}")
        for op in gacha.pickup_op:
            if op_dict[op]['star'] == 5:
                if op_dict[op]['obtain'] == '限定寻访':
                    text.append(f"{{{{干员头像|{op}|limited=1}}}}")
                    if op_dict[op]['limit_time'] != '':
                        time_array = time.localtime(int(op_dict[op]['limit_time']))
                        limit_time = time.strftime("%Y-%m-%d", time_array)
                        limit_text = f'''\n※限定干员【{op}】加入【{gacha.series}】系列限定寻访的时间为{limit_time}'''
                else:
                    text.append(f"{{{{干员头像|{op}}}}}")

        text.append(limit_text)
        limit_text = ''
        if gacha.comment1 != "":
            text.append(f"\n※{gacha.comment1}")
        text.append('\n|')

        for op in gacha.shop_op:
            if op_dict[op]['star'] < 5:
                text.append(f"{{{{干员头像|{op}|shop=1}}}}")
        for op in gacha.pickup_op:
            if op_dict[op]['star'] < 5:
                if op_dict[op]['obtain'] == '限定寻访':
                    text.append(f"{{{{干员头像|{op}|limited=1}}}}")
                    if op_dict[op]['limit_time'] != '':
                        time_array = time.localtime(int(op_dict[op]['limit_time']))
                        limit_time = time.strftime("%Y-%m-%d", time_array)
                        limit_text = f'''\n※限定干员【{op}】加入【{gacha.series}】系列限定寻访的时间为{limit_time}'''
                else:
                    text.append(f"{{{{干员头像|{op}}}}}")

        text.append(limit_text)
        if gacha.comment2 != "":
            text.append(f"\n※{gacha.comment2}")
        text.append('')
    if category == 'special':
        text.append(const['startup_gacha_table'])
    else:
        text.append("\n|}")

    return ''.join(text)


async def update_op(bot):
    print('op')
    ask_string = const['ask_op']
    tasks = [bot.ask(ask_string)]
    results = await asyncio.gather(*tasks)
    print('op')
    op = {}
    for result in results[0]['results']:
        for data in result.values():
            name = data['printouts']['干员名'][0]
            op[name] = {
                'star': int(data['printouts']['稀有度'][0]),
                'number': data['printouts']['干员序号'][0],
                'obtain': data['printouts']['获得方式'][0]
            }
            try:
                op[name]['limit_time'] = data['printouts']['寻访解限时间'][0]['timestamp']
            except IndexError:
                op[name]['limit_time'] = ''
            else:
                print('Found limit time')
    with open('data/operator.yaml', 'w') as op_file:
        yaml.dump(op, op_file)
    print("Operator data updated.")


async def update_gacha(bot):
    print("gacha")
    ask_string = [
        const['ask_rotate_gacha'],
        const['ask_standard_gacha'],
        const['ask_special_gacha']
    ]
    tasks = []
    for string in ask_string:
        tasks.append(bot.ask(string))
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
                link=data['printouts']['卡池名'][0],
                category='rotate'
            ))
    for result in results[1]['results']:
        for file, data in result.items():
            g_result = Gacha(
                data['printouts']['寻访开启时间cn'][0]['timestamp'],
                data['printouts']['寻访关闭时间cn'][0]['timestamp'],
                file,
                data['printouts']['出率提升干员'],
                link=data['printouts']['卡池名'][0],
                name=data['printouts']['寻访名cn'][0],
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
    for result in results[2]['results']:
        for file, data in result.items():
            g_result = Gacha(
                data['printouts']['寻访开启时间cn'][0]['timestamp'],
                data['printouts']['寻访关闭时间cn'][0]['timestamp'],
                file,
                data['printouts']['出率提升干员'],
                link=data['printouts']['卡池名'][0],
                name=data['printouts']['寻访名cn'][0],
                category='special'
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
            try:
                g_result.series = data['printouts']['限定寻访分类'][0]
            except IndexError:
                pass
            else:
                print('Found limit series')
            gacha.append(g_result)
            gacha.sort(key=lambda t_gacha: t_gacha.start_time)
    with open('data/gacha.yaml', 'w') as gacha_file:
        yaml.dump(gacha, gacha_file)
    print("Gacha data updated.")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    start = time.perf_counter()
    loop.run_until_complete(main())
    end = time.perf_counter()
    print(f"用时{end - start}s")
