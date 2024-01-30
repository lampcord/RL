import random
import json
import copy


class QuizController:

    def __init__(self, path, count, decay):
        self.path = path
        self.count = count
        self.decay = decay
        self.session = {}
        self.history = {}
        self.load()

    def load(self):
        try:
            with open(self.path, 'r') as json_file:
                self.history = json.load(json_file)

        except Exception as e:
            print('History not found')

    def save(self):
        with open(self.path, 'w') as json_file:
            json.dump(self.history, json_file, indent=4)

    def get_question_index(self):
        questions_indexes = list(range(self.count))
        error_k = 200.0
        base_blunder = 100.0 + error_k * 0.080
        base_blunder *= self.decay
        weights = [100.0] * self.count
        for k in self.history.keys():
            if k in self.session:
                continue
            data = self.history[k]
            has_been_visited = False
            for choice, score in data:
                has_been_visited = True
                weights[int(k)] += error_k * abs(score)
            for choice, score in data:
                weights[int(k)] *= self.decay
            if not has_been_visited:
                weights[int(k)] = base_blunder

        # for x in range(len(weights)):
        #     print(x, weights[x])

        return random.choices(questions_indexes, weights, k=1)[0]

    def post_result(self, question_index, choice, score):
        key = str(question_index)
        session = self.session.get(key, [])
        session.append([choice, score])
        self.session[key] = session
        history = self.history.get(key, [])
        history.append([choice, score])
        self.history[key] = history

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


