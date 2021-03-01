class _Member:

    def __init__(self, name, rating):
        self.name = name
        self.rating = rating
        self.deferred = 0
        self.problems = 0

    def compare_rating(self, opponent):
        delta = min(400, max(-400, opponent.rating - self.rating))
        return (1 + 10 ** (delta / 400.0)) ** -1


class Rating:

    def __init__(self, base_rating=1000):
        self.base_rating = base_rating
        self.members = []

    def __get_member_list(self):
        return self.members

    def get_member(self, name):
        for member in self.members:
            if member.name == name:
                return member
        return None

    def contains(self, name):
        for member in self.members:
            if member.name == name:
                return True
        return False

    def add_member(self, name, rating=None):
        if rating is None:
            rating = self.base_rating

        self.members.append(_Member(name=name, rating=rating))

    def remove_member(self, name):
        self.__get_member_list().remove(self.get_member(name))

    def get_member_rating(self, name):
        member = self.get_member(name)
        return member.rating

    def get_rating_list(self):
        lst = []
        for member in self.__get_member_list():
            lst.append((member.name, member.rating))
        return lst

    def get_k_factor(self, name):
        member = self.get_member(name)
        if member.problems <= 30:
            return 40
        elif member.rating < 2400:
            return 20
        else:
            return 10

    def get_problem_complexity(self, results, bound=4000):
        res = 1000
        std_dev = len(self.members) + 1
        for problem_rating in range(bound):
            cur_std_dev = min(
                [
                    sum(
                        [
                            (results[member.name] -
                             member.compare_rating(_Member(
                                 name="Задача",
                                 rating=problem_rating))
                             ) ** 2 if results[member.name] != -1 else 0
                            for member in self.members
                        ]
                    )
                ]
            )
            if cur_std_dev < std_dev:
                std_dev = cur_std_dev
                res = problem_rating
        return res

    def record_problem(self, results, way, mod=True):
        expected = {}
        new_rating = {}

        present_members_number = 0
        for x in results:
            if x != -1:
                present_members_number += 1

        if way == "standard":
            problem = _Member("Задача", self.get_problem_complexity(results))

        for member in self.members:
            name = member.name
            if results[name] != -1:
                if way == "standard":
                    expected[name] = member.compare_rating(problem)
                elif way == 0:
                    expected[name] = 1
                    for opponent in self.members:
                        if opponent.name != name and results[opponent.name] != -1:
                            expected[name] *= member.compare_rating(opponent)
                    expected[name] **= 1 / (present_members_number - 1)
                else:
                    expected[name] = 0
                    for opponent in self.members:
                        if opponent.name != name and results[opponent.name] != -1:
                            expected[name] += member.compare_rating(opponent) ** way
                    expected[name] /= present_members_number - 1
                    expected[name] **= 1 / way
                new_rating[name] = max(0, member.rating + \
                                       self.get_k_factor(name) * (results[name] - expected[name]))
                member.problems += 1
            else:
                new_rating[name] = member.rating

        res = {}
        for member in self.members:
            delta = new_rating[member.name] - member.rating
            res[member.name] = str(delta).replace(".", ",")
            if mod:
                member.rating = new_rating[member.name]
            else:
                member.deferred += delta
        return res

    def update(self):
        for member in self.members:
            member.rating += member.deferred
            member.deferred = 0
