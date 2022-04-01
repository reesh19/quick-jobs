from os import system

from asyncio import sleep
from multiprocessing.connection import wait
from signal import pause
from turtle import delay
from googlesearch import search
from datetime import datetime as dt
from datetime import timedelta as td
from bs4 import BeautifulSoup as bs
import requests
import time

titles = ["data scientist", "machine learning"]
locs = ['Los Angeles', 
        # 'Burbank', 
        # 'Glendale', 
        'Culver City', 
        'Coupertino', 
        # 'Palo Alto', 
        'Santa Monica',
        'California']

def get_jobs(loc=None, remote=False, job_titles=None, ignore_director=True, max_results=20, n_days=3):
    """
    Performs hyper-precise job searches on 4 popular job boards
    -----------------------------------------------------------

    loc (str):
        City/Country/Region to search jobs in, default behavior is to search 
        without geographic restrictions

            Jobs in Los Angeles:
                > get_jobs(loc='los angeles')

            Jobs in France:
                > get_jobs(loc='france')


    remote (bool):
        While True, only remote jobs will be considered. 
        Default value is False.

            ONLY remote jobs:
                > get_jobs(remote=True)

            All jobs:
                > get_jobs(remote=False)


    job_titles (iterable, str):
        Exact job title(s) to search for, if none are specified a list of Data 
        Science related job titles will be used

            Single title:
                > get_jobe(job_titles='Propulsion Engineer')

            Multiple titles:
                > get_jobs(job_titles=['Data Engineer','Cook','Librarian'])


    ignore_director (bool):
        If True, job titles which include the word 'Director' will be ignored


    max_results (int):
        Maximum number of results (per job board)

            > get_jobs(max_results=2) --> 8 results (max)
                2 results * 4 job boards = 8

            > get_jobs(max_results=15) --> 60 results (max)
                15 results * 4 job boards = 60


    n_days (int):
        Number of days to retroactively search

            Jobs listed in the last 1 day / last 24 hours: 
                > get_jobs(n_days=1)
            
            Jobs listed in the last 4 days / 96 hours:
                > get_jobs(n_days=4)

    -----------------------------------------------------------------------

    ex: 
        Search for Fireman jobs, 40 results max, in Alaska, all remote, posted 
        in the last 2 days:

        > get_jobs('alaska', True, 'fireman', 10, 2)

    """
    urls = ['jobs.lever.co/*',
            'apply.workable.com/*',
            'boards.greenhouse.io/*/jobs',
            'jobs.jobvite.com',
            'builtin.com/job/*',
            'jobs.dice.com',
            'stackoverflow.com/jobs']

    s = ''

    if job_titles:

        if job_titles == 'ds':
            job_titles = titles

        if type(job_titles) == str:
            s += f""""{job_titles}" """

        elif type(job_titles) == list and all(type(i) == str for i in job_titles):
            n = 0

            for i in job_titles:
                s += f""""{i}" """
                n += 1

                if n < len(job_titles):
                    s += 'OR '

        else: pass

    if loc:

        if loc == 'ds':
            loc = locs

        if type(loc) == str:
            s += f""""{loc}" """

        elif type(loc) == list and all(type(i) == str for i in loc):
            l = 0

            for i in loc:
                s += f""""{i}" """
                l += 1

                if l < len(loc):
                    s += 'OR '

        else: pass

    if remote:
        s += 'remote '

    if ignore_director: 
            s += "-Director -Principal -Lead"

    dtformat = "%Y-%m-%d"
    t0 = dt.now() - td(n_days)
    t_str = t0.strftime(dtformat)

    queries = [f"""{s} site:{url} after:{t_str}""" for url in urls]

    agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15'

    results = []
    count = 0

    for i in queries:
        res = dict()
        session = requests.Session()
        session.headers['User-Agent'] = agent

        for url in search(i, stop=max_results, pause=2, user_agent=agent):
            try:
                req = session.get(url)
                soup = bs(req.content, 'html.parser')
                title = soup.title.get_text()

                if title.startswith('Job'):
                    title = title.strip('Job Application for ')

                if job_titles == ["data scientist", "machine learning"]:
                    if any(job in title.lower() for job in ['machine learning', 'data scientist', 'mle', 'ml engineer', 'data science']) and url not in res:
                            res[url] = title
                            count += 1
                else:
                    if any(job in title.lower() for job in job_titles):
                        if url not in res:
                            res[url] = title
                            count += 1
                        # res[f'{url}'] = title
                        # count += 1

                time.sleep(.1)
            
            except: continue

        results.append(res)

    message = f'Found {count} jobs posted in the last {n_days} day(s)'
    
    # results = []
    # message = ''

    return message, results, queries

