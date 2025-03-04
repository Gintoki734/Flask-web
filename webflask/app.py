from flask import Flask, render_template, request, jsonify
import os
import markdown
import json
import pandas as pd

app = Flask(__name__)

# File paths where the data will be stored
LOG_FILE = "user_page_time.csv"
LOG_QUIZ = "user_quiz_performance.csv"

# Define available courses - https://www.w3schools.com/python/python_dictionaries.asp
COURSES = {
    "Talking about yourself": {"content": "data/Talking about yourself.txt", "quiz": "data/Talking about yourself.json"},
    "Talking about family": {"content": "data/Talking about family.txt", "quiz": "data/Talking about family.json"},
    "Animals and pets": {"content": "data/Animals and pets.txt", "quiz": "data/Animals and pets.json"},
    "Classroom language": {"content": "data/Classroom language.txt", "quiz": "data/Classroom language.json"},
    "Weather and seasons": {"content": "data/Weather and seasons.txt", "quiz": "data/Weather and seasons.json"},
    "Numbers and numeracy": {"content": "data/Numbers and numeracy.txt", "quiz": "data/Numbers and numeracy.json"},
    "Days, months and dates": {"content": "data/Days, months and dates.txt", "quiz": "data/Days, months and dates.json"},
    "Colours": {"content": "data/Colours.txt", "quiz": "data/Colours.json"},
    "Clothes": {"content": "data/Clothes.txt", "quiz": "data/Clothes.json"},
    "Food and drink": {"content": "data/Food and drink.txt", "quiz": "data/Food and drink.json"},
    "Exploring the town": {"content": "data/Exploring the town.txt", "quiz": "data/Exploring the town.json"}
}



# https://stackoverflow.com/questions/47048906/convert-markdown-tables-to-html-tables-using-python
# Function to read and convert markdown content
def load_course_content(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as file:
            return markdown.markdown(file.read(), extensions=["tables"])
    return "Content not available."

# Function to load quiz questions
def load_quiz(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    return {"error": "Quiz not available."}

# Dispalys the first page
@app.route("/")
def home():
    return render_template("landingpage.html")

# Dispalys the first page
@app.route("/index")
def index():
    return render_template("index.html", courses=COURSES)

# Displays course content
@app.route("/course/<course_name>")
def course(course_name):
    if course_name in COURSES:
        content = load_course_content(COURSES[course_name]["content"])
        return render_template("course.html", course_name=course_name, content=content)
    return "Course not found", 404

# Displays quiz content for that specific course
@app.route("/quiz/<course_name>")
def quiz(course_name):
    if course_name in COURSES:
        quiz_data = load_quiz(COURSES[course_name]["quiz"])
        return render_template("quiz.html", course_name=course_name, quiz_data=quiz_data)
    return "Quiz not found", 404

# Writes the data collected from the course page into the csv file
@app.route('/log_time', methods=['POST'])
def log_time():
    # Handles any error occured
    try:
        # Getting the data in JSON format and retriving it and storing temporary data incase there is a void/missing data
        data = request.get_json()
        duration = data.get("duration", 0)
        course_name = data.get("courseName", "Unknown Course")
        date = data.get("date", "Unknown Date")
        time = data.get("time", "Unknown Time")

        # Check if the file exists and read it otherwise initialize an empty DataFrame
        if os.path.exists(LOG_FILE):
            df = pd.read_csv(LOG_FILE)
        else:
            df = pd.DataFrame(columns=["Session ID", "Time Spent (seconds)", "Course Name", "Date", "Time"])

        # Data entry for the log
        new_entry = pd.DataFrame({
            "Session ID": [len(df) + 1], 
            "Time Spent (seconds)": [duration],
            "Course Name": [course_name],
            "Date": [date],
            "Time": [time]
        })

        # Append new entry and save it to CSV
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_csv(LOG_FILE, index=False, encoding='utf-8')

        return jsonify({"Message": "Quiz logged"}), 200

    except Exception as e:
        return jsonify({"Error": str(e)}), 500

@app.route('/log_quiz', methods=['POST'])
def log_quiz():
    # Handles any error occured
    try:
        # Getting the data in JSON format and retriving it and storing temporary data incase there is a void/missing data
        data = request.get_json()
        score = data.get("quiz_score", 0)
        course_name = data.get("courseName", "Unknown Course")
        date = data.get("date", "Unknown Date")
        time = data.get("time", "Unknown Time")
        optionClicked = data.get("clickCounts", [0] * 4)
        quiztime = data.get("quiztimetaken", [0] * 4)

        # Check if the file exists and read it otherwise initialize an empty DataFrame
        if os.path.exists(LOG_QUIZ):
            df = pd.read_csv(LOG_QUIZ)  # Read the CSV file
        else:
            df = pd.DataFrame(columns=[
                "Session ID", "Score", "Course Name", "Date", "Time",
                "OptionsClicked_Question_1", "OptionsClicked_Question_2", 
                "OptionsClicked_Question_3", "OptionsClicked_Question_4",
                "Time_Question_1", "Time_Question_2", "Time_Question_3", "Time_Question_4"
            ])

        # Data entry for the log            
        new_entry = pd.DataFrame({
            "Session ID": [len(df) + 1], 
            "Score": [score],
            "Course Name": [course_name],
            "Date" : [date],
            "Time": [time]
            })
        for i in range(4):
            new_entry[f"OptionsClicked_Question_{i+1}"] = optionClicked[i]
            new_entry[f"Time_Question__{i+1}"] = quiztime[i]

        # Append new entry and save it to CSV
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_csv(LOG_QUIZ, index=False)

        return jsonify({"Message": "Quiz logged"}), 200
    except Exception as e:
        return jsonify({"Error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)

