from googlesearch import search
from datetime import datetime as dt
from datetime import timedelta as td
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import time
import os

class QuickJobs(object):
    def __init__(self, loc=None, remote=True, job_titles=None, ignore_director=True, max_results=50, n_days=5):
        self.loc = loc
        self.remote = remote
        self.job_titles = job_titles
        self.ignore_director = ignore_director
        self.max_results = max_results
        self.n_days = n_days

        self.my_info = {'fullname': 'Ricardo Rodriguez',
                        'name1': 'Ricardo', 
                        'name2': 'Rodriguez',
                        'headline': 'Data Scientist',
                        'email': 'rodriguezr235@gmail.com',
                        'phone': '7083743618',
                        'address': 'Los Angeles, CA',
                        'current_company': 'INI-P Solutions, LLC',
                        'languages': 'English, Spanish',
                        'linkedin': 'https://www.linkedin.com/in/ricardo-a-rodriguez-f/',
                        'github': 'https://github.com/reesh19',
                        'res': '/Users/reesh/Projects/qj/quickjobs/resume.pdf',
                        'website': 'https://ricardo-rodriguez.medium.com/',
                        'salary': '$100,000'}
        self.ds_titles = ["data analyst", "data scientist", "machine learning"]
        self.ds_undesired = ['senior', 'sr.', 'staff', 'lead']
        self.ds_jobs = ['machine learning', 
                        'data scientist', 
                        'mle', 
                        'ml engineer', 
                        'data science', 
                        'data analyst', 
                        'technical services engineer']
        self.ds_locs = ['Los Angeles', 
                        'Culver City', 
                        'Coupertino', 
                        'Santa Monica', 
                        'California']
        self.urls = ['jobs.lever.co/*', 
                     'apply.workable.com/*', 
                     'boards.greenhouse.io/*/jobs', 
                     'jobs.jobvite.com', 
                     'builtin.com/job/*']
        self.agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15'

        self.lever = dict()
        self.workable = dict()
        self.greenhouse = dict()
        self.jobvite = dict()
        self.builtin = dict()
        self.other = dict()

        self.results = []
        self.crawl_error = []
        self.automation_error = []
        
        self.count = 0

        self.queries = self.build_queries()
        self.message = f'Found {self.count} new jobs in the past {self.n_days} days.'


    def __repr__(self):
        return self.message


    def build_queries(self):
        s = ''

        if self.job_titles:
            if self.job_titles == 'ds':
                self.job_titles = self.ds_titles

            if isinstance(self.job_titles, str):
                s += f""""{self.job_titles}" """

            elif isinstance(self.job_titles, list) and all(isinstance(i, str) for i in self.job_titles):
                n = 0

                for i in self.job_titles:
                    s += f""""{i}" """
                    n += 1

                    if n < len(self.job_titles):
                        s += 'OR '

            else: pass

        if self.loc:

            if self.loc == 'ds':
                self.loc = self.ds_locs

            if isinstance(self.loc, str):
                s += f""""{self.loc}" """

            elif isinstance(self.loc, list) and all(isinstance(i, str) for i in self.loc):
                l = 0

                for i in self.loc:
                    s += f""""{i}" """
                    l += 1

                    if l < len(self.loc):
                        s += 'OR '

            else: pass

        if self.remote:
            s += 'remote '

        if self.ignore_director: 
                s += "-Director -Principal -Lead -Senior -Sr."

        dtformat = "%Y-%m-%d"
        t0 = dt.now() - td(self.n_days)
        t_str = t0.strftime(dtformat)

        queries = [f"""{s} site:{url} after:{t_str}""" for url in self.urls]
        
        return queries


    def crawl(self):
        for i in self.queries:
            res = dict()
            session = requests.Session()
            session.headers['User-Agent'] = self.agent

            for url in search(i, stop=self.max_results, pause=2, user_agent=self.agent):
                if url not in res:
                    try:
                        req = session.get(url)
                        soup = bs(req.content, 'html.parser')

                    except Exception as e:
                        self.crawl_error.append(f'{e}')
                        continue

                    if 'builtin' in url:
                        try:
                            soup.find_element(By.XPATH, '//div[@class="remove-text"]')
                            continue
                        except:
                            try:
                                _url = soup.body.findChild('div', attrs={'class': 'apply-now-result'}).get_attribute_list('data-path')[0][0:-16]

                                req = session.get(_url)
                                soup = bs(req.content, 'html.parser')

                                title = soup.head.findChild('meta', attrs={'name': 'description'}).get('content').lower()
                            except:
                                try:
                                    title = soup.title.get_text().lower()
                                except:
                                    try:
                                        title = soup.body.main.get_text().replace('\n', ' ').lower()
                                    except Exception as e:
                                        self.crawl_error.append(f'{e}')
                                        continue
                        
                    else:
                        title = soup.title.get_text()
                        
                    if title.startswith('Job'):
                        title = title.strip('Job Application for ')

                    if self.job_titles == self.ds_titles:
                        if any(job in title.lower() for job in self.ds_jobs):
                            try:
                                clean_url = self.url_cleaner(url=_url, title=title)

                                if 'lever' in clean_url:
                                    self.lever[clean_url] = title

                                elif 'workable' in clean_url:
                                    self.workable[clean_url] = title

                                elif 'greenhouse' in clean_url:
                                    self.greenhouse[clean_url] = title

                                elif 'jobvite' in clean_url:
                                    self.jobvite[clean_url] = title
                                
                                elif 'builtin' in clean_url:
                                    self.builtin[clean_url] = title

                                else:
                                    self.other[clean_url] = title

                            except:
                                clean_url = self.url_cleaner(url=url, title=title)
                                res[clean_url] = title

                    else:
                        if any(job in title.lower() for job in self.job_titles):
                            try:
                                clean_url = self.url_cleaner(url=_url, title=title)

                                if 'lever' in clean_url:
                                    self.lever[clean_url] = title

                                elif 'workable' in clean_url:
                                    self.workable[clean_url] = title

                                elif 'greenhouse' in clean_url:
                                    self.greenhouse[clean_url] = title

                                elif 'jobvite' in clean_url:
                                    self.jobvite[clean_url] = title
                                
                                elif 'builtin' in clean_url:
                                    self.builtin[clean_url] = title

                                else:
                                    self.other[clean_url] = title

                            except:
                                clean_url = self.url_cleaner(url=url, title=title)

                                res[clean_url] = title

                    time.sleep(1)

                else:
                    continue

            if res:
                cheat = res.keys().__str__().split("""', '""")[1]

                if 'lever' in cheat:
                    self.lever.update(res)

                elif 'workable' in cheat:
                    self.workable.update(res)

                elif 'greenhouse' in cheat:
                    self.greenhouse.update(res)

                elif 'jobvite' in cheat:
                    self.jobvite.update(res)

                elif 'builtin' in cheat:
                    self.builtin.update(res)

                else:
                    self.other.update(res)

            time.sleep(2)

        return self.get_job_count()


    def clean_urls(self, url, title):
        if any(key_word in title for key_word in self.ds_undesired):
            if not ('scientist' in title or 'engineer' in title):
                if 'lever' in url:
                    if not '/apply' in url:
                        if url.endswith('/'):
                            url += 'apply/'

                        else:
                            url += '/apply/'

                elif 'workable' in url:
                    if not '/apply' in url:
                        if url.endswith('/'):
                            url += 'apply/'

                        else:
                            url += '/apply/'

                elif 'greenhouse' in url:
                    if not '#app' in url:
                        if url.endswith('/'):
                            url += '#app'
                        
                        else:
                            url += '/#app'

                elif 'jobvite' in url:
                    if not '/apply' in url:
                        if url.endswith('/'):
                            url += 'apply/'

                        else:
                            url += '/apply/'

        else:
            if 'lever' in url:
                if not '/apply' in url:
                    if url.endswith('/'):
                        url += 'apply/'

                    else:
                        url += '/apply/'

            elif 'workable' in url:
                if not '/apply' in url:
                    if url.endswith('/'):
                        url += 'apply/'

                    else:
                        url += '/apply/'

            elif 'greenhouse' in url:
                if not '#app' in url:
                    if url.endswith('/'):
                        url += '#app'
                    
                    else:
                        url += '/#app'

            elif 'jobvite' in url:
                if not '/apply' in url:
                    if url.endswith('/'):
                        url += 'apply/'

                    else:
                        url += '/apply/'
            
        return url


    def get_job_count(self):
        self.count = len(self.lever) + len(self.workable) + len(self.greenhouse) + len(self.jobvite) + len(self.builtin) + len(self.other)

        return


    def lever_apps(self):
        browser = webdriver.Safari()

        for url in self.lever.keys():
            try:
                browser.switch_to.new_window('tab')
                browser.get(url)
            except Exception as e:
                print(f'{url} FAILED: {e}')
                self.errors.append(url)
                continue

            time.sleep(2)
            
            fullname = browser.find_element(By.NAME, 'name')
            fullname.send_keys(self.my_info['fullname'])

            email = browser.find_element(By.NAME, 'email')
            email.send_keys(self.my_info['email'])

            phone = browser.find_element(By.NAME, 'phone')
            phone.send_keys(self.my_info['phone'])

            org = browser.find_element(By.NAME, 'org')
            org.send_keys(self.my_info['current_company'])

            try:
                linkedin = browser.find_element(By.NAME, 'urls[LinkedIn]')
                linkedin.send_keys(self.my_info['linkedin'])

                github = browser.find_element(By.NAME, 'urls[GitHub]')
                github.send_keys(self.my_info['github'])

                website = browser.find_element(By.NAME, 'urls[Other]')
                website.send_keys(self.my_info['website'])
            except:
                pass

            try:
                salary = browser.find_element(By.XPATH, "//textarea[@name='cards[6aa3a729-c53d-43f5-9ddd-8c18bfd2a146][field0]']")
                salary.send_keys(self.my_info['salary'])
            except:
                pass

            try:    
                workauth0 = browser.find_element(By.XPATH, 
                    "//input[@type='radio' and @name='cards[dcbfc765-5272-44d1-a58d-0ce56afd20f4][field0]' and @'Yes']")
                browser.execute_script("arguments[0].scrollIntoView();", workauth0)
                browser.execute_script("arguments[0].click();", workauth0)

                workauth1 = browser.find_element(By.XPATH, 
                    "//input[@type='radio' and @name='cards[dcbfc765-5272-44d1-a58d-0ce56afd20f4][field1]' and @'No']")
                browser.execute_script("arguments[0].scrollIntoView();", workauth1)
                browser.execute_script("arguments[0].click();", workauth1)    
            except:
                pass

            resume = browser.find_element(By.XPATH, "//input[@type='file']")
            resume.send_keys('/Users/reesh/Projects/qj/quickjobs/resume.pdf')

            time.sleep(3)

            try:
                consent_box = browser.find_element(By.NAME, 'consent[marketing]')
                browser.execute_script("arguments[0].scrollIntoView();", consent_box)
                browser.execute_script("arguments[0].click();", consent_box)
            except:
                pass

        return
        

    def greenhouse_apps(self):
        browser = webdriver.Safari()

        for url in self.greenhouse.keys():
            try:
                browser.switch_to.new_window('tab')
                browser.get(url)
            except Exception as e:
                print(f'{url} FAILED: {e}')
                self.errors.append(url)
                continue

            time.sleep(2)

            firstname = browser.find_element(By.NAME, 'job_application[first_name]')
            firstname.send_keys(self.my_info['firstname'])

            lastname = browser.find_element(By.NAME, 'job_application[last_name]')
            lastname.send_keys(self.my_info['lastname'])

            email = browser.find_element(By.NAME, 'job_application[email]')
            email.send_keys(self.my_info['email'])

            phone = browser.find_element(By.NAME, 'job_application[phone]')
            phone.send_keys(self.my_info['phone'])

            try:
                linkedin = browser.find_element(By.PARTIAL_LINK_TEXT, 'LinkedIn')
                linkedin.send_keys(self.my_info['linkedin'])

                github = browser.find_element(By.PARTIAL_LINK_TEXT, 'GitHub')
                github.send_keys(self.my_info['github'])
            except:
                pass

            resume = browser.find_element(By.XPATH, "//input[@type='file']")
            resume.send_keys('/Users/reesh/Projects/qj/quickjobs/resume.pdf')

            time.sleep(3)
        
        return


    def workable_apps(self):
        browser = webdriver.Safari()

        for url in self.workable.keys():
            try:
                browser.switch_to.new_window('tab')
                browser.get(url)
            except Exception as e:
                print(f'{url} FAILED: {e}')
                self.errors.append(url)
                continue

            time.sleep(2)

            firstname = browser.find_element(By.NAME, 'firstname')
            firstname.send_keys(self.my_info['firstname'])

            lastname = browser.find_element(By.NAME, 'lastname')
            lastname.send_keys(self.my_info['lastname'])

            email = browser.find_element(By.NAME, 'email')
            email.send_keys(self.my_info['email'])

            phone = browser.find_element(By.NAME, 'phone')
            phone.send_keys(self.my_info['phone'])

            address = browser.find_element(By.NAME, 'address')
            address.send_keys(self.my_info['address'])



            try:
                linkedin = browser.find_element(By.NAME, 'linkedin')
                linkedin.send_keys(self.my_info['linkedin'])

                github = browser.find_element(By.NAME, 'github')
                github.send_keys(self.my_info['github'])
                
            except:
                pass

            resume = browser.find_element(By.XPATH, "//input[@type='file']")
            resume.send_keys('/Users/reesh/Projects/qj/quickjobs/resume.pdf')

            time.sleep(3)
        
        return
    

    def jobvite_apps(self):
        browser = webdriver.Safari()

        for url in self.jobvite.keys():
            try:
                browser.switch_to.new_window('tab')
                browser.get(url)
            except Exception as e:
                print(f'{url} FAILED: {e}')
                self.errors.append(url)
                continue

            time.sleep(2)

            firstname = browser.find_element(By.XPATH, "//input[@autocomplete='given-name']")
            firstname.send_keys(self.my_info['firstname'])

            lastname = browser.find_element(By.XPATH, "//input[@autocomplete='family-name']")
            lastname.send_keys(self.my_info['lastname'])

            email = browser.find_element(By.XPATH, "//input[@autocomplete='email']")
            email.send_keys(self.my_info['email'])

            address = browser.find_element(By.XPATH, "//input[@autocomplete='Full Address*']")
            address.send_keys(self.my_info['address'])

            phone = browser.find_element(By.XPATH, "//input[@autocomplete='tel']")
            phone.send_keys(self.my_info['phone'])

            try:
                compensation = browser.find_element(By.XPATH, "//input[@type='number']")
                compensation.send_keys(self.my_info['compensation'])

            except:
                pass

            try:
                languages = browser.find_element(By.XPATH, "//input[@id='jv-field-y6fLXfwN']")
                languages.send_keys(self.my_info['languages'])

            except:
                pass

            try:
                where_find = browser.find_element(By.XPATH, "//select[@name='input-ymvuXfw2']//child::option[@label='Other']")
                where_find.click()

            except:
                pass

            try:
                work_status = browser.find_element(By.XPATH, "//select[@name='input-yfJRXfww']//child::option[@label='Permanent Resident']")
                work_status.click()

            except:
                pass

            resume = browser.find_element(By.XPATH, "//input[@id='file-input-0']")
            resume.send_keys('/Users/reesh/Projects/qj/quickjobs/resume.pdf')

            time.sleep(3)
        
        return
    

    def builtin_apps(self):
        s = ''

        for i in self.builtin.keys():
            s += f"""'{i} '"""

        os.system(f'open {s}')

        return


    def other_apps(self):
        for i in self.other.keys():
            s += f"""'{i} '"""

        os.system(f'open {s}')

        return


def main():
    qj = QuickJobs(job_titles='ds')

    if qj.queries:
        qj.crawler()

    if qj.lever:
        qj.lever_apps()
    if qj.workable:
        qj.workable_apps()
    if qj.greenhouse:
        qj.greenhouse_apps()
    if qj.jobvite:
        qj.jobvite_apps()
    if qj.builtin:
        qj.builtin_apps()
    if qj.other:
        qj.other_apps()

    return


if __name__ == '__main__':
    main()