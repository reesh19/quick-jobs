"""Main routing for Quick Jobs App"""
from flask import Flask, render_template, request , redirect #, url_for
from .model import get_jobs

def create_app():
    """Create Flask Application"""
    app = Flask(__name__)

    @app.route("/")
    def root():
        """Redirects to home""" 
        return redirect("/home")


    @app.route("/home", methods=["POST", "GET"])
    def home():
        """Reads inputs, calls mmodel, returns prediction page"""
        if request.method == "POST":
            lc = str(request.values["location"]).split(',')
            ts = str(request.values['job_titles']).split(',')
            
            de = bool(request.values['ignore_director'])
            re = bool(request.values['remote'])
            
            rs = int(request.values['max_results'])
            ds = int(request.values['n_days'])
            
            message, results = get_jobs(loc=lc, remote=re, job_titles=ts,
                            ignore_director=de, max_results=rs, n_days=ds)

            return render_template("results.html", 
                                    message=message, 
                                    results=results)
        
        return render_template("home.html")


    return app