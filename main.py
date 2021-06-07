import asyncio
import time
from lxml import html
import yaml

from aiowikibot import Bot


async def main():
    with open('setting.yml') as s:
        setting = yaml.load(s, Loader=yaml.BaseLoader)

    bot = Bot(setting['username'], setting['password'], setting['api_url'])
    await bot.login_wiki()

    title = 'User:txrtanzi/sandbox/auto'
    tasks = [bot.read_parsed('User:Txrtanzi/榛名')]
    results = await asyncio.gather(*tasks)

    # print(results)
    # for result in results:
    #     print(result)
    tree = html.fromstring(results[0])
    # print(tree.text_content().rstrip())
    with open('result.txt', 'w', encoding='utf-8') as result_file:
        # for result in results:
        #     result_file.write(result)
        result_file.write(results[0])
    tasks = [bot.write_wiki(title, tree.text_content().rstrip(), 'Edited by bot', minor=True, bot=True)]
    results = await asyncio.gather(*tasks)
    for result in results:
        print(result)

    await bot.close()

if __name__ == "__main__":
    # asyncio.set_event_loop_policy(None)
    loop = asyncio.get_event_loop()
    start = time.perf_counter()
    loop.run_until_complete(main())
    end = time.perf_counter()
    print(f"用时{end - start}s")
