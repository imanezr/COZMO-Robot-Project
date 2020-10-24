from aima.logic import *
from aima.utils import *
from grammar.extractor import ClueExtractor


class MurderEngine:

    def __init__(self):

        self.is_m_room_known = False
        self.is_w_room_known = False
        self.is_w_known = False

        clauses = []

        # Cause of death -> weapon inference
        clauses.append(expr('CauseOfDeath(Stab) ==> Weapon(Knife)'))
        clauses.append(expr('CauseOfDeath(Shot) ==> Weapon(Revolver)'))
        clauses.append(expr('CauseOfDeath(Strangled) ==> Weapon(Rope)'))
        clauses.append(expr('CauseOfDeath(Blunt) ==> Weapon(Book)'))

        # Weapon -> WeaponRoom inference
        clauses.append(expr("Weapon(Knife) ==> WeaponRoom(Kitchen)"))
        clauses.append(expr("Weapon(Rope) ==> WeaponRoom(Attic)"))
        clauses.append(expr("Weapon(Revolver) ==> WeaponRoom(Study)"))
        clauses.append(expr("Weapon(Book) ==> WeaponRoom(Library)"))

        # Murder access
        # clauses.append(expr("MurderRoom(m_room) & MurderTime(a,b) & Access(p, m_room, a, b) ==> CouldMurder(p)"))

        # Weapon access
        # clauses.append(expr("WeaponRoom(w_room) & WeaponTime(a,b) & Access(p, w_room, a, b) ==> CouldGetWeapon(p)"))

        self.kb = FolKB(clauses)
        self.extractor = ClueExtractor()

    def eval_sentence(self, sentence):
        facts = self.extractor.get_labels(sentence)
        for key, values in facts.items():
            key_str = str(key)
            values_str = [str(value).capitalize() for value in values]

            if key_str == "cause":
                self.assert_cod(values_str[0])
                self.assert_victim(values_str[1])
            elif key_str == "WeaponRoom" and not self.is_w_room_known:
                self.is_w_room_known = True
                self.assert_weapon_room(values_str[0])
            elif key_str == "MurderRoom" and not self.is_m_room_known:
                self.is_m_room_known = True
                self.assert_murder_room(values_str[0])
            elif key_str == "Weapon" and not self.is_w_known:
                self.is_w_known = True
                self.assert_weapon(values_str[0])
            elif key_str == "WeaponTime":
                self.assert_weapon_time(values_str[0], values_str[1])
            elif key_str == "MurderTime":
                self.assert_murder_time(values_str[0], values_str[1])
            elif key_str == "Access":
                self.assert_room_access(values_str[0], values_str[1], values_str[2], values_str[3])

    def assert_victim(self, victim):
        self.kb.tell(expr("Victim({})".format(victim)))
        fact = fol_fc_ask(self.kb, expr('Victim(victim)'))
        print(list(fact))

    def get_victim(self):
        return self.kb.ask(expr("Victim(victim)"))[expr('victim')].op

    def assert_cod(self, cod):
        self.kb.tell(expr('CauseOfDeath({})'.format(cod)))
        fact = fol_fc_ask(self.kb, expr('CauseOfDeath(cod)'))
        print(list(fact))

        weapon = fol_fc_ask(self.kb, expr('Weapon(weapon)'))
        print(list(weapon))

        weapon_room = fol_fc_ask(self.kb, expr('WeaponRoom(weapon_room)'))
        print(list(weapon_room))

    def assert_murder_room(self, m_room):
        self.kb.tell(expr('MurderRoom({})'.format(m_room)))
        fact = fol_fc_ask(self.kb, expr('MurderRoom(murder_room)'))
        print(list(fact))

    def assert_murder_time(self, start, end):
        self.kb .tell(expr('MurderTime({}, {})'.format(start, end)))
        fact = fol_fc_ask(self.kb, expr('MurderTime(murder_start_time, murder_end_time)'))
        print(list(fact))

    def assert_room_access(self, person, room, time_start, time_end):
        self.kb.tell(expr('Access({}, {}, {}, {})'.format(person, room, time_start, time_end)))
        print('person: {}, room: {}, time_start: {}, time_end: {}'.format(person, room, time_start, time_end))

    def assert_weapon_time(self, time_start, time_end):
        self.kb.tell(expr('WeaponTime({}, {})'.format(time_start, time_end)))
        fact = fol_fc_ask(self.kb, expr('WeaponTime(w_time_start, w_time_end)'))
        print(list(fact))

    def assert_weapon_room(self, room):
        self.kb.tell(expr('WeaponRoom({})'.format(room)))
        fact = fol_fc_ask(self.kb, expr('WeaponRoom(w_room)'))
        print(list(fact))

    def assert_weapon(self, weapon):
        self.kb.tell(expr('Weapon({})'.format(weapon)))
        fact = fol_fc_ask(self.kb, expr('Weapon(weapon)'))
        print(list(fact))

    def assert_could_murder(self):
        self.kb.tell(expr("MurderRoom(m_room) & MurderTime(a,b) & Access(p, m_room, a, b) ==> CouldMurder(p)"))
        fact = fol_fc_ask(self.kb, expr('CouldMurder(could_murder)'))
        print(list(fact))

    def assert_could_get_weapon(self):
        self.kb.tell(expr("WeaponRoom(w_room) & WeaponTime(a,b) & Access(p, w_room, a, b) ==> CouldGetWeapon(p)"))
        fact = fol_fc_ask(self.kb, expr('CouldGetWeapon(could_get_weapon)'))
        print(list(fact))

    def assert_murderer(self):
        self.kb.tell(expr("WeaponRoom(w_room) & WeaponTime(a,b) & Access(p, w_room, a, b) ==> CouldGetWeapon(p)"))
        accesses = fol_fc_ask(self.kb, expr('Access(person, room, time_start, time_end)'))
        print(list(accesses))

        self.assert_could_murder()
        self.assert_could_get_weapon()

        solver = expr("(CouldMurder(murderer) & CouldGetWeapon(murderer)) ==> Murderer(murderer)")
        self.kb.tell(solver)
        fact = list(fol_fc_ask(self.kb, expr('Murderer(murderer)')))
        print(fact)

    def get_murderer(self):
        return self.kb.ask(expr('Murderer(murderer)'))[expr('murderer')].op

    def get_murder_weapon(self):
        return self.kb.ask(expr("Weapon(weapon)"))[expr("weapon")].op

    def get_murder_time(self):
        a = self.kb.ask(expr("MurderTime(a, b)"))[expr("a")].op
        b = self.kb.ask(expr("MurderTime(a, b)"))[expr("b")].op
        return [a, b]

    def get_weapon_time(self):
        a = self.kb.ask(expr("WeaponTime(a, b)"))[expr("a")].op
        b = self.kb.ask(expr("WeaponTime(a, b)"))[expr("b")].op
        return [a, b]

    def get_murder_room(self):
        return self.kb.ask(expr("MurderRoom(room)"))[expr("room")].op

    def get_weapon_room(self):
        return self.kb.ask(expr("WeaponRoom(room)"))[expr("room")].op


# Test sequence
if __name__ == "__main__":

    engine = MurderEngine()

    # Murder info
    engine.eval_sentence("Mr.Black was Shot.")
    engine.eval_sentence("Mr.Black died_in the Library")
    engine.eval_sentence("Mr.Black died_between one and two.")

    # Weapon info
    engine.eval_sentence("A revolver was_discovered between six and eight")
    engine.eval_sentence("Colonel Mustard was_in the Study between six and eight.")
    engine.eval_sentence("Colonel Mustard was_in the Library between one and two.")

    # Find culprit
    engine.assert_murderer()
