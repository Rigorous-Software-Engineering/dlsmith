class Variable(object):
    def __init__(self, name, vtype, value):
        self.name = name
        self.type = vtype
        self.value = value

    def set_name(self, name):
        self.name = name
    def set_type(self, vtype):
        self.type = vtype
    def set_value(self, value):
        self.value = value


    def get_name(self):
        return self.name
    def get_type(self):
        return self.type
    def get_value(self):
        return self.value
