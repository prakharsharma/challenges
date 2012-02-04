#!/usr/bin/python

import random
import sys
import ConfigParser
import MySQLdb

def parseCfgFile(_path, sectionName, sectionCfg):
    config = ConfigParser.ConfigParser()
    config.read(_path)
    for k, v in config.items(sectionName):
        sectionCfg[k] = v

def get_distinct_random_in_range(a, b):
    i = random.randint(a, b)
    j = i
    while j == i:
        j = random.randint(a, b)
    return (i, j)

class Concept:

    dbCfg = {}
    id_to_concept = {}
    root_concepts = {}
    value_to_concept = {}
    conn = None

    @classmethod
    def get_db_conn(cls):
        if Concept.conn is not None:
            return Concept.conn
        Concept.conn = MySQLdb.connect(host = Concept.dbCfg['host'].strip('"').strip("'"),\
                port = int(Concept.dbCfg['port'].strip('"').strip("'")),\
                db = Concept.dbCfg['db'].strip('"').strip("'"),\
                user = Concept.dbCfg['user'].strip('"').strip("'"),\
                passwd = Concept.dbCfg['password'].strip('"').strip("'"),\
                use_unicode = True,\
                charset = 'utf8')
        return Concept.conn

    def __load_from_db(self):
        self.__loadedFromDb = True
        cursor = Concept.get_db_conn().cursor()
        cursor.execute("""SELECT value, parent FROM concept""");
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            self.__add_concept(value = row[0], parent = row[1])
        cursor.close()

    def __insert_concept(self, value):
        cursor = Concept.get_db_conn().cursor()
        cursor.execute("""SELECT id FROM concept WHERE value = %s""",
                value)
        row = cursor.fetchone()
        if row is not None:
            cursor.close()
            return False
        cursor.execute("""INSERT INTO concept(value) VALUES (%s)""",
                value)
        Concept.get_db_conn().commit()
        self.__id = cursor.lastrowid
        cursor.close()
        return True

    def __init_from_db(self, uuid, value, parent, score):
        self.__id = uuid
        self.__value = value
        self.__score = score
        self.__parent = parent
        self.__children = {}
        Concept.id_to_concept[self.__id] = self
        if parent == -1:
            Concept.root_concepts[self.__id] = self
        Concept.value_to_concept[value] = self.__id

    def __init__(self, loadFromDbFlag, **kwargs):
        if loadFromDbFlag:
            self.__init_from_db(uuid = kwargs['uuid'], value =
                    kwargs['value'], parent = kwargs['parent'], score =
                    kwargs['score'])
        value = kwargs['value'].strip().lower()
        if self.__insert_concept(value) is False:
            return
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
        return ((self.__parent is None or self.__parent == -1) and [None] or \
                [Concept.id_to_concept[self.__parent]])[0]

    def set_score(self, parentScore, dirtyConcepts):
        self.__score = parentScore - 1
        dirtyConcepts.append(self.__id)
        for k in self.__children.keys():
            Concept.id_to_concept[k].set_score(parentScore = self.__score,
                    dirtyConcepts = dirtyConcepts)

    def flush_concept(self):
        cursor = Concept.get_db_conn().cursor()
        cursor.execute("""UPDATE concept SET parent = %s, score = %s WHERE id =
                %s""", (self.__parent, self.__score, self.__id))
        cursor.close()

    @classmethod
    def add_concept(cls, value):
        node = cls(loadFromDbFlag = False, value = value)
#        print node.get_stats()

    @classmethod
    def flush_dirty_concepts(cls, dirtyConcepts):
        for cid in dirtyConcepts:
            c = Concept.id_to_concept[cid]
            c.flush_concept()
        Concept.get_db_conn().commit()

    @classmethod
    def merge_concepts(cls, parent, child):
        if child.__id in Concept.root_concepts:
            del Concept.root_concepts[child.__id]
        curr_par = child.get_parent()
        if curr_par is not None:
            del curr_par.__children[child.__id]
        parent.__children[child.__id] = child.__id
        child.__parent = parent.__id
        dirtyConcepts = []
        dirtyConcepts.append(parent.__id)
        child.set_score(parentScore = parent.__score, \
                dirtyConcepts = dirtyConcepts)
        Concept.flush_dirty_concepts(dirtyConcepts)

    @classmethod
    def handle_judgment(cls, c1, c2, judgment):
        c1 = int(c1.strip())
        c2 = int(c2.strip())
        n1 = Concept.id_to_concept[c1]
        n2 = Concept.id_to_concept[c2]
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
            return ((str(c1.__id), c1.__value), (str(c2.__id), c2.__value))
        if len(keys) < 2:
            sys.stdout.write('No more concepts to judge')
            sys.stdout.flush()
            return (None, None)
        b = a
        while b == a:
            b = random.randint(0, len(keys) - 1)
        return ((str(keys[a]), Concept.id_to_concept[keys[a]].__value),\
                (str(keys[b]), Concept.id_to_concept[keys[b]].__value))

    @classmethod
    def top_10_concepts(cls):
        cursor = Concept.get_db_conn().cursor()
        cursor.execute("""SELECT value FROM concept ORDER BY score DESC LIMIT 10""")
        top10 = []
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            top10.append(row[0])
        cursor.close()
        return top10

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

    @classmethod
    def setup_node_children(cls):
        for pid in Concept.id_to_concept.keys():
            par = Concept.id_to_concept[pid]
            for cid in Concept.id_to_concept.keys():
                if cid == pid:
                    continue
                child = Concept.id_to_concept[cid]
                if child.__parent == pid:
                    par.__children[cid] = cid

    @classmethod
    def load_from_db(cls):
        cursor = Concept.get_db_conn().cursor()
        cursor.execute("""SELECT * FROM concept""")
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            node = cls(loadFromDbFlag = True, uuid = row[0], value = row[1], parent = row[2],
                    score = row[3])
        cursor.close()
        Concept.setup_node_children()

    @classmethod
    def setup(cls, cfgFile):
        parseCfgFile(cfgFile, 'database', Concept.dbCfg)
        Concept.load_from_db()


if __name__ == "__main__":
    pass
