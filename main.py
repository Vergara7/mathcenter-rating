from rating import *

TASKS = 32
MOD = False  # False -- new, True -- old
CRUEL_FROM = -1  # -1 if not cruel

ratings = {"": Rating(),
           "c": Rating(),
           "g": Rating(),
           "a": Rating(),
           "nt": Rating(),
           "aORnt": Rating()}

members = open("members.txt")
names = list(map(lambda s: s.strip(), members.readlines()))
themes_file = open("themes.txt")
themes = list(themes_file.readline().split())

for name in names:
    for rating in ratings.values():
        rating.add_member(name)

tasks = []
task_deltas = []

complexities_file = open("complexities.txt", "w")

for n in range(TASKS):
    tasks.append(open("tasks/Серия {}.txt".format(n + 1)))
    task_deltas.append(open("task_deltas/Серия {}.txt".format(n + 1), "w"))

    perfect = list(map(int, tasks[-1].readline().split()))
    cnt = len(perfect)
    task_themes = themes[:cnt]
    themes = themes[cnt:]

    results = [{} for i in range(cnt)]
    for name in names:
        res = list(map(int, tasks[n].readline().split()))
        for i in range(cnt):
            results[i][name] = res[i]
        present = False
        if CRUEL_FROM != -1 and n + 1 >= CRUEL_FROM:
            present = True
        else:
            for i in range(cnt):
                if perfect[i] == 1 and results[i][name] == 1:
                    present = True
        if not present:
            for i in range(cnt):
                if perfect[i] == 1:
                    results[i][name] = -1

    delta = {}
    for name in names:
        delta[name] = []

    for i in range(cnt):
        if perfect[i] == 1:
            print(ratings[""].get_problem_complexity(results[i]), end='\t', file=complexities_file)
            res = ratings[""].record_problem(results[i], "standard", MOD)
            task_theme = task_themes[i]
            ratings[task_theme].record_problem(results[i], "standard", MOD)
            if task_theme == "a" or task_theme == "nt":
                ratings["aORnt"].record_problem(results[i], "standard", MOD)
            for name in names:
                delta[name].append(res[name])
        else:
            print("-", end='\t', file=complexities_file)
            for name in names:
                delta[name].append("0")
    if not MOD:
        for member in ratings[""].members:
            big_delta = member.deferred
            print(str(big_delta).replace(".", ","), file=task_deltas[-1])
        for rating in ratings.values():
            rating.update()

    delta_file = open("deltas/{}_results.txt".format(tasks[-1].name[6:-4]), "w")
    for name in names:
        print(*delta[name], sep='\t', file=delta_file)
    print('', end='\t', file=complexities_file)

for theme_id in ["", "c", "g", "a", "nt", "aORnt"]:
    rating_file = open("ratings/rating_{}.txt".format(theme_id), "w")
    for name, rating in ratings[theme_id].get_rating_list():
        print(str(rating).replace(".", ","), file=rating_file)
