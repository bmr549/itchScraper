
import urllib
from time import sleep

from requests_html import HTMLSession
from selenium import webdriver


# Constants
from selenium.webdriver import FirefoxProfile

username = input("Username: ")
password = input("Password: ")
bundleUrl = input("BundleURL: ")
session = HTMLSession()
loginUrl = "https://itch.io/login"
rawDownloadLinks = []
gamePageLinks = []
driver_path = "C:\Program Files\GeckoDriver\geckodriver-v0.27.0-win64\geckodriver.exe"
profile = FirefoxProfile()
profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/zip, application/x-zip-compressed, application/x-compressed, application/pdf, application/octet-stream, application/epub")
profile.set_preference("browser.helperApps.neverAsk.openFile", "application/zip, application/x-zip-compressed, application/x-compressed, application/pdf, application/octet-stream, application/epub")
profile.set_preference("broswer.download.manager.showWhenStarting", False)
profile.set_preference("browser.download.dir", "D:\Downloads")
profile.set_preference("browser.download.folderList", 2)
profile.set_preference("browser.helperApps.alwaysAsk.force", False)
profile.set_preference("browser.pdf.launchDefaultEdgeAsApp", False)
driver = webdriver.Firefox(firefox_profile=profile, executable_path=driver_path)


def setLoginPayload(username, password, csrfToken):
    loginPayload = {
        "username": username,
        "password": password,
        "csrf_token": csrfToken
    }
    return loginPayload


def urlEncode(token):
    return urllib.parse.unquote(token)


def getCookie(data):
    csrfToken = session.cookies[data]
    return urlEncode(csrfToken)


def loginToItch(url):
    csrfToken = getCookie("itchio_token")
    loginPayload = setLoginPayload(username, password, csrfToken)
    print(loginPayload)
    return session.post(url, data=loginPayload)


def getTwoFactorAuthToken(url):
    token = url[28:]
    token = token.replace(f"?username={username}", "")
    return urlEncode(token)


def sendTwoFactorAuthentication(url):
    twoFactorCode = input("Input Two-Factor Code: ")
    twoFactorPayload = {
        "code": twoFactorCode,
        "csrf_token": getTwoFactorAuthToken(url)
    }
    return session.post(url, data=twoFactorPayload)

def getPageLinks(page):
    allLinks = page.html.absolute_links
    linkCount = 0
    for i in allLinks:
        if "/download/" in i and "/bundle/" not in i:
            gamePageLinks.append(i)
            linkCount += 1
    print(f"Found {linkCount} item(s)")

def iteratePages():
    page = 1
    while page < 60:
        print(f"On Page {page} of 59")
        result = session.get(f"{bundleUrl}?page={page}")
        getPageLinks(result)
        page += 1

def getBundlePages():
    result = session.get(loginUrl) # Preempt the site so that tokens generate
    result = loginToItch(result.url)
    result = sendTwoFactorAuthentication(result.url)
    # We should be logged in by this point

    iteratePages()


def downloadPage(url):
    driver.get(url)
    downloadButtons = driver.find_elements_by_class_name("download_btn")
    currentDownload = 0
    while currentDownload < len(downloadButtons):
        downloadButtons[currentDownload].click()
        sleep(2)
        currentDownload += 1

def runSelenium(username, password):
    driver.get(loginUrl)
    login = driver.find_element_by_name("username").send_keys(username)
    password = driver.find_element_by_name("password").send_keys(password)
    submit = driver.find_element_by_class_name("button").click()
    authentication = driver.find_element_by_name("code").send_keys(input("2FA Code: "))
    submit = driver.find_element_by_class_name("button").click()

    page = 60
    currentButton = 1
    while page < 60:
        driver.get(f"{bundleUrl}?page={page}")
        print(f"Page: {page}")
        unclaimedButtons = driver.find_elements_by_name("action")
        buttons = len(unclaimedButtons)
        print(f"Unclaimed Items: {buttons}")
        while currentButton <= buttons:
            print(f"Button: {currentButton}")
            unclaimedButtons = driver.find_elements_by_name("action")
            unclaimedButtons[0].click()
            currentButton += 1
            driver.back()
        page += 1
        currentButton = 1


def main():
    runSelenium(username, password)
    getBundlePages()
    currentGame = 1
    games = len(gamePageLinks)
    while currentGame < games:
        downloadPage(gamePageLinks[currentGame])
        currentGame += 1

main()