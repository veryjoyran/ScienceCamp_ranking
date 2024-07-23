from flask import Flask, request, render_template, jsonify
import csv

app = Flask(__name__)


def read_leaderboard(file_path):
    leaderboard = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            row['完成时间'] = int(row['完成时间'])
            row['加罚时间'] = int(row['加罚时间'])
            row['最终时间'] = int(row['最终时间'])
            leaderboard.append(row)
    return leaderboard


def write_leaderboard(file_path, leaderboard):
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        fieldnames = ['组名', '完成时间', '加罚时间', '最终时间']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for entry in leaderboard:
            writer.writerow(entry)


def update_leaderboard(file_path, group_name, completion_time, penalty_time):
    leaderboard = read_leaderboard(file_path)
    for entry in leaderboard:
        if entry['组名'] == group_name:
            entry['完成时间'] = completion_time
            entry['加罚时间'] = penalty_time
            entry['最终时间'] = completion_time + penalty_time
            break

    leaderboard.sort(key=lambda x: x['最终时间'])
    write_leaderboard(file_path, leaderboard)


def add_ranking(leaderboard):
    leaderboard.sort(key=lambda x: x['最终时间'])
    for idx, entry in enumerate(leaderboard, start=1):
        entry['排名'] = idx
    return leaderboard


@app.route('/')
def index():
    leaderboard = read_leaderboard('leaderboard.csv')
    leaderboard_with_ranking = add_ranking(leaderboard)
    return render_template('index.html', leaderboard=leaderboard_with_ranking)


@app.route('/update', methods=['POST'])
def update():
    data = request.get_json()
    group_name = data['group_name']
    completion_time = int(data['completion_time'])
    penalty_time = int(data['penalty_time'])
    update_leaderboard('leaderboard.csv', group_name, completion_time, penalty_time)
    return jsonify(success=True)


if __name__ == '__main__':
    app.run(debug=True)
