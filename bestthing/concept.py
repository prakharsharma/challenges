#!/usr/bin/python

import random

def get_distinct_random_in_range(a, b):
    i = random.randint(a, b)
    j = i
    while j == i:
        j = random.randint(a, b)
    return (i, j)

class Concept:

    count = 0
    id_to_concept = {}
    root_concepts = {}
    value_to_concept = {}

    def __init__(self, value):
        value = value.strip().lower()
        Concept.count += 1
        self.__id = Concept.count
        self.__value = value
        self.__score = 0
        self.__parent = None
        self.__children = {}
        Concept.id_to_concept[self.__id] = self
        Concept.root_concepts[self.__id] = self
        Concept.value_to_concept[value] = self.__id

    def __del__(self):
        Concept.id_to_concept[self.__id] = None

    def get_stats(self):
        return "{id: %d, value: %s}" % (self.__id, self.__value)

    def get_concepts(self):
        if self.__children is None or len(self.__children) == 0:
            return (self, None)
        keys = self.__children.keys()
        if len(keys) == 1:
            return Concept.id_to_concept[self.__children[keys[0]]].get_concepts()
        (a, b) = get_distinct_random_in_range(0, len(keys) - 1)
        return (Concept.id_to_concept[self.__children[keys[a]]],\
                Concept.id_to_concept[self.__children[keys[b]]])

    def get_root(self):
        return (self.__parent is None and [self] or \
                [Concept.id_to_concept[self.__parent].get_root()])[0]

    def get_parent(self):
        return (self.__parent is None and [None] or \
                [Concept.id_to_concept[self.__parent]])[0]

    def set_score(self, parentScore):
        self.__score = parentScore - 1
        for k in self.__children.keys():
            Concept.id_to_concept[k].set_score(parentScore = self.__score)

    @classmethod
    def add_concept(cls, value):
        node = cls(value)
#        print node.get_stats()

    @classmethod
    def merge_concepts(cls, parent, child):
        if child.__id in Concept.root_concepts:
            del Concept.root_concepts[child.__id]
        curr_par = child.get_parent()
        if curr_par is not None:
            del curr_par.__children[child.__id]
        parent.__children[child.__id] = child.__id
        child.__parent = parent.__id
        child.set_score(parentScore = parent.__score)

    @classmethod
    def handle_judgment(cls, c1, c2, judgment):
        c1 = c1.strip().lower()
        c2 = c2.strip().lower()
        if c1 in Concept.value_to_concept and c2 in Concept.value_to_concept:
            n1 = Concept.id_to_concept[Concept.value_to_concept[c1]]
            n2 = Concept.id_to_concept[Concept.value_to_concept[c2]]
            if n1.__score != n2.__score:
                return
            if judgment == '1':
                Concept.merge_concepts(parent = n1, child = n2)
            else:
                Concept.merge_concepts(parent = n2, child = n1)

    @classmethod
    def get_concepts_to_judge(cls):
        keys = Concept.root_concepts.keys()
        a = random.randint(0, len(keys) - 1)
        (c1, c2) = Concept.id_to_concept[keys[a]].get_concepts()
        if c2 is not None:
            return (c1.__value, c2.__value)
        if len(keys) < 2:
            sys.stdout.write('No more concepts to judge')
            sys.stdout.flush()
            return (None, None)
        b = a
        while b == a:
            b = random.randint(0, len(keys) - 1)
        return (Concept.id_to_concept[keys[a]].__value,\
                Concept.id_to_concept[keys[b]].__value)

    @classmethod
    def sorted_concepts(cls):
        scores = {}
        for cid in Concept.id_to_concept.keys():
            c = Concept.id_to_concept[cid]
            if c.__score not in scores:
                scores[c.__score] = []
            scores[c.__score].append(c.__value)
        skeys = scores.keys()
        skeys.sort(reverse = True)
        retVal = {}
        for k in skeys:
            retVal[k] = scores[k]
        return retVal


if __name__ == "__main__":
    pass
