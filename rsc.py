from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from getpass import getpass
from bs4 import BeautifulSoup
import urllib.parse
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from os import environ
import subprocess
import json

KEY_ID="9852BA295EEEE573F78741544922766356FA955B"

def set_chrome_options():
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
    chrome_options = FirefoxOptions()
    chrome_options.add_argument(f'user-agent={user_agent}')
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--proxy-server='direct://'")
    chrome_options.add_argument("--proxy-bypass-list=*")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Firefox(options=chrome_options)
    #browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
    return driver

def get_credentials():
    pwd = getpass()
    subprocess.run(['gpg', '--passphrase', pwd, '--output', 'secrets.json', '--decrypt', 'secrets.json.gpg'], capture_output=False, text=False)
    with open('secrets.json') as f:
        parameters = json.load(f)
    
    student_number = parameters['rsc_user']
    password = parameters['rsc_pwd']
    subprocess.run(['rm', 'secrets.json'])
    return student_number, password

def navigate():
    browser.get("https://www.ru.nl/rsc/")
    time.sleep(1)
    browser.find_element(By.XPATH,'/html/body/div[2]/header/div[2]/div[3]/div/div[3]/div[2]/div/div/div/nav/div/ul/li/span/a').click()
    authenticated = False
    while not authenticated:
        student_number, password = get_credentials()
        browser.find_element(By.CSS_SELECTOR,'#inputNummer').send_keys(student_number)
        browser.find_element(By.CSS_SELECTOR,'#inputPassword').send_keys(password)
        time.sleep(1)
        browser_url = browser.current_url
        browser.find_element(By.XPATH, '/html/body/div[3]/article/div[2]/div[2]/form/div[3]/div/button').click()
        time.sleep(1)
        if browser_url == browser.current_url:
            print("wrong credentials, try again")
        else:
            authenticated = True
            print("logged in.")
    time.sleep(1)

def update(browser):
    #browser.find_element(By.XPATH, '/html/body/header/div/div/div/div[3]/div[2]/ul/li[6]/a/span').click()
    #page_source = browser.page_source
    #soup = BeautifulSoup(page_source, 'html.parser')
    #div = soup.find_all('div', class_='columns')[0]
    #inputs = div.contents
    #for input in inputs:
    #    print(input.text)

    browser.find_element(By.XPATH, '/html/body/header/div/div/div/div[3]/div[2]/ul/li[5]/a/span').click()
    page_source = browser.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    pass

def try_to_subscribe(browser, ticket_hour, timer):
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    browser.find_element(By.XPATH, f'/html/body/div[3]/article/table/tbody/tr[{ticket_hour}]/td[3]/a').click()



    time.sleep(1)
    full = True
    while full:
        try:
            browser.find_element(By.XPATH, '/html/body/div[3]/article/div/div[1]/div/a').click()
            time.sleep(1)
        except:
            #error = browser.find_element(By.XPATH, '/html/body/div[3]/article/div/div[1]/div').text.lstrip().rstrip()
            #if error == "Full":
            time.sleep(60*timer)
            browser.refresh()
            continue
        full = False

    browser.find_element(By.XPATH, '/html/body/div[3]/article/article[1]/b/a').click()
    time.sleep(1)
    browser.find_element(By.XPATH, '/html/body/div[3]/article/div/form/fieldset/div/div[2]/div/button').click()
    pass

def subscribe_ticket_hour(browser):
    #navigate to ticket hours page and select all days
    browser.find_element(By.XPATH, '/html/body/header/div/div/div/div[3]/div[2]/ul/li[6]/a/span').click()
    time.sleep(1)
    browser.find_element(By.XPATH, '/html/body/div[3]/article/form/div[2]/label/input').click()

    #get page source, find activities and print them to the user
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    activities = soup.select('input[type="radio"][name="PRESET[Tickets][naam][]"]')
    ticket_hours = []


    #ask user which activity he want to subscribe to
    ticket_hour = None
    while(ticket_hour == None):
        for activity, i in zip(activities[1:], range(1, len(activities))):
            name = activity.next
            print(i, " : ", name)
            ticket_hours.append((str(i), name))
        ticket_hour_input = input("these are the ticket hour offered by the sport center at the moment. To which one do you want to subscribe?(Enter number): ")
        ticket_hour = next(filter(lambda tup: ticket_hour_input in tup, ticket_hours), None)
        if ticket_hour != None:
            yes_no = input(f"So you want to subscribe to {ticket_hour[1]}?(y,n): ")
            if yes_no == "y" or yes_no =="Y":
                ticket_hour = ticket_hour[1]
            else:
                ticket_hour = None
        else:
            print(ticket_hour_input, "was not available, check for typos or that the activity you want to subscribe for is offered")

    encoded_ticket_hour = urllib.parse.quote(ticket_hour)
    browser.get(f'https://publiek.usc.ru.nl/publiek/tickets.php?PRESET%5BTickets%5D%5Bnaam%5D%5B%5D={encoded_ticket_hour}&PRESET%5BTickets%5D%5Bdag%5D%5B%5D=')
    time.sleep(1)
    browser.find_element(By.XPATH, '/html/body/header/div/div/div/div[1]/ul/li[3]/a').click()
    #get all the available activities
    ticket_hours = BeautifulSoup(browser.page_source, 'html.parser').find_all('tr', class_ = 'clickabletr')
    tickets = list(map(lambda x: (x.contents[1].text.rstrip(), x.contents[2].text.rstrip().replace('\n', ''), 
                             x.contents[3].text.rstrip().replace('\n', ''), x.contents[5].text.rstrip(), x.contents[4].text.rstrip().replace('\n', '').lstrip()), ticket_hours))
    
    ticket_hour = None
    while(ticket_hour == None):
        for (ticket, i) in zip(tickets, range(1,len(tickets)+1)):
            print(i, ") ","date:", ticket[0], " time:", ticket[1],
                    " activity:", ticket[2],
                    " Teacher:", ticket[3], "\n")
        ticket_hour = int(input("these are the ticket hour offered by the sport center at the moment. To which one do you want to subscribe?(Enter number): "))
        if ticket_hour in range(1,len(tickets)+1):
            yes_no = input(f"So you want to subscribe to {tickets[ticket_hour-1]}?(y,n): ")
            if yes_no == "y" or yes_no =="Y":
                try_to_subscribe(browser, ticket_hour, 0.05)
            else:
                ticket_hour = None
        else:
            ticket_hour = None
    pass

def subscribe_course(course_name):
    pass

#set options for chrome driver
browser = set_chrome_options()

#navigate to rsc page and login
navigate()

#ask user if he/she/they want to subscribe to ticket hour or course
#print("do you want to subscribe to a Ticket hour(T) or a Course(C)?")
request = "T"
# request = input("Enter C or T: ")

if request == "T":
    subscribe_ticket_hour(browser)
    print("subscribed") 
else:
    browser.find_element(By.XPATH, '/html/body/header/div/div/div/div[3]/div[2]/ul/li[5]/a/span').click()
    pass
    




