import asyncio
import datetime
import subprocess
import chardet
from data.sites import Sites
from data import db_session

db_sess = db_session.create_session()
websites = [[i, db_sess.query(Sites).filter(Sites.id == i).link] for i in db_sess.query(Sites)]


async def ping_website(website):
    ping_process = await asyncio.create_subprocess_exec(
        "ping", "-n", "3", website,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await ping_process.communicate()
    return website, ping_process.returncode, stdout, stderr


async def run_pings():
    while True:
        results = await asyncio.gather(*[ping_website(website[1].split("//")[1] if "//" in website[1] else website[1]) for website in websites])
        for result in results:
            res_id = result[0][0]
            site_ping = result[2]
            result = chardet.detect(site_ping)
            decoded = site_ping.decode(result['encoding'])
            result_ping = decoded.split("\r\n")[-2].split(',')[-1].split(' = ')[-1].split()[0]
            work_db = db_session.create_session()
            site = Sites(
                id=res_id,
                link=work_db.query(Sites).filter(Sites.id == res_id).link,
                owner_id=work_db.query(Sites).filter(Sites.id == res_id).owner_id,
                ping=result_ping,
                check_time=datetime.now(),
                description=work_db.query(Sites).filter(Sites.id == res_id).description,
                ids_feedbacks=work_db.query(Sites).filter(Sites.id == res_id).ids_feedbacks
            )
            db_sess.add(site)
            db_sess.commit()
        await asyncio.sleep(120)  # ждем 2 минуты перед повторной проверкой


asyncio.run(run_pings())  # запуск тестиорования сайтов перекинуть в main