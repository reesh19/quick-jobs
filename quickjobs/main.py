"""Main routing for Quick Jobs App"""
from flask import Flask, render_template, request, redirect
from .model2 import get_jobs

def create_app():
    """Create Flask Application"""
    app = Flask(__name__)

    @app.route("/")
    def root():
        """Redirects to home""" 
        return redirect("/home")


    @app.route("/home", methods=["POST", "GET"])
    def home():
        """Reads inputs, calls model, returns prediction page"""
        if request.method == "POST":
            lc = request.values["location"].split(',')
            jt = request.values['job_titles'].split(',')
            
            id = bool(request.values['ignore_director'])
            re = bool(request.values['remote'])
            
            mr = int(request.values['max_results'])
            nd = int(request.values['n_days'])
            
            message, results, queries = get_jobs(loc=lc, remote=re, job_titles=jt, ignore_director=id, max_results=mr, n_days=nd)

            return render_template("results.html", 
                                    message=message, 
                                    results=results,
                                    queries=queries)
        
        return render_template("home.html")


    return app