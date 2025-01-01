# app/utils/LinkedInManager.py
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
import time
import os
from PyPDF2 import PdfReader
from webdriver_manager.chrome import ChromeDriverManager


class LinkedInManager:
    def __init__(self, username, password, experienceLevel):
        self.username = username
        self.password = password
        self.driver = None
        self.isLogin = False
        self.easyApplyState = False
        self.experienceLevel = experienceLevel
        self.num_ofJobs_added = 0

    def login(self):
        print("start Logging in...")
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Run in headless mode
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("user-agent=Mozilla/5.0")

        # Use the installed chromedriver
        self.driver = webdriver.Chrome(service=Service("/usr/local/bin/chromedriver"), options=options)

        try:
            print("self.driver = webdriver.Chrome(options=options) OK !!")
            self.driver.get('https://www.linkedin.com/login')
            time.sleep(3)

            try:
                print(f"Attempting to log in as {self.username}...")
                username_field = self.driver.find_element(By.ID, 'username')
                username_field.send_keys(self.username)
                time.sleep(1)
            except:
                print("Username already entered.")
                return True
            try:
                print("Entering password...")
                password_field = self.driver.find_element(By.ID, 'password')
                password_field.send_keys(self.password)
                time.sleep(1)
                password_field.send_keys(Keys.RETURN)
            except:
                print("Login form not found; checking if already logged in.")
                if "feed" in self.driver.current_url:
                    print("Already logged in!")
                    self.isLogin = True
                    return True
                else:
                    print("Login failed or additional steps required.")
                    return False

            time.sleep(5)
            if "checkpoint/challenge" in self.driver.current_url:
                print("Verification required. Please complete the process manually.")
                time.sleep(30)
            elif "feed" in self.driver.current_url:
                self.isLogin = True
                print("Login successful!")
                return True
            else:
                print("Login failed.")
                return False

        except Exception as e:
            print(f"error with Login")
            return False

    def search_jobs(self, job_title):
        if not self.isLogin:
            print("Not logged in. Please log in first.")
            return

        job_listings = self.__get_job_list(job_title, False)
        if job_listings:
            self.get_job_details(job_listings)
            time.sleep(2)

        return self.num_ofJobs_added

    def search_jobs_for_titles(self, job_titles: list, maxNumberOfJobsTosearch: int):
        if not self.isLogin:
            print("Not logged in. Please log in first.")
            return []

        all_jobs = []
        for job_title in job_titles:
            print(f"Searching jobs for: {job_title}")
            job_listings = self.__get_job_list(job_title, False, maxNumberOfJobsTosearch)
            if job_listings:
                job_details = self.get_job_details(job_listings)
                all_jobs.extend(job_details)  # Add all job details to the list
                time.sleep(2)

        return all_jobs  # Return the list of all job details

    def __get_job_list(self, job_title, easyApply_filter, maxNumberOfJobsTosearch):
        self.driver.get('https://www.linkedin.com/jobs/')
        job_listings = []
        try:
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'input.jobs-search-box__text-input.jobs-search-box__keyboard-text-input'))
            )
            search_box.clear()
            search_box.send_keys(job_title)
            time.sleep(3)
            search_box.send_keys(Keys.RETURN)
            time.sleep(4)

            if not self.__filterJobs(easyApply_filter):
                print("No jobs were found with the required filters.")
                return []

            # XPath to target all job list items
            job_listings_element = self.driver.find_elements(By.XPATH,
                                                             "//li[contains(@class, 'scaffold-layout__list-item') and @data-occludable-job-id]")
            job_listings_len = len(job_listings_element)
            print(f'len of job_listings_element: {job_listings_len}')
            if job_listings_len == 0:
                print("No job listings found after filtering. Please check the filters.")
                return []

            time.sleep(1)
            i = 1
            while i <= job_listings_len:
                try:
                    # Use `find_element` instead of `find_elements` for a single element and correct the XPath
                    job_element = self.driver.find_element(By.XPATH,
                                                           f"(//li[contains(@class, 'scaffold-layout__list-item') and @data-occludable-job-id])[{i}]")
                    job_listings.append(job_element)
                    i += 1
                    if i > maxNumberOfJobsTosearch:
                        break

                except Exception as e:
                    print(f"{i}) No job element found, skipping.", "*" * 40)
                    break  # Exit the loop if no element is found
            if easyApply_filter:
                print(f"found {len(job_listings)} jobs for {job_title} and easyApply_filter")
            else:
                print(f"found {len(job_listings)} jobs for {job_title} and easyApply_filter")

            return job_listings

        except Exception as e:
            print(f"An error occurred in __get_job_list: {str(e).splitlines()[0]}")
            return []


    def get_job_details(self, job_listings):
        print("Start get_job_details function:\n")
        job_details = []  # Collect all job details in this list

        try:
            for index, job in enumerate(job_listings):
                if index > 0 and index % 8 == 0:  # Scroll after processing 10 jobs
                    self.scroll_down_inWebPage("jobs-search-results-list")
                    time.sleep(2)

                try:
                    # Click the job to load its details
                    job.click()
                    time.sleep(3)  # Allow time for the job details to load

                    # Extract company name
                    company_name_element = job.find_element(By.XPATH, ".//div[contains(@class, 'artdeco-entity-lockup__subtitle')]/span")
                    company_name = company_name_element.text.strip()

                    # Extract job link
                    job_element = job.find_element(By.XPATH, ".//a[contains(@class, 'job-card-container__link')]")
                    job_link = job_element.get_attribute('href')

                    # Extract job description
                    job_description_element = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//div[contains(@class, 'jobs-box__html-content') and @id='job-details']")
                        )
                    )
                    job_description = job_description_element.text.strip()

                    # Open job link in a new tab to extract title
                    self.driver.execute_script("window.open(arguments[0]);", job_link)
                    self.driver.switch_to.window(self.driver.window_handles[1])
                    time.sleep(5)

                    # Extract job title
                    title_element = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, 'h1.t-24.t-bold.inline')
                        )
                    )
                    title = title_element.text.strip()

                    # Close the tab and return to the main window
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
                    time.sleep(2)

                    # Append the job details as a tuple to the list
                    job_details.append((company_name, job_description, title, job_link))

                    # Print all details in one line
                    print(f"\n\nJob {index + 1}:\n Company: {company_name},\n Title: {title},\n Description: {job_description},\n Link: {job_link}")
                except Exception as e:
                    print(f"An error occurred while processing job {index + 1}: {e}")
                    if len(self.driver.window_handles) > 1:
                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])

        except Exception as e:
            print(f"An error occurred while retrieving job details: {str(e).splitlines()[0]}")

        return job_details

    def __search_easy_apply(self, user_description, job_listings, resume_text):
        print("start __search_easy_apply function: \n")
        print(f"len(job_listings): {len(job_listings)}\n")
        self.scroll_up_inWebPage("jobs-search-results-list")
        try:
            for index, job in enumerate(job_listings):
                if index == 8:
                    self.scroll_to_middle_inWebPage("jobs-search-results-list")
                    time.sleep(3)
                elif index == 10:
                    self.scroll_down_inWebPage("jobs-search-results-list")
                    time.sleep(2)
                try:
                    company_name_element = job.find_element(By.CLASS_NAME, 'job-card-container__primary-description')
                    company_name = company_name_element.text.strip()

                    job_element = job.find_element(By.CSS_SELECTOR, 'a.job-card-list__title')
                    job_link = job_element.get_attribute('href')

                    self.driver.execute_script("window.open(arguments[0]);", job_link)
                    self.driver.switch_to.window(self.driver.window_handles[1])
                    time.sleep(3)

                    title_element = self.driver.find_element(By.CSS_SELECTOR, 'h1.t-24.t-bold.inline')
                    title = title_element.text.strip()

                    job_description_element = self.driver.find_element(By.CSS_SELECTOR,
                                                                       'div.jobs-box__html-content.jobs-description-content__text')
                    job_description = job_description_element.text.strip()

                    if not self.db_manager.does_job_exist(company_name, title):
                        if self.ensures_acceleration_to_the_position(job_description, title, resume_text,
                                                                     user_description):
                            print(f"Job {index + 1}: {title} is suitable.")
                            if self.__easy_submit_CV():
                                version = 'A' if self.CV == 'A' else 'B'
                                self.db_manager.add_job_toDB(company_name, job_link, title, version, "web")
                                self.num_ofJobs_added += 1
                                print(f"Job {index + 1}) {title} at {company_name} suitable successfully !", "*" * 20,
                                      "\n")
                                time.sleep(2)
                        else:
                            print(f"Job {index + 1}: {title} is not suitable.")
                    else:
                        print(f"Job {index + 1}) {title} at {company_name} already exists in DB", "*" * 20, "\n")

                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
                    time.sleep(5)
                    print(f"Job {index + 1} Details:\nCompany Name: {company_name}\nJob Title: {title}\n")

                except Exception as e:
                    print(f"An error occurred while processing job {index + 1}: {e.args}")
                    if len(self.driver.window_handles) > 1:
                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])

        except Exception as e:
            print(f"An error occurred while searching for jobs: {str(e).splitlines()[0]}")

        finally:
            if self.easyApplyState:
                self.__turns_off_and_on_easy_apply()

    def __send_message_to_hr(self, job_title, company_name, job_link):
        def close_chet():
            try:
                time.sleep(2)
                # Close the chat after sending the message using a more generic XPath
                close_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable(
                        (By.XPATH,
                         "//button[contains(@class, 'msg-overlay-bubble-header__control') and contains(., 'Close your conversation')]")
                    )
                )
                close_button.click()
                time.sleep(4)
                return True
            except Exception as e:
                print(f"Error closing chat: {str(e).splitlines()[0]}")
                return False

        try:
            # Wait for the "Message" button to be present and clickable using XPath
            message_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//button[.//span[text()="Message"]]'))
            )
            hr_connected = self.__connectToHR()
            if hr_connected:
                print("Successfully connected to HR.\n\n")
            else:
                print("Could not connect to HR or no HR found.\n\n")

        except Exception as e:
            print("No HR available.\n\n")
            return False, ""

        # Extract the HR name
        try:
            hr_name_element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(@class,'hirer-card__hirer-information')]//strong[contains(text(), '')]")
                )
            )
            hr_name = hr_name_element.text.strip()
            hr_first_name = hr_name.split()[0]
            print(f"HR Name: {hr_name}, Job Link: {job_link}")
            exist_job = self.db_manager.does_hr_have_job(hr_name, company_name, job_title)
            if exist_job:
                print("You already sent a message about this job.\n", "*" * 40)
                return False, ""
            # Click the "Message" button
            message_button.click()
            time.sleep(3)
        except Exception as e:
            print("No HR name available.")
            close_chet()
            return False, ""

        # Wait for the message div to be present
        try:
            message_div = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.msg-form__contenteditable[contenteditable="true"]')
                )
            )
            message_div.clear()
            # Construct the message string in the correct order
            message = (
                f"Hi {hr_first_name},\n\n"
                f"Hi {hr_first_name},I hope you’re doing well !\n\n"
                f"I’m Yarden, a third-year Software Engineering student. I’m passionate about tackling challenging problems, "
                f"algorithms, and creative thinking—exactly what excites me about the {job_title} role at {company_name}.\n\n"
                "I’ve developed strong problem-solving skills through both my studies and mentoring leadership programs. I believe I can "
                "bring value to your team and would love to chat about how I can contribute.\n\n"
                "I’d be happy to send you my resume and discuss the opportunity further.\n\n"
                "Looking forward to hearing from you!\n\n"
                "Best, Yarden.\n\n"
                f"Here’s the link to the job posting: {job_link}"
            )

            message_div.send_keys(message)
            time.sleep(4)
            send_button = WebDriverWait(self.driver, 5).until(  # Wait for the "Send" button to be present
                EC.presence_of_element_located(
                    (By.XPATH,
                     "//div[contains(@class, 'msg-form__msg-content-container')]//button[@type='submit' and contains(@class, 'artdeco-button--primary') and contains(@class, 'msg-form__send-btn')]")
                )
            )
            send_button.click()  # Click the "Send" button
            time.sleep(3)
        except Exception as e:
            try:
                time.sleep(2)
                send_button_type2 = WebDriverWait(self.driver, 5).until(  # Wait for the "Send" button to be present
                    EC.presence_of_element_located(
                        (By.XPATH, "//button[normalize-space()='Send']")
                    )
                )
                send_button_type2.click()  # Click the "Send" button
                time.sleep(3)
            except Exception as e:
                print(f"Message error: {str(e).splitlines()[0]}")
                close_chet()
                return False, ""

        # mack sleep(2)
        return close_chet(), hr_name

    def __filterJobs(self, easyApply_filter):
        # For 24 hours, remove the comment from the line below
        # self.__jobs_published_last_24_hours()
        # time.sleep(2)

        # Check if jobs were published in the last week
        # if not self.__jobs_published_last_week():
        #     return False
        # time.sleep(2)

        # Verify experience level filter is working
        if not self.__experience_level(self.experienceLevel):
            print("No jobs found matching the experience level.")
            return False
        time.sleep(2)

        # Toggle easy apply filter if needed
        if (easyApply_filter and not self.easyApplyState) or (not easyApply_filter and self.easyApplyState):
            if not self.__turns_off_and_on_easy_apply():
                print("No result for easy Apply filter\n")
                return False

        return True

    def locate_scrollable_element(self, element):
        try:
            # Try locating by class name first
            return WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, element))
            )
        except Exception:
            try:
                # If class name fails, try locating by XPath
                return WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, element))
                )
            except Exception as e:
                print(f"Failed to locate element: {str(e).splitlines()[0]}")
                return None

    def scroll_upDown_inWebPage(self, element):
        scrollable_div = self.locate_scrollable_element(element)
        if scrollable_div:
            self.scroll_down_inWebPage(scrollable_div)
            time.sleep(2)
            self.scroll_up_inWebPage(scrollable_div)

    def scroll_down_inWebPage(self, scrollable_div):
        self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
        time.sleep(2)

    def scroll_up_inWebPage(self, scrollable_div):
        self.driver.execute_script("arguments[0].scrollTop = 0", scrollable_div)
        time.sleep(2)

    def scroll_to_middle_inWebPage(self, element):
        scrollable_div = self.locate_scrollable_element(element)
        if scrollable_div:
            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight / 2", scrollable_div)
            time.sleep(2)

    def scroll_to_quarter_inWebPage(self, element):
        scrollable_div = self.locate_scrollable_element(element)
        if scrollable_div:
            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight / 2", scrollable_div)
            time.sleep(2)

    def __connectToHR(self):
        try:
            # Locate and click on the HR profile link/button
            profile_element = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH,
                     "//div[contains(@class,'hirer-card__hirer-information')]//a[contains(@href, '/in/')]")
                )
            )
            hr_name = profile_element.text.strip().split('\n')[0]
            print(f"HR Name: {hr_name}")
            profile_link = profile_element.get_attribute('href')
            print(f"HR Profile Link: {profile_link}")
            time.sleep(1)
            self.driver.execute_script("window.open(arguments[0]);", profile_link)
            self.driver.switch_to.window(self.driver.window_handles[2])
            time.sleep(6)
        except Exception as e:
            print(f"Could not find HR element or navigate to HR profile: {str(e).splitlines()[0]}")
            return False

        try:
            # Locate and click the "Connect" button with the specific name in aria-label
            connect_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, f"(//button[contains(@aria-label, 'Invite {hr_name} to connect')])[2]")
                )
            )
            connect_button.click()
            time.sleep(2)
        except Exception as e:
            try:
                # Locate and click the "Connect" button with the class 'artdeco-button--primary'
                connect_button_type2 = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable(
                        (By.XPATH,
                         "(//button[contains(@class, 'artdeco-button--primary') and .//span[text()='Connect']])[2]")
                    )
                )
                connect_button_type2.click()
                time.sleep(2)
            except Exception as e:
                try:
                    # Locate and click the "Connect" button with the class 'artdeco-button--secondary' and aria-label
                    connect_button_type3 = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable(
                            (By.XPATH,
                             f"(//button[contains(@aria-label, 'Invite {hr_name} to connect') and contains(@class, 'artdeco-button--secondary')])[1]")
                        )
                    )
                    connect_button_type3.click()
                    time.sleep(2)
                except Exception as e:
                    try:
                        connect_button_type4 = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable(
                                (
                                    By.XPATH,
                                    "//div[@class='pvs-profile-actions__action']//button[span[text()='Connect']]")
                            )
                        )
                        connect_button_type4.click()
                        time.sleep(2)
                    except Exception as e:
                        try:
                            connect_button_type5 = WebDriverWait(self.driver, 5).until(
                                EC.element_to_be_clickable(
                                    (
                                        By.XPATH, f"(//button[@aria-label='Invite {hr_name} Shushan to connect'])[2]")
                                )
                            )
                            connect_button_type5.click()
                            time.sleep(2)

                        except Exception as e:
                            print(f"Cannot find connect button for {hr_name}: {str(e).splitlines()[0]}")
                            self.driver.close()
                            self.driver.switch_to.window(self.driver.window_handles[1])
                            time.sleep(3)
                            return False

        # If prompted, send the connection request without a note
        try:
            send_without_note_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH,
                     "//button[@aria-label='Send without a note' and contains(@class, 'artdeco-button--primary')]")
                )
            )
            send_without_note_button.click()
            print("Connection request sent successfully.")
            time.sleep(3)
        except TimeoutException:
            print("No 'Send now' button found, possibly already connected or another issue.")

        # Send the connection request without a note if prompted
        self.__sendWithoutNote()
        # Close the HR profile tab and return to the main job listing page
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[1])
        time.sleep(3)
        return True

    def extract_text_from_pdf(self, pdf_path):
        text = ""
        with open(pdf_path, "rb") as file:
            reader = PdfReader(file)
            for page in reader.pages:
                text += page.extract_text()
        return text

    def ensures_acceleration_to_the_position(self, job_description, job_title, resume_text, user_description):
        if "intern" in job_title.lower() or "student" in job_title.lower() or "junior" in job_title.lower():
            return True

        if "senior" in job_title.lower() or (not self.__check_experience(job_description, 2)):
            return False

        return True

    def __parse_ai_result(self, ai_result):
        lines = ai_result.split('\n')
        score = 0
        explanation = ""
        for line in lines:
            if "Suitability score" in line:
                score = int(line.split(':')[-1].strip())
            elif "Explanation" in line:
                explanation = line.split(':')[-1].strip()
        return score, explanation

    def __check_experience(self, jobDescription, max_experience):
        lines = jobDescription.split('.')
        for line in lines:
            if 'experience' in line.lower():
                words = line.split()
                for word in words:
                    if word.isdigit():
                        if int(word) > max_experience:
                            return False
        return True

    def __jobs_published_last_24_hours(self):
        try:
            # Wait for the "Date posted" filter button to be clickable and then click it
            date_posted_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, 'searchFilter_timePostedRange'))
            )
            date_posted_button.click()
            time.sleep(2)

            # Wait for the "Past 24 hours" option to be clickable and then click it
            select_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//span[text()="Past 24 hours"]/ancestor::label'))
            )
            select_button.click()
            time.sleep(1)

            # Wait for the "Show results" button to be clickable and then click it
            show_results_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH,
                                            '//button[contains(@aria-label, "Apply current filter to show") and contains(@class, "artdeco-button--primary")]/span[text()[contains(.,"Show")]]'))
            )
            show_results_button.click()
            time.sleep(3)

        except Exception as e:
            print(f"An error occurred while applying the filter: {str(e).splitlines()[0]}")

    def __jobs_published_last_week(self):
        try:
            # Wait for the "Date posted" filter button to be clickable and then click it
            date_posted_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, 'searchFilter_timePostedRange'))
            )
            date_posted_button.click()
            time.sleep(2)

            # Wait for the "Past 24 hours" option to be clickable and then click it
            select_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//span[text()="Past week"]/ancestor::label'))
            )
            select_button.click()
            time.sleep(1)

            # Wait for the "Show results" button to be clickable and then click it
            show_results_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH,
                                            '//button[contains(@aria-label, "Apply current filter to show") and contains(@class, "artdeco-button--primary")]/span[text()[contains(.,"Show")]]'))
            )
            show_results_button.click()
            time.sleep(3)
            return True

        except Exception as e:
            print(f"An error occurred while applying the filter: {str(e).splitlines()[0]}")
            return False

    def __turns_off_and_on_easy_apply(self):
        try:
            # Try finding the element by its aria-label attribute
            easy_apply_button = self.driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Easy Apply filter."]')
            easy_apply_button.click()
            time.sleep(2)
            self.easyApplyState = not self.easyApplyState
            return True

        except Exception as e:
            print(f"An error occurred while applying the filter: {str(e).splitlines()[0]}")
            return False

    # if dont work copy __easy_submit_CV function from test file
    def __easy_submit_CV(self):
        print("Start __easy_submit_CV function \n")
        next_button_count = 0
        time.sleep(5)

        # 1) Try to click the easy_apply_button
        try:
            easy_apply_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "(//div[@class='jobs-apply-button--top-card'])[1]"))
            )
            easy_apply_button.click()
            time.sleep(3)
        except Exception as e:
            print("This job was already submitted.")
            return False

        # 2) Try to click the continue_applying_button
        try:
            continue_applying_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH,
                                            '(//button[@aria-label="Easy Apply to Signal Processing Research and Algorithm Developer at ASTERRA"])[1]'))
            )
            continue_applying_button.click()
            time.sleep(3)
        except Exception as e:
            try:
                continue_applying_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH,
                                                '(//button[@aria-label="Easy Apply to Signal Processing Research and Algorithm Developer at ASTERRA"])[2]'))
                )
                continue_applying_button.click()
                time.sleep(3)
            except Exception as e:
                print("No continue_applying_button needed or available.")

        # 3) Try to go to the next step
        try:
            while True:
                next_button = self.driver.find_element(By.XPATH,
                                                       "(//button[contains(@id, 'ember') and contains(@aria-label, 'next')])[1]")
                next_button.click()
                time.sleep(3)
                next_button_count += 1
                try:
                    confirmed_element = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//label[@data-test-text-selectable-option__label='Confirmed']"))
                    )
                    confirmed_element.click()
                    time.sleep(2)
                except Exception as e:
                    print("No 'Confirmed' element found or needed.")
                    print(f"Error: {str(e).splitlines()[0]}")
        except Exception as e:
            print(f"Error clicking 'Next' button after {next_button_count} times: {str(e).splitlines()[0]}")

        # 4) Try to find all input fields and fill them
        try:
            # Find all input text fields within the 'ph5' div
            input_text_fields = self.driver.find_elements(By.XPATH,
                                                          "//div[@class='ph5']//input[@type='text' and contains(@class, 'text')]")
            # Fill all input text fields with '1'
            if input_text_fields:
                for input_field in input_text_fields:
                    try:
                        input_field.clear()
                        input_field.send_keys('1')
                        print(f"Filled input field with ID: {input_field.get_attribute('id')} with '1'")
                        time.sleep(3)
                    except Exception as e:
                        print(
                            f"Failed to fill input field with ID: {input_field.get_attribute('id')}. Error: {str(e).splitlines()[0]}")
            else:
                print("No input text fields found.\n")

            try:
                yes_label = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//div[@class='ph5']//label[@data-test-text-selectable-option__label='Yes']"))
                )
                yes_label.click()
                time.sleep(1)
            except Exception as e:
                print(f"Error: {str(e).splitlines()[0]}")

        except Exception as e:
            print(f"An error occurred: {str(e).splitlines()[0]}")
            return False

        self.__select_yes_for_uniface_experience("Yes")

        # 5) Try to click the review button
        try:
            review_button = self.driver.find_element(By.XPATH, "//button[span[text()='Review']]")
            review_button.click()
            time.sleep(3)
        except Exception as e:
            print("No 'Review' option found in __easy_submit_CV function!")
            print(f"Error: {str(e).splitlines()[0]}")
            return False

        # 6) Try to submit the application
        try:
            submit_button = self.driver.find_element(By.XPATH, '//button[@aria-label="Submit application"]')
            submit_button.click()
            time.sleep(3)
            done_button = self.driver.find_element(By.XPATH, "//button[contains(@class, 'artdeco-modal__dismiss')]")
            done_button.click()
            time.sleep(3)
            print("Application submitted successfully.")
            return True
        except Exception as e:
            print("This job was already submitted.")
            print(f"Error: {str(e).splitlines()[0]}")
            return False

    def __sendWithoutNote(self):
        try:
            send_without_note_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH,
                     "//button[@aria-label='Send without a note' and contains(@class, 'artdeco-button--primary')]")
                )
            )
            send_without_note_button.click()
            print("Connection request sent successfully.")
            time.sleep(3)
        except TimeoutException:
            print("No 'Send now' button found, possibly already connected or another issue.")

    def __experience_level(self, level):
        try:
            # Locate the button by its ID and click it
            experience_level_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@id='searchFilter_experience']"))
            )
            experience_level_button.click()
            print("Clicked on 'Experience level' button")

            time.sleep(2)
            print("Clicked on 'All filters' button")

            if level.lower() == 'entry level':
                # Click on "Internship" checkbox
                internship_checkbox = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@id='experience-1']/following-sibling::label"))
                )
                internship_checkbox.click()
                time.sleep(1)
                print("Selected 'Internship' filter")

                # Click on "Entry level" checkbox
                entry_level_checkbox = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@id='experience-2']/following-sibling::label"))
                )
                entry_level_checkbox.click()
                time.sleep(1)
                print("Selected 'Entry level' filter")
                #
                # associate_level_checkbox = WebDriverWait(self.driver, 5).until(
                #     EC.element_to_be_clickable((By.XPATH, "//input[@id='experience-3']/following-sibling::label"))
                # )
                # associate_level_checkbox.click()
                # time.sleep(1)
                # print("Selected 'Associate level' filter")
            else:
                # Click on "Mid-Senior level" checkbox
                mid_senior_checkbox = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@id='experience-4']/following-sibling::label"))
                )
                mid_senior_checkbox.click()
                print("Selected 'Mid-Senior level' filter")

            time.sleep(2)
            # Show results and check if the number of results is greater than zero
            show_results_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH,
                                            "(//button[contains(@aria-label, 'Apply current filter to show') and contains(@class, 'artdeco-button')])[2]"))
            )
            res = show_results_button.text.split()
            show_results_button.click()
            print("Clicked on 'Show results' button")
            time.sleep(3)

            if int(res[1]) > 0:
                print(f"{res[1]} jobs found matching your experience level.")
                return True

            print("No results found for your experience level.")
            return False
        except Exception as e:
            print(f"An error occurred: {str(e).splitlines()[0]}")
            return False

    def __try_click_buttons(self, xpaths):
        """Try to find and click a button from a list of possible XPaths."""
        for i, xpath in enumerate(xpaths):
            try:
                button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                button.click()
                time.sleep(3)
                print(f"Clicked with Xpath {i + 1}\n")
                return True
            except Exception as e:
                print(
                    f"Failed to click button number {i + 1} for XPath ending with: {xpath[-20:]}, Error: {str(e).splitlines()[0]}\n")
                continue
        return False

    def __select_yes_for_uniface_experience(self, answer="Yes"):
        try:
            # Locate the dropdown element
            dropdown_element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH,
                                            "//select[contains(@id, 'text-entity-list-form-component-formElement') and contains(@aria-describedby, 'multipleChoice-error')]"))
            )
            # Click the dropdown to reveal options
            dropdown_element.click()
            time.sleep(1)

            # Find the option element within the dropdown list
            option_xpath = f"//select[contains(@id, 'text-entity-list-form-component-formElement')]//option[text()='{answer}']"
            option_element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, option_xpath))
            )
            option_element.click()

            print(f"Selected '{answer}' from the dropdown for Uniface experience.")
            time.sleep(2)

        except TimeoutException:
            print("The dropdown for Uniface experience could not be found or was not clickable within the time limit.")
        except Exception as e:
            print(f"An error occurred while selecting the option '{answer}': {str(e).splitlines()[0]}")

    def logout(self):
        if not self.isLogin:
            print("Not logged in. No need to log out.")
            return
        try:
            self.driver.get('https://www.linkedin.com/m/logout/')
            time.sleep(3)

            self.driver.quit()
            self.isLogin = False
            print("Logged out successfully.")
        except Exception as e:
            print(f"An error occurred during logout: {str(e).splitlines()[0]}")
