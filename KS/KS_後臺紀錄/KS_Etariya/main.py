import undetected_chromedriver as uc
import time
import sqlite3
from datetime import datetime

EMAIL = 'cameronqoo@gmail.com'
PASS = 'ailent32123'


if __name__ == '__main__':

    con = sqlite3.connect('./ks.db')
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS etariya(total, buyer, follow, covered, datetime)")

    driver = uc.Chrome(use_subprocess=True) 
    driver.get("https://www.kickstarter.com/login?then=/projects/moaideas/board-game-invitation-to-etariya-island/dashboard?ref=creator-nav") 
    driver.maximize_window()
    input('===PASS ANY KEY TO CONTINUE===')

    driver.find_element(uc.By.ID, 'user_session_email').send_keys(EMAIL)
    driver.find_element(uc.By.ID, 'user_session_password').send_keys(PASS)
    driver.find_element(uc.By.NAME, 'commit').submit()

    while True:
        con = sqlite3.connect('./ks.db')
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS etariya(total, buyer, follow, covered, datetime)")

        data = (
            driver.find_element(uc.By.CSS_SELECTOR, '.stats-numbers').find_elements(uc.By.TAG_NAME, 'h1')[0].text,
            driver.find_element(uc.By.CSS_SELECTOR, '.stats-numbers').find_elements(uc.By.TAG_NAME, 'h1')[2].text,
            driver.find_elements(uc.By.CSS_SELECTOR, '.w25p.mr1.mb2.mb0-md')[0].text.split('\n')[0],
            driver.find_elements(uc.By.CSS_SELECTOR, '.w25p.mr1.mb2.mb0-md')[1].text.split('\n')[0],
            datetime.now()
        )
        cur.execute("INSERT INTO etariya VALUES(?, ?, ?, ?, ?)", data)
        con.commit()
        con.close()
        driver.find_element(uc.By.CSS_SELECTOR, '.bttn.bttn-medium.bttn-secondary.fill-bttn-icon.hover-fill-bttn-icon.keyboard-focusable').click()

        time.sleep(3600)
        driver.refresh()
    
    driver.close()