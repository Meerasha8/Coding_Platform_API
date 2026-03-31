from flask import Flask,jsonify
import os
from dotenv import load_dotenv
import requests
from math import ceil

load_dotenv()


LEETCODE_URL = os.getenv("LEETCODE_URL")
USER = os.getenv("LEETCODE_ID")

CODEFORCES_ID = os.getenv("CODEFORCES_ID")
CODEFORCES_URL = os.getenv("CODEFORCES_URL") + CODEFORCES_ID
CODEFORCES_STATUS_URL = os.getenv("CODEFORCES_STATUS_URL") + CODEFORCES_ID

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
    "variables": {"username": USER}
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
        "username": USER
    }
}

app = Flask(__name__)


@app.route("/leetcode/<username>",methods=["GET"])
def leetcode(username):
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
    ranking_res = requests.get(CODEFORCES_URL).json()["result"][0]
    
    curr_rating = ranking_res["rating"]
    max_rating = ranking_res["maxRating"]
    curr_rank = ranking_res["rank"]
    max_rank = ranking_res["maxRank"]
    
    count_res = requests.get(CODEFORCES_STATUS_URL).json()
    
    solved = set()
    print(count_res)
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
    
    

if __name__ == "__main__":
    print(CODEFORCES_URL)
    app.run(host="0.0.0.0",port=5000,debug=True)
    