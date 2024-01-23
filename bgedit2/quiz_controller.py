import random
import json
import copy

class QuizController:
    def __init__(self, path, count, threshold):
        self.path = path
        self.count = count
        self.threshold = threshold
        self.new_right = []
        self.old_right = []
        self.new_wrong = []
        self.old_wrong = []
        self.session = {}
        self.history = {}
        self.load()

    def load(self):
        pass
        try:
            with open(self.path, 'r') as json_file:
                self.__dict__ = json.load(json_file)
            self.session = {}
            recovered_keys = []
            for key in range(self.count):
                if key not in self.new_right and key not in self.old_right and key not in self.new_wrong and key not in self.old_wrong:
                    recovered_keys.append(key)
                    print(f'Recovering {key}')
            for key in recovered_keys:
                self.old_right.append()
            wrong_list = []
            for key in self.new_wrong:
                wrong_list.append(key)
            for key in self.old_wrong:
                wrong_list.append(key)
            self.old_wrong = copy.deepcopy(wrong_list)
            self.new_wrong = []


        except Exception as e:
            self.old_right = list(range(self.count))
            random.shuffle(self.old_right)
    def save(self):
        with open(self.path, 'w') as json_file:
            json.dump(self.__dict__, json_file, indent=4)

    def get_question_index_from_lists(self, l_old, l_new):
        question_index = None
        if len(l_old) > 0:
            question_index = l_old.pop()
        elif len(l_new) >= self.threshold:
            random.shuffle(l_new)
            l_old = copy.deepcopy(l_new)
            l_new = []
            question_index = l_old.pop()
        return question_index, l_old, l_new


    def get_question_index(self):
        pass
        question_index = None
        if random.random() < 0.7:
            print('getting wrong')
            question_index, old_wrong, new_wrong = self.get_question_index_from_lists(self.old_wrong, self.new_wrong)
            self.old_wrong = copy.deepcopy(old_wrong)
            self.new_wrong = copy.deepcopy(new_wrong)
        if question_index is None:
            print('getting right')
            question_index, old_right, new_right = self.get_question_index_from_lists(self.old_right, self.new_right)
            self.old_right = copy.deepcopy(old_right)
            self.new_right = copy.deepcopy(new_right)

        return question_index

    def post_result(self, question_index, choice, score):
        if score < 0.0:
            self.new_wrong.append(question_index)
        else:
            self.new_right.append(question_index)
        session = self.session.get(question_index, [])
        session.append((choice, score))
        self.session[question_index] = session
        history = self.history.get(question_index, [])
        history.append((choice, score))
        self.history[question_index] = history

    def dump(self):
        print('-' * 40)
        for k in self.__dict__.keys():
            print(f'{k}: {self.__dict__[k]}')


if __name__ == '__main__':
    qc = QuizController('test.json', 30, 5)
    qc.dump()

    for x in range(40):
        question_index = qc.get_question_index()
        score = 0.0
        print(question_index)
        if question_index:
            if question_index % 3 == 0:
                score = -0.1
        qc.post_result(question_index, random.randint(0, 3), score)
        qc.dump()
    # qc.save()


