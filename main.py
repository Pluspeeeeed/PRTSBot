import asyncio
import time
from textwrap import dedent

from lxml import html
import yaml

from aiowikibot import Bot
from gacha import Gacha
from op import Operator


async def main():
    with open('setting.yaml', encoding='utf-8') as s:
        setting = yaml.load(s, Loader=yaml.BaseLoader)

    bot = Bot(setting['username'], setting['password'], setting['api_url'])
    await bot.login_wiki()
    tasks = []
    # await generate_wikitext(bot)
    text = await generate_wikitext(bot, range=(0, 18))
    tasks.append(bot.write_wiki('User:Txrtanzi/sandbox/gacha/2019', text, 'Edited by bot.', bot=True, minor=False))
    text = await generate_wikitext(bot, range=(18, 44))
    tasks.append(bot.write_wiki('User:Txrtanzi/sandbox/gacha/2020', text, 'Edited by bot.', bot=True, minor=False))
    text = await generate_wikitext(bot, range=(44, 55))
    tasks.append(bot.write_wiki('User:Txrtanzi/sandbox/gacha/2021', text, 'Edited by bot.', bot=True, minor=False))
    # tasks = [update_op(bot), update_gacha(bot)]
    await asyncio.gather(*tasks)
    await bot.close()


async def generate_wikitext(bot, *, range=None):
    '''Range of gacha to display in list'''
    gacha_range = range
    '''String to return'''
    text = []
    print('out')
    '''Load gacha and operator data'''
    with open('gacha.yaml') as g:
        gacha_list = yaml.unsafe_load(g)
    with open('operator.yaml') as op:
        op_list = yaml.unsafe_load(op)
    ''''dump operator name and star into a dict for query'''
    op_index = {}
    for op in op_list:
        op_index[op.name] = op.star
    print('out')
    rotate_title = """\
        {| class="wikitable mw-collapsible fullline logo" style="width:100%; text-align:center; white-space:normal; display:table;"
        ! style="width:5%" |序号
        ! style="width:25%" |寻访页面
        ! style="width:20%" |开启时间
        ! style="width:25%" |特定干员（6星）
        ! style="width:25%" |特定干员（5星）"""

    text.append(dedent(rotate_title))
    '''process range'''
    if gacha_range is None:
        gacha_range = (0, len(gacha_list))
    elif len(range) == 1:
        gacha_range = (range, len(gacha_list))

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
    with open('setting.yaml', encoding='utf-8') as s:
        setting = yaml.load(s, Loader=yaml.BaseLoader)
    ask_string = setting['ask_op']
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
    with open('operator.yaml', 'w') as f:
        yaml.dump(op, f)
    print("Operator data updated.")


async def update_gacha(bot):
    print("gacha")
    with open('setting.yaml', encoding='utf-8') as s:
        setting = yaml.load(s, Loader=yaml.BaseLoader)
    ask_string = setting['ask_gacha']
    tasks = [bot.ask(ask_string)]
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
    with open('gacha.yaml', 'w') as f:
        yaml.dump(gacha, f)
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
