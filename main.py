import json, textwrap, cmd

# https://inventwithpython.com/blog/2014/12/11/making-a-text-adventure-game-with-the-cmd-and-textwrap-python-modules/

SCREEN_WIDTH = 80

rooms = { }
items = { }
props = { }
inventory = [ ]
location = 'Sick Bay'

#this is a new line for this branch


##############################################################
class Room:
    # -------------------------------------------------------
    def __init__(self, name, desc, exits):
        self.name = name
        self.desc = desc
        self.exits = exits
        self.ground = [ ]
        self.props = [ ]
        self.barriers = { }

    # -------------------------------------------------------
    def add_item(self, item_to_add):
        self.ground.append(item_to_add)

    # -------------------------------------------------------
    def remove_item(self, item_to_remove):
        pass

    # -------------------------------------------------------
    def add_prop(self, prop_to_add):
        self.props.append(prop_to_add)

    # -------------------------------------------------------
    def add_barrier(self, direction, prop):
        self.barriers[direction] = prop

    # -------------------------------------------------------
    def move_player(self, direction):
        if direction in self.exits:
            if direction in self.barriers:
                b = self.barriers[direction]
                if b.state != "open":
                    return (False, "Your way is blocked by %s" % (b))
                else:
                    return (True, self.exits[direction])
            else:
                return (True, self.exits[direction])
        else:
            return (False, "You cannot go that way.")

    # -------------------------------------------------------
    def get_item_by_alias(self, item_to_get):
        for i in self.ground:
                if item_to_get in i.aliases:
                    return i
        return None

    # -------------------------------------------------------
    def get_prop_by_alias(self, prop_to_get):
        for i in self.props:
                if prop_to_get in i.aliases:
                    return i
        for b in self.barriers.values():
                if prop_to_get in b.aliases:
                    return b
        return None


    # -------------------------------------------------------
    def display(self):
        print(self.name)
        #print("-" * len(self.name))

        str = self.desc

        if len(self.barriers) > 0:
            for direction, b in self.barriers.items():
                str += " To the %s is a %s which is %s." % (direction, b.name, b.state)

        print(str)
        #print()

        if len(self.ground) > 0:
            for i in self.ground:
                print("%s" % (i.ground_desc))
            #print()

        if len(self.props) > 0:
            for p in self.props:
                print("%s" % (p.desc))
            #print()

        # show all the exists that aren't blocked
        for d, name in self.exits.items():
            if (d in self.barriers.keys()):
                prop = self.barriers[d]
                if (prop.state == "open"):
                    print("%s: %s" % (d.title(), name))
                else:
                    print("%s: %s (blocked by %s)" % (d.title(), name, prop.name))
            else:
                print("%s: %s" % (d.title(), name))



#########################################################
class Item:
    # -------------------------------------------------------
    def __init__(self, name, args):
        self.name = name
        self.desc = args['desc']
        self.ground_desc = args['ground_desc']
        self.aliases = args['aliases']

    def __str__(self):
        return self.desc

    def __repr__(self):
        return self.__str__()


#########################################################
class Prop:
    # -------------------------------------------------------
    def __init__(self, name, args):
        self.name = name
        self.desc = args['desc']
        self.aliases = args['aliases']

        try:
            self.state = args['state']
        except KeyError:
            self.state = None

        try:
            lock_item = items[args['locked_with']]
            self.locked_with = lock_item
        except KeyError:
            self.locked_with = None

        try:
            self.contains = [ ]
            for i in args['contains']:
                self.contains.append(items[i])
        except KeyError:
            self.contains = None    #might need to change to [    ]

    def __str__(self):
        if self.state != None:
            return "%s (%s)" % (self.name, self.state)
        else:
            return self.name

    def __repr__(self):
        return self.__str__()