class QuickJobs(object):
    def __init__(self, loc, remote, job_titles, ignore_director, max_results, n_days, bloom_urls):
        loc=None, remote=False, job_titles=None, ignore_director=True, max_results=20, n_days=3
        self.loc = None
        self.remote = False
        self.job_titles = None
        self.ignore_director = True
        self.max_results = 20
        self.n_days = 7
        self.bloom_urls = None
        self.message, self.results, self.queries = self.search()
        self.jobs_df = self.get_jobs_df()



    def __repr__(self):
        return f"""\n{self.message}:\n\n{self.results}\n"""


    def search(self) -> list[dict]:
        params = gen_request_parameters(query=self.query, 
                                        results_per_call=100,
                                        granularity=None, 
                                        tweet_fields='author_id',
                                        user_fields='username',
                                        expansions='author_id')

        rs = ResultStream(request_parameters=params,
                        max_results=1000,
                        max_pages=1,
                        **self.search_args)

        tweets = list(rs.stream())

        return tweets


    def get_tweets_df(self) -> pd.DataFrame:
        users = {}

        for i in self.tweets:
            for u in i['includes']['users']:
                id = u['id']
                username = u['username']

                if id not in users:
                    users[id] = username

        results = {}
        docs = set()

        for i in self.tweets:
            for j in i['data']:
                _ = j['text'].lower().replace('\n\n', ' ').replace('\n', ' ')

                if len(_) <= 300:
                    doc = self.nlp(_)
                    plural = ['us', 'we', 'our']

                    if any([i in doc.text for i in plural]):
                        continue

                    else: 
                        user = users[j['author_id']]

                        if not docs:
                            results[user] = [doc.text, j['id']]

                        else: 
                            similar = [d.similarity(doc) for d in docs]

                            if all([j <= .99 for j in similar]):
                                if user not in results:
                                    results[user] = [doc.text, j['id']]

                                else: 
                                    results[user].append([doc.text, j['id']])

                    docs.add(doc)

        df = pd.DataFrame(data=results.items(), columns=['username', 'data'])
        df['tweet_id'] = df['data'].apply(lambda x: x[1])
        df['tweet_text'] = df['data'].apply(lambda x: x[0])
        df.drop(columns=['data'], inplace=True)

        return df

    def load_targets(self, targets: list[int]) -> str:
        s = ''

        for i in targets:
            _id = self.tweets_df.iloc[i].tweet_id
            _user = self.tweets_df.iloc[i].username

            s += f"https://twitter.com/{_user}/status/{_id} "

        return s

if __name__ == '__main__':
    system('clear')
    print(pyfiglet.figlet_format("tutor reesh", font="cybermedium"))

    query = input('Example query: (("dog" OR "cat" OR "dragon") (adopt OR rescue) (free OR "no charge")) lang:en -is:retweet -has:media -is:quote \n\nEnter your search query(or type "reesh", no quotes): ')

    if query == 'reesh':
        query = """(("take my" OR "do my" OR "good money") (math OR calc OR calculus OR precalc OR stats OR statistics OR stat OR chemistry OR chem OR biology OR bio OR physics OR phys OR phy) (test OR exam OR assignment OR midterm OR final OR class OR course) -affordable -"let me help") lang:en -is:retweet -has:media -has:links -has:mentions -is:quote"""

    m = MathAlacarte(query=query)

    print(m,'\n')

    while True:
        choice1 = input('Continue? (y/n): ')

        if choice1 == 'y':
            while True:
                targets = input('\nEnter tweet indices to load, separated by a comma: ')
                targets = [int(i) for i in targets.replace(' ', '').split(',')]

                if isinstance(targets, list) and all([isinstance(i, int) for i in targets]):

                    try:
                        urls = m.load_targets(targets)
                        print(f'\nurls: {urls}\n')

                    except ValueError:
                        print('Welp, something broke. One more try? (y/n): ')

                        if input() == 'y':
                            continue

                        else:
                            print('Okay... BYE!')
                            break

                    choice2 = input('Open in browser? (y/n): ')

                    if choice2 == 'y':
                        system(f'open {urls}')
                        exit()

                    else: exit()

                else:
                    choice3 = input('\nInvalid input. Try again? (y/n): \n')

                    if choice3 == 'y':
                        continue

                    else: exit()

        else:
            print('Okay... BYE!')
            exit()