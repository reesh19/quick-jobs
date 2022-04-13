from googlesearch import search
from datetime import datetime as dt
from datetime import timedelta as td
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.by import By
from country_list import countries_for_language

import requests
import time
import os
import re

class QuickJobs(object):
    def __init__(self, loc=None, remote=True, job_titles=None, ignore_director=True, max_results=100, n_days=5):
        self.loc = loc
        self.remote = remote
        self.job_titles = job_titles
        self.ignore_director = ignore_director
        self.max_results = max_results
        self.n_days = n_days

        self.countries = self.get_countries()

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
        self.ds_undesired = ['senior', 
                             'sr.',
                             'staff',
                             'lead', 
                             'principal', 
                             'director']
        self.ds_jobs = ['machine learning', 
                        'data scientist', 
                        'data analyst',
                        'technical analyst',
                        'consultant',
                        'builtin-url',
                        'builtin-redirect',
                        'workable-url']
        self.ds_locs = ['Los Angeles', 
                        'Culver City', 
                        'Coupertino', 
                        'Santa Monica', 
                        'California']

        self.urls = ['jobs.lever.co/*', 
                     'apply.workable.com/*', 
                     'boards.greenhouse.io/*', 
                     'jobs.jobvite.com/*', 
                     'builtin.com/job/*']

        self.agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15'

        self.lever = dict()
        self.workable = dict()
        self.greenhouse = dict()
        self.jobvite = dict()
        self.builtin = dict()
        self.other = dict()
        self.all_jobs = dict()
        self.crawl_error = dict()

        print('Building queries...')
        self.queries = self.build_queries()
        print('Done!')
        print('Execute .crawl(), then check inspect with .get_info()')


    def __repr__(self):
        return self.get_info()


    def get_info(self):
        _ = [self.lever, self.workable, self.greenhouse, self.jobvite, self.builtin, self.other, self.crawl_error]

        __ = ['lever', 'workable', 'greenhouse', 'jobvite', 'builtin', 'other', 'crawl_error']
        
        try:
            _count = 0

            for i in _:
                _count += len(i)

            _message = f'Found {_count} new jobs in the past {self.n_days} days.'

            print(_message)
            
            print('\n\nCounts')
            print('----------------')

            for i, j in zip(__, _):
                print(f'{i}: {len(j)}')

            print('\n\nErrors')
            print('----------------')

            for k, v in self.crawl_error.items():
                print(f'{k}: {v}')
        
        except:
            print('404... Nothing to display yet. Have you called the crawl() method yet?')
        
        return


    def get_countries(self):
        _ = dict(countries_for_language('en'))
        _.__delitem__('US')
        _.__delitem__('CA')
        _['UK'] = 'United Kingdom'
        _['EU'] = 'Europe'

        return {country.lower():None for country in _.values()}


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
                if url not in self.all_jobs:
                    self.all_jobs[url] = None

                    if 'workable' not in url:
                        try:
                            req = session.get(url)
                            soup = bs(req.content, 'html.parser')

                        except:
                            continue

                    if 'builtin' in url:
                        if soup.find('div', {'class':'remove-text'}) is not None:
                            continue

                        try:
                            _url = soup.body.findChild('div', attrs={'class': 'apply-now-result'}).get_attribute_list('data-path')[0]

                            _req = session.get(_url)
                            _soup = bs(_req.content, 'html.parser')

                            try:
                                title = _soup.title.text.lower()
                            
                            except:
                                title = 'builtin-redirect'

                        except:
                            try:
                                title = soup.find('title').text.split('-')[0].lower()
                                details = soup.find('span', {'class': 'company-address'}).text.lower()

                                title = title + details

                            except:
                                title = 'builtin-url'
                    
                    elif 'lever' in url:
                        #Find title using different elements in the url
                        try:
                            title = soup.find('div', {'class': 'posting-headline'}).findChild('h2').text.lower()
                        except:
                            try:
                                title = soup.find('div', {'class': 'posting-headline'}).findChild('h1').text.lower()
                            except:
                                try:
                                    title = soup.find('div', {'class': 'posting-headline'}).text.lower()
                                except:
                                    try:
                                        title = soup.find('div', {'class': 'section page-centered posting-header'}).text.lower()
                                    except:
                                        try:
                                            title = soup.title.text.lower()

                                        except Exception as e:
                                            if url not in self.crawl_error:
                                                self.crawl_error[url] = e
                                            
                                            continue

                        # Try finding loc using different elements in the url
                        try:
                            details = soup.find('div', {'class': 'posting-categories'}).findChildren('div')[0].text.lower()
                        except:
                            try:
                                _details = soup.find('div', {'class': 'posting-categories'}).findChildren('div')

                                details = ''
                                
                                for i in _details:
                                    details += i.text.lower() + ' '
                            
                            except:
                                pass

                        details = re.sub(' +', '', details)

                        if details:
                            title = title + ' ' + details
                    
                    elif 'workable' in url:
                        try:
                            _ = url.split('/')
                            __ = 'https://apply.workable.com/api/v2/accounts/'
                            api_call = __ + _[3] + '/jobs/' + _[5]

                            data = session.get(api_call).json()
                            title = data["title"]
                            _details = data["location"].values()
                            details = ''
                            for i in _details:
                                if i:
                                    details += f'{i}, '
                            
                            title = title.lower() + ' ' + details.lower()

                        except Exception as e:
                            if url not in self.crawl_error:
                                self.crawl_error[url] = e
                            continue
                    
                    elif 'greenhouse' in url:
                        try:
                            title = soup.find('h1', {'class': 'app-title'}).text.strip().lower()

                            details = soup.find('div', {'class': 'location'}).text.replace('\n', '').strip().lower()

                            details = re.sub(' +', ' ', details)
                            
                            title = title + ' ' + details

                        except:
                            try:
                                title = soup.find('div', {'id': 'header'}).text.replace('\n', '').strip().lower() 
                                title = re.sub(' +', ' ', title)

                            except Exception as e:
                                if url not in self.crawl_error:
                                    self.crawl_error[url] = e
                                continue
                    
                    elif 'jobvite' in url:
                        try:                            
                            title = soup.find('h2', attrs={'class': 'jv-header'}).text.replace('\n', '').strip().lower()

                            details = soup.find('p', attrs={'class': 'jv-job-detail-meta'}).text.replace('\n', '').strip(' ').lower()

                            details = re.sub(' +', '', details)

                            title = title + ' ' + details

                        except Exception as e:
                            if url not in self.crawl_error:
                                self.crawl_error[url] = e
                            continue
                        
                    else:
                        try:
                            title = soup.title.text.lower()

                        except:
                            try:
                                _title = soup.find_all('h1')
                            except:
                                try:
                                    _title = soup.find_all('h2')
                                except:
                                    if url not in self.crawl_error:
                                        self.crawl_error[url] = e
                                    continue
                                
                            title = ''
                                
                            for i in _title:
                                title += i.text.lower() + ' '
                        
                    if self.job_titles == self.ds_titles:
                        if any(job in title for job in self.ds_jobs):
                            if not any(country in title for country in self.countries):
                                if any(i in url for i in ['lever', 'workable', 'greenhouse', 'jobvite']):
                                    clean_url = self.clean_url(url=url)

                                    if 'lever' in clean_url:
                                        self.lever[clean_url] = title

                                    elif 'workable' in clean_url:
                                        self.workable[clean_url] = title

                                    elif 'greenhouse' in clean_url:
                                        self.greenhouse[clean_url] = title

                                    elif 'jobvite' in clean_url:
                                        self.jobvite[clean_url] = title
                                    
                                elif 'builtin' in url:
                                        self.builtin[url] = title

                                else:
                                    self.other[url] = title

                    else:
                        if any(job in title.lower() for job in self.job_titles):
                            # if not any(country in title.lower() for country in self.countries):
                            try:
                                clean_url = self.clean_url(url=_url, title=title)

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
                                clean_url = self.clean_url(url=url, title=title)

                                res[clean_url] = title

                    time.sleep(1)

                else:
                    continue

            if res:
                try:
                    first_key = list(res.keys())[0]

                    if 'lever' in first_key:
                        self.lever.update(res)

                    elif 'workable' in first_key:
                        self.workable.update(res)

                    elif 'greenhouse' in first_key:
                        self.greenhouse.update(res)

                    elif 'jobvite' in first_key:
                        self.jobvite.update(res)

                    elif 'builtin' in first_key:
                        self.builtin.update(res)
                    
                    else:
                        self.other.update(res)

                except:
                    pass

            time.sleep(2)

        return


    def clean_url(self, url):
        if url.endswith('apply') or url.endswith('apply/') or url.endswith('#app') or url.endswith('#app/'):
            return url
        
        else:
            if 'lever' in url:
                _url = url.split('/')

                if len(_url[4]) == 36:
                    url = 'https://jobs.lever.co/' + _url[3] + '/' + _url[4] + '/apply'

            elif 'workable' in url:
                if url.split('/')[-2] == 'j':
                    if url.endswith('/'):
                        url = url + 'apply/'

                    else:
                        url = url + '/apply/'

            elif 'greenhouse' in url:
                if '#app' not in url:
                    if url.endswith('/'):
                        url = url + '#app'
                    
                    else:
                        url = url + '/#app'

            elif 'jobvite' in url:
                if 'apply' not in url:
                    if url.endswith('/'):
                        url = url + 'apply/'

                    else:
                        url = url + '/apply/'
                
            return url


    def lever_apps(self):
        browser = webdriver.Safari()
        count = 0

        for url in self.lever.keys():
            count += 1

            try:
                browser.switch_to.new_window('tab')
                browser.get(url)

            except Exception as e:
                print(f'{url} FAILED: {e}')
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
                captcha = browser.find_element(By.XPATH, "//div[@id='checkbox']")
                browser.execute_script("arguments[0].scrollIntoView();", captcha)
                browser.execute_script("arguments[0].click();", captcha)

            except:
                pass

            try:
                consent_box = browser.find_element(By.NAME, 'consent[marketing]')
                browser.execute_script("arguments[0].scrollIntoView();", consent_box)
                browser.execute_script("arguments[0].click();", consent_box)

            except:
                pass

            if count == len(self.lever):
                print('All done!')
                time.sleep(99999999999999)


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
            firstname.send_keys(self.my_info['name1'])

            lastname = browser.find_element(By.NAME, 'lastname')
            lastname.send_keys(self.my_info['name2'])

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
    try:
        qj = QuickJobs(job_titles='ds')

        if qj.queries:
            qj.crawler()
        
        return qj
    
    except Exception as e:
        print(e)
        pass


if __name__ == '__main__':
    qj = QuickJobs(job_titles='ds')
    
    if qj.queries:
        qj.crawler()
    
    