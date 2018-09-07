import utils

class HelpActions(object):

    def generate_random_name(self, name):
        return name + utils.generate_random_name()
