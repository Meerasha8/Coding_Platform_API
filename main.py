from flask import Flask,jsonify,render_template
import os
from dotenv import load_dotenv
import requests
from math import ceil
from selenium import webdriver
from bs4 import BeautifulSoup
import re
import time

load_dotenv()


LEETCODE_URL = os.getenv("LEETCODE_URL")

CODEFORCES_URL = os.getenv("CODEFORCES_URL")
CODEFORCES_STATUS_URL = os.getenv("CODEFORCES_STATUS_URL")

CODECHEF_URL = os.getenv("CODECHEF_URL")

GITHUB = os.getenv("GITHUB")

LINKEDIN = os.getenv("LINKEDIN")





app = Flask(__name__)

@app.route("/")
def home_page():
    return render_template("index.html",github=GITHUB,linkedin=LINKEDIN)

@app.route("/leetcode")
def leetcode_guide():
    return render_template("leetcode.html",active="leetcode",github=GITHUB,linkedin=LINKEDIN)

@app.route("/codeforces")
def codeforces_guide():
    return render_template("codeforces.html",active="codeforces",github=GITHUB,linkedin=LINKEDIN)

@app.route("/codechef")
def codechef_guide():
    return render_template("codechef.html",active="codechef",github=GITHUB,linkedin=LINKEDIN)


@app.route("/leetcode/<username>",methods=["GET"])
def leetcode(username):
    COUNT_QUERY = {
    "query": """
    query getUserProfile($username: String!) {
        matchedUser(username: $username) {
            username
            submitStats {
                acSubmissionNum {
                    difficulty
                    count
                }
            }
            profile {
                ranking
                reputation
            }
        }
    }
    """,
    "variables": {"username": username}
}
    RATING_QUERY = {
    "query": """
    query userContestRankingInfo($username: String!) {
        userContestRanking(username: $username) {
            rating
            globalRanking
            attendedContestsCount
            topPercentage
        }
    }
    """,
    "variables": {
        "username": username
    }
}
    
    count_res = requests.post(LEETCODE_URL,json=COUNT_QUERY)
    count_data= count_res.json()
    count = count_data["data"]["matchedUser"]["submitStats"]["acSubmissionNum"]
    total = count[0]["count"]
    easy = count[1]["count"]
    medium = count[2]["count"]
    hard = count[3]["count"]
    
    rating_res = requests.post(LEETCODE_URL,json=RATING_QUERY)
    rating_data = rating_res.json()["data"]["userContestRanking"]
    attended_contest = rating_data["attendedContestsCount"]
    globalRanking = rating_data["globalRanking"]
    rating = ceil(rating_data["rating"])
    topPercentage = rating_data["topPercentage"]
    
    data = {
        "total":total,
        "easy":easy,
        "medium":medium,
        "hard":hard,
        "attended_contest":attended_contest,
        "globalRanking":globalRanking,
        "rating":rating,
        "topPercentage":topPercentage
    }
    
    return jsonify(data)

@app.route("/codeforces/<username>",methods=["GET"])
def codeforces(username):
    ranking_res = requests.get(CODEFORCES_URL+username).json()["result"][0]
    
    curr_rating = ranking_res["rating"]
    max_rating = ranking_res["maxRating"]
    curr_rank = ranking_res["rank"]
    max_rank = ranking_res["maxRank"]
    
    count_res = requests.get(CODEFORCES_STATUS_URL+username).json()
    
    solved = set()
    for sub in count_res["result"]:
        if sub.get("verdict") == "OK":
            prob = sub["problem"]
            solved.add((prob["contestId"],prob["index"]))
    
    data = {
        "curr_rating":curr_rating,
        "curr_rank":curr_rank,
        "max_rating":max_rating,
        "max_rank":max_rank,
        "problem_solved":len(solved)
    }
    
    return jsonify(data)

@app.route("/codechef/<username>",methods=["GET"])
def codechef(username):
    driver = webdriver.Chrome()
    driver.get(CODECHEF_URL+username)
    time.sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html,"html.parser")
    text = soup.get_text(" ",strip=True)
    
    rating_block = re.search(r'(\d{3,4})\s*\(\s*\+?(-?\d+)\s*\)\s*Rating', text)

    if rating_block:
        rating = rating_block.group(1)
        change = rating_block.group(2)
    else:
        rating = "Not found"
        change = "Not found"
        
    problems_match = re.search(r'Total Problems Solved:\s*(\d+)', text)
    problems = problems_match.group(1) if problems_match else "Not found"
    
    driver.quit()
    
    data = {
        "rating":rating,
        "change_in_rating":change,
        "problems":problems
    }
    
    return jsonify(data)
    
        
    
    

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)
    