from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import os
import sys
import pprint


def login(usr, pwd):
    # enter in username
    user = browser.find_element_by_css_selector('#user_session_username')
    user.send_keys(usr)

    # enter in password
    user_password = browser.find_element_by_css_selector('#user_session_password')
    user_password.send_keys(pwd)

    # click login
    login_button = browser.find_element_by_css_selector('#user_session_submit')
    login_button.click()


def get_page(url):
    browser.get(url)


def logout():
    browser.get("https://www.vhlcentral.com/logout")


def check_element_existence(element_path):
    try:
        browser.find_element_by_xpath(element_path)
    except NoSuchElementException:
        return False
    return True


# this function is for getting file paths for files inside executable
def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


print('Peter Edmonds: AutoVHLv1.4\n USE AT YOUR OWN RISK!')

while True:
    username = input("enter your username: ")
    password = input("enter you password: ")
    print('vhl-username:' + str(username))
    print('vhl-password:' + str(password))
    correct = input('is this correct? (y/n)')
    if correct == 'y':
        break
    else:
        pass

# start browser
browser = webdriver.Chrome(executable_path=resource_path('chromedriver.exe'))

# go to vhl home
get_page("https://www.vhlcentral.com/home")

# login user
login(username, password)

# go to homepage
get_page('http://descubre3.vhlcentral.com/home/?SS=on')

# set window name
window_main = browser.window_handles[0]

# all urls give 'no assignment' until further notice, vhl only displays 10 assignments at a time
hw_urls = ['no_assignment'] * 11

# THIS BLOCK GATHERS ALL URLS FROM USER

# for every assignment
for assignment_number in range(11):
    # make sure the link actually exists, if not it will remain as no_assignment
    if check_element_existence('/html/body/div/div/div/div/div[4]/div[2]/div[1]/div[2]/div[3]/div/dl[1]/ul/li'
                               '[' + str(assignment_number) + ']/a'):
        # i use 'assignment_number + 1' so we never try to index the li[0] ([li] starts at 1)
        hw = browser.find_element_by_xpath('/html/body/div/div/div/div/div[4]/div[2]/div[1]/div[2]/div[3]/div/dl[1]'
                                           '/ul/li[' + str(assignment_number) + ']/a')
        # click on link
        hw.click()
        # name popup window as window_new so we can change its state
        window_new = browser.window_handles[1]
        # switch to the popup window
        browser.switch_to.window(window_new)

        # this block makes sure a valid url is passed in
        while True:
            # constantly set url to be window url
            hw_urls[assignment_number] = browser.current_url
            # by default, all tabs have url 'about:blank'
            if hw_urls[assignment_number] == 'about:blank':

                # if the url is still default, continue loop
                continue
            else:
                # if url is valid, break out of loop
                hw_urls[assignment_number] = browser.current_url
                break

        # close window
        browser.close()

        # return to main window
        browser.switch_to.window(window_main)

# THIS BLOCK GETS ALL VHL ANSWERS FROM VHL SCHOOL USER
logout()
login('vhlschool', 'vhlschool')
answers_book = []
for y in range(11):
    for x in range(1):
        answers_book.append(["no answer"])

# for every assignment
f = open("vhl.txt", "w+")
f.close()

# this does all the assignments
for assignment_number in range(11):
    # if there is an assignment to be done
    if hw_urls[assignment_number] != 'no_assignment':
        # load assignment page
        get_page(hw_urls[assignment_number])

        # click submit
        submit = browser.find_element_by_name('submitRecital')
        submit.click()
        browser.save_screenshot('assignment' + str(assignment_number) + '.png')

        answers_raw = browser.find_elements_by_xpath(
            '//li[@class="answer_correction"]/label/span | //span[@class="correct"] | //li[@color="green"]/label/span')
        answer_text = []
        answer_final = []
        for answer in answers_raw:
            answer_text.append(answer.text)
        for answer in answer_text:
            if " or " in answer:
                scrub = answer[:answer.find(" or ")]
                answer_final.append(scrub)
            else:
                scrub = answer
                answer_final.append(scrub)
        answers_book[assignment_number] = answer_final
        f = open("vhl.txt", "a+")
        f.write('ASSIGNMENT #' + str(assignment_number) + ': ' + ' URL: ' + str(hw_urls[assignment_number]) + '  ')
        counter = 1
        for answer in answer_final:
            f.write(str(answer) + ', ')
        f.write("\n")
        f.close()
pp = pprint.PrettyPrinter()

pp.pprint(answers_book)
logout()
login(username, password)
for assignment_number in range(11):
    # if there is an assignment to be done
    if hw_urls[assignment_number] != 'no_assignment':
        # load assignment page
        get_page(hw_urls[assignment_number])

        # if assignment is a multi assignemnt
        if check_element_existence(
                '//form[contains(@name, "RecitalForm")]//input[contains(@type, "text")]') and check_element_existence(
                '//form[contains(@name, "RecitalForm")]//input[contains(@type, "radio")]'):
            current_input = browser.find_element_by_xpath('//html/body')
            while current_input.tag_name != 'select' and current_input.tag_name != 'input':
                current_input.send_keys(Keys.TAB)
                current_input = browser.switch_to.active_element

            for question in range(len(answers_book[assignment_number])):
                current_input = browser.switch_to.active_element
                if current_input.tag_name == 'select':
                    print('question ' + str(question) + ' is a dropdown')
                    dropdown = browser.switch_to.active_element
                    select = Select(dropdown)
                    select.select_by_visible_text(answers_book[assignment_number][question])
                elif current_input.tag_name == 'input':
                    if current_input.get_attribute('type') == 'radio':
                        print('question' + str(question) + 'is a button')
                        if check_element_existence(
                        '//form[contains(@name, "RecitalForm")]//input[contains(@type, "radio")]') and check_element_existence(
                        '//label/span[contains(text(),"cierto")]') and check_element_existence(
                        '//label/span[contains(text(),"falso")]'):
                            print('question ' + str(question) + ' is a true / false')
                        else:
                            # answer as a normal button
                            print('question ' + str(question) + ' is a normal button')
                            options_root = browser.switch_to.active_element
                            options_parent = options_root.find_element_by_xpath('..')
                            options_double_parent = options_parent.find_element_by_xpath('..')
                            print(str(options_parent.tag_name))
                            options_text = options_double_parent.find_elements_by_xpath('./li/label/span')

                            # for every option in the question
                            for option in options_text:
                                print('option text = ' + str(option.text))
                                # get parent web element
                                option_label = option.find_element_by_xpath('..')
                                print('option label = ' + str(option_label))

                                # get id of parent, this id matches the id of the corresponding button
                                option_id = option_label.get_attribute('for')
                                print('option id = ' + str(option_id))

                                # select correct button
                                input_box = browser.find_element_by_id(option_id)

                                # if the book answer is == to the text of the option
                                if answers_book[assignment_number][question] == option.text:
                                    print('answer is ' + str(option.text))
                                    input_box.click()
                                    break
                    else:
                        print('question ' + str(question) + ' is a text box')
                        # answer as text box
                        current_input.send_keys([answers_book[assignment_number][question]])
                current_input.send_keys(Keys.TAB)
            input()
        # if form is made of text boxes
        elif check_element_existence('//form[contains(@name, "RecitalForm")]//input[contains(@type, "text")]'):
            print(str(assignment_number) + '= text forms')
            boxes = browser.find_elements_by_xpath('//form[contains(@name, "RecitalForm")]//input'
                                                   '[contains(@type, "text")]')
            # using an index object (cb) is not pythonic. ill fix this using enumerations but i don't wanna break stuff
            cb = 0
            for box in boxes:
                box.send_keys(answers_book[assignment_number][cb])
                cb += 1
            input()
        # else if form is buttons with true / false
        elif check_element_existence(
                '//form[contains(@name, "RecitalForm")]//input[contains(@type, "radio")]') and check_element_existence(
            '//label/span[contains(text(),"cierto")]') and check_element_existence(
            '//label/span[contains(text(),"falso")]'):
            print(str(assignment_number) + '= true / false')
            options = browser.find_elements_by_xpath('//label/span')
            for question in range(len(answers_book[assignment_number])):
                q_ans = answers_book[assignment_number][question]
                if q_ans == 'cierto':
                    button_input = options[question * 2]
                    button_input.click()
                elif q_ans == 'falso':
                    button_input = options[(question * 2) + 1]
                    button_input.click()
            input()

        # else if form is buttons
        elif check_element_existence('//form[contains(@name, "RecitalForm")]//input[contains(@type, "radio")]'):
            print(str(assignment_number) + '= buttons')
            # get web element of all question options
            # for every question in the assignment
            for questions in range(len(answers_book[assignment_number])):
                options = browser.find_elements_by_xpath('//label/span')
                # for every option in the question
                for option in options:
                    # get parent web element
                    option_label = option.find_element_by_xpath('..')
                    # get id of parent, this id matches the id of the corresponding button
                    option_id = option_label.get_attribute('for')
                    # select correct button
                    input_box = browser.find_element_by_id(option_id)
                    # if the book answer is == to the text of the option
                    if answers_book[assignment_number][questions] == option.text:
                        # click
                        input_box.click()
                        break
            input()

        # form is a dropdown
        elif check_element_existence('//form[contains(@name, "RecitalForm")]//input'):
            print(str(assignment_number) + '= dropdown')
            dropdowns = browser.find_elements_by_xpath('//select')
            for question in range(len(answers_book[assignment_number])):
                select = Select(dropdowns[question])
                select.select_by_visible_text(answers_book[assignment_number][question])
            input()

    else:
        pass
