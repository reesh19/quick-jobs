from googlesearch import search
from datetime import datetime as dt
from datetime import timedelta as td
from pytz import timezone as tz


def get_jobs(loc=None, remote=None, job_titles=None, ignore_director=None, max_results=None, n_days=None):
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

    # if job_titles:
    #     titles = job_titles
    
    # else:
    #     titles = ["Data Scientist",
    #               "Data Analyst",
    #               "Data Engineer",
    #               "Machine Learning Engineer",
    #               "ML Engineer",
    #               "Machine Learning Scientist",
    #               "Quantitative Analyst",
    #               "Quantitative Researcher"]
    
    s = ''

    if loc:
        if type(loc) == str:
            s += f""""{loc}" """
        
        elif type(loc) == list and type(loc[0]) == str:
            l = 0
            
            for i in loc:
                s += f""""{i}" """
                l += 1
                if l < len(loc):
                    s += 'OR '
        else:
            # message = 'That is not a valid location(s) friend...'
            return # message
    
    if remote:
        s += """"remote" """

    n = 0

    if type(job_titles) == str:
        s += f""""{job_titles}" """
    
    elif type(job_titles) == list and type(job_titles[0]) == str:
        for i in job_titles:
            s += f""""{i}" """
            n += 1
            if n < len(job_titles):
                s += 'OR '
    
    else:
        # message = 'Whoopsie, no valid job title(s) found... Try again?'
        return # message
    
    if ignore_director: 
            s += '-director'

    dtformat = "%Y-%m-%d"
    yesterday = dt.now().astimezone(tz('US/Pacific')) - td(n_days)
    t_str = yesterday.astimezone(tz('US/Pacific')).strftime(dtformat)

    queries = [f""""{s} site:https://{url}/* after:{t_str}""" for url in urls]

    results = []

    count = 0

    for i in queries:
        for j in search(i, stop=max_results, pause=3):
            results.append(j)
            count += 1

    message = f'Found {count} jobs posted in the last {n_days} day(s):'

    return message, results