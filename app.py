from flask import Flask, request, render_template, jsonify
import csv

app = Flask(__name__)


def read_leaderboard(file_path):
    leaderboard = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            for key in row:
                row[key] = int(row[key]) if key != '组名' else row[key]
            leaderboard.append(row)
    return leaderboard


def write_leaderboard(file_path, leaderboard):
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        fieldnames = ['组名', '常规赛基础完成时间', '常规赛任务加罚时间', '常规赛重试加罚时间', '常规赛完成时间',
                      '开放赛基础完成时间', '开放赛任务加罚时间', '开放赛重试加罚时间', '开放赛完成时间', '总完成时间']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for entry in leaderboard:
            writer.writerow(entry)


def update_leaderboard(file_path, group_name, norm_base_time, norm_task_penalty, norm_retry_penalty, open_base_time, open_task_penalty, open_retry_penalty):
    leaderboard = read_leaderboard(file_path)
    for entry in leaderboard:
        if entry['组名'] == group_name:
            entry['常规赛基础完成时间'] = norm_base_time
            entry['常规赛任务加罚时间'] = norm_task_penalty
            entry['常规赛重试加罚时间'] = norm_retry_penalty
            entry['常规赛完成时间'] = norm_base_time + norm_task_penalty + norm_retry_penalty
            entry['开放赛基础完成时间'] = open_base_time
            entry['开放赛任务加罚时间'] = open_task_penalty
            entry['开放赛重试加罚时间'] = open_retry_penalty
            entry['开放赛完成时间'] = open_base_time + open_task_penalty + open_retry_penalty
            entry['总完成时间'] = entry['常规赛完成时间'] + entry['开放赛完成时间']
            break

    # 分离总完成时间大于 0 和等于 0 的条目
    positive_time_entries = [e for e in leaderboard if e['总完成时间'] > 0]
    zero_time_entries = [e for e in leaderboard if e['总完成时间'] == 0]

    # 调试信息
    # print("正时间条目:", positive_time_entries)
    # print("零时间条目:", zero_time_entries)

    # 对总完成时间大于 0 的条目进行排序
    sorted_positive_entries = sorted(positive_time_entries, key=lambda x: x['总完成时间'])

    # 调试信息
    # print("排序后的正时间条目:", sorted_positive_entries)

    # 合并排序后的条目和总完成时间为 0 的条目
    sorted_leaderboard =  sorted_positive_entries+zero_time_entries

    # print("最终排序后的排行榜:", sorted_leaderboard)

    write_leaderboard(file_path, sorted_leaderboard)


def add_ranking(leaderboard):
    # leaderboard.sort(key=lambda x: x['总完成时间'])
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
    norm_base_time = int(data['norm_base_time'])
    norm_task_penalty = int(data['norm_task_penalty'])
    norm_retry_penalty = int(data['norm_retry_penalty'])
    open_base_time = int(data['open_base_time'])
    open_task_penalty = int(data['open_task_penalty'])
    open_retry_penalty = int(data['open_retry_penalty'])
    update_leaderboard('leaderboard.csv', group_name, norm_base_time, norm_task_penalty, norm_retry_penalty,
                       open_base_time, open_task_penalty, open_retry_penalty)
    return jsonify(success=True)


if __name__ == '__main__':
    app.run(debug=True)