#########################################################
class TextAdventureCmd(cmd.Cmd):
        prompt = '\n> '

        # -------------------------------------------------------
        def default(self, arg):
                print('I do not understand that command. Type "help" for a list of commands.')

        # -------------------------------------------------------
        def do_quit(self, arg):
                """Quit the game."""
                return True

        do_exit = do_quit

        # -------------------------------------------------------
        def do_look(self, arg):
            print()
            rooms[location].display()

        # -------------------------------------------------------
        def do_go(self, arg):
            global location
            ret = rooms[location].move_player(arg)
            if ret[0]:
                location = ret[1]
                print("You move %s." % (arg))
                print()
                rooms[location].display()
            else:
                print(ret[1])

        # -------------------------------------------------------
        def do_north(self, arg):
            self.do_go("north")

        # -------------------------------------------------------
        def do_east(self, arg):
            self.do_go("east")

        # -------------------------------------------------------
        def do_south(self, arg):
            self.do_go("south")

        # -------------------------------------------------------
        def do_west(self, arg):
            self.do_go("west")

        do_n = do_north
        do_e = do_east
        do_s = do_south
        do_w = do_west

        # -------------------------------------------------------
        def do_open(self, arg):
            if arg == "":
                print("Open what?")
                return

            prop_to_open = arg.lower()
            p = rooms[location].get_prop_by_alias(prop_to_open)

            if p == None:
                print("You don't see a %s here." % (prop_to_open))
            elif p.state == 'closed':
                p.state = 'open'
                print("You open the %s." % (p.name))
            elif p.state == 'locked':
                print("It's locked.")
            elif p.state == 'open':
                print("It's already open.")
            else:
                print("That doesn't look openable.")

        # -------------------------------------------------------
        def do_unlock(self, arg):
            global props

            if arg == "":
                print("Unlock what?")
                return

            prop_to_get = arg.lower()
            p = rooms[location].get_prop_by_alias(prop_to_get)

            if p == None:
                print("You don't see a %s here." % (prop_to_get))

            elif p.state == 'locked':
                if p.locked_with in inventory:
                    p.state = 'closed'
                    print("You unlock the %s with the %s." % (p.name, p.locked_with))
                else:
                    print("You need %s to unlock that" % (p.locked_with))

            elif p.state in ["closed", "open"]:
                print("It's already unlocked.")

            else:
                print("Doesn't look like you can unlock that.")

        # -------------------------------------------------------
        def do_get(self, arg):
            item_to_get = arg.lower()

            if item_to_get == '':
                print("Get what? Type 'look' to see what's here.")
                return

            r = rooms[location]
            i = r.get_item_by_alias(item_to_get)

            if i != None:
                inventory.append(i)
                r.ground.remove(i)
                print("You take the %s." % (i))
            else:
                print("You don't see a %s here." % (item_to_get))

        # -------------------------------------------------------
        def do_inventory(self, args):
            print("Inventory:")
            if len(inventory) == 0:
                print("    Nothing!")
            else:
                for i in inventory:
                    print("    %s" % (i))

        do_inv = do_inventory

        # -------------------------------------------------------
        def do_search(Self, arg):

            if arg == "":
                print("Search what?")
                return

            prop_to_get = arg.lower()
            p = rooms[location].get_prop_by_alias(prop_to_get)

            if p.contains != None:
                for i in p.contains:
                    rooms[location].ground.append(i)
                    p.contains.remove(i)
                    print("You search the %s and find %s." % (p, i))




#### initialize #################################################
with open('space.json') as json_file:
    data = json.load(json_file)

    #create all of the items first so they can be referenced
    for k in data['items']:
        items[k] = Item(k, data['items'][k])

    #create all of the props
    for k in data['props']:
        props[k] = Prop(k, data['props'][k])

    #create all of the rooms
    for r in data['rooms']:
        new_room = Room(r, data['rooms'][r]['desc'], data['rooms'][r]['exits'])

        try:
            for i in data['rooms'][r]['ground']:
                new_room.add_item(items[i])
        except KeyError:
            pass

        try:
            for p in data['rooms'][r]['props']:
                new_room.add_prop(props[p])
        except KeyError:
            pass

        try:
            for k, v in data['rooms'][r]['barriers'].items():
                new_room.add_barrier(k, props[v])
        except KeyError:
            pass

        rooms[r] = new_room



#### HELPERS ###################################################




#### main #######################################################
if __name__ == '__main__':
    print('Text Adventure Demo!')
    print('====================')
    print()
    print('(Type "help" for commands.)')
    print()
    rooms[location].display()
    TextAdventureCmd().cmdloop()
    print('Thanks for playing!')
