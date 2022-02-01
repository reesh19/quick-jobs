from googlesearch import search
from datetime import datetime as dt
from datetime import timedelta as td
from pytz import timezone as tz
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen

titles = ["Data Scientist",
          "Machine Learning Engineer",
          "ML Engineer",
          "Machine Learning",
          "Data Science"]

def get_jobs(loc="los angeles", remote=False, job_titles=["Data Scientist", "Machine Learning Engineer", "ML Engineer", "Machine Learning", "Data Science"], ignore_director=True, max_results=20, n_days=3):
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
        While True, only remote jobs will be considered, however it is recommended 
        to set 'loc' to your home country to avoid non-relevant results.

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
    urls = ['jobs.lever.co', 
            'apply.workable.com', 
            'boards.greenhouse.io', 
            'jobs.jobvite.com/*/job']
    
    s = ''

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
    
    if remote:
        s += """"remote" """
    
    if ignore_director: 
            s += '-director'

    dtformat = "%Y-%M-%D"
    yesterday = dt.now().astimezone(tz('US/Pacific')) - td(n_days)
    t_str = yesterday.astimezone(tz('US/Pacific')).strftime(dtformat)

    queries = [f""""{s} site:https://{url}/* after:{t_str}""" for url in urls]

    results = [] 
    # results = [[list0],[list1], ..] 
    # results[0] = [job0, job1, ...]
    # results[0][0] = (job title, job url)

    count = 0

    for i in queries:
        res = []
        
        for url in i:
            
            for reply in search(url, stop=max_results, pause=3):
                soup = bs(urlopen(reply))
                
                res.append((soup.title.get_text(), reply))
                count += 1
        
        results.append(res)

    message = f'Found {count} jobs posted in the last {n_days} day(s):'
    
    return message, results