import datetime
import random
import json
import copy


class QuizController:

    def __init__(self, path, count, decay, new_mult=1.0):
        self.path = path
        self.count = count
        self.decay = decay
        self.new_mult = new_mult
        self.session = {}
        self.history = {}
        self.last_visited = {}
        self.categories = {}
        self.load()
        self.oldest_start = 28

    def load(self):
        try:
            with open(self.path, 'r') as json_file:
                self.history = json.load(json_file)

        except Exception as e:
            print('History not found')

        lv_path = self.path.replace('qc.json', 'qc_lv.json')
        try:
            with open(lv_path, 'r') as json_file:
                self.last_visited = json.load(json_file)

        except Exception as e:
            print('Last visited not found')

        cat_path = self.path.replace('qc.json', 'qc_cat.json')
        try:
            with open(cat_path, 'r') as json_file:
                self.categories = json.load(json_file)

        except Exception as e:
            print('Categories not found')

    def save(self):
        with open(self.path, 'w') as json_file:
            json.dump(self.history, json_file, indent=4)

        lv_path = self.path.replace('qc.json', 'qc_lv.json')
        with open(lv_path, 'w') as json_file:
            json.dump(self.last_visited, json_file, indent=4)

        cat_path = self.path.replace('qc.json', 'qc_cat.json')
        with open(cat_path, 'w') as json_file:
            json.dump(self.categories, json_file, indent=4)


    def get_question_index(self):
        # first find any that have never been seen
        print(f'Looking for never seen questions')
        choices = []
        for ndx in range(self.count):
            k = str(ndx)
            if k in self.session:
                continue
            if k not in self.history.keys():
                choices.append(ndx)
        if len(choices) > 0:
            return random.choice(choices)

        # next find any that haven't been seen in N days
        num_days = self.oldest_start
        target_count = self.count // 4
        while num_days >= 0:
            print(f'Looking for questions over [{num_days}] days old...')
            error_k = 200.0
            choices = []
            weights = []
            for ndx in range(self.count):
                k = str(ndx)
                if k in self.session:
                    continue
                if k in self.last_visited.keys():
                    last_visited = datetime.datetime.fromtimestamp(self.last_visited[k])
                    age = datetime.datetime.now() - last_visited
                    if age <= datetime.timedelta(days=num_days):
                        continue

                weight = 100.0
                data = self.history.get(k, [])
                for choice, score in data:
                    weight += error_k * abs(score)
                for _ in data:
                    weight *= self.decay
                choices.append(ndx)
                weights.append(weight)

            if len(choices) >= target_count:
                self.oldest_start = num_days
                return random.choices(choices, weights, k=1)[0]

            num_days -= 1

        return 0

    def post_result(self, question_index, choice, score):
        key = str(question_index)
        session = self.session.get(key, [])
        session.append([choice, score])
        self.session[key] = session
        history = self.history.get(key, [])
        history.append([choice, score])
        self.history[key] = history
        self.last_visited[key] = datetime.datetime.now().timestamp()

    def dump(self):
        print('-' * 40)
        for k in self.__dict__.keys():
            print(f'{k}: {self.__dict__[k]}')

    def print_report(self):
        total_seen = 0.0
        for question_index in range(self.count):
            history = self.history.get(str(question_index), [])
            total_count = 0.0
            total_score = 0.0
            for h in history:
                total_count += 1.0
                total_score += h[1]
            if total_count == 0:
                continue
            average_score = 0.0 if total_count == 0.0 else total_score / total_count
            print(f'{question_index:3} {total_count:3} {average_score:.3}')
            total_seen += 1
        print (f'Coverage {total_seen / self.count:.3}')

    def print_last_visited(self):
        report = {}
        for k in self.last_visited.keys():
            date = datetime.datetime.fromtimestamp(self.last_visited[k])
            formatted_date_local = date.strftime('%Y-%m-%d')
            report[formatted_date_local] = report.get(formatted_date_local, 0) + 1
        keys = sorted(report.keys())
        for k in keys:
            print(k , report[k])


if __name__ == '__main__':
    qc = QuizController('test.json', 30, 0.99)
    qc.dump()

    for x in range(1000):
        question_index = qc.get_question_index()
        score = 0.0
        print(question_index)
        if question_index:
            if question_index % 3 == 0:
                score = -0.1
        qc.post_result(question_index, random.randint(0, 3), score)

    qc.dump()

    total = {}
    counts = {}
    for k in qc.history.keys():
        data = qc.history[k]
        total_score = 0.0
        total_count = 0
        for choice, score in data:
            total_count += 1
            total_score += score
        print(f'{k:3} {total_count:3}    {total_score:.3}')

    # qc.save()


