import random

class Quotes:
    def __init__(self):
        self.quotes = [


            "We have one path from the very beginning: either be good at something or get good at something - Summer Night Fantasy",
            "If you experience hell first, then everything is heaven to you - Babyish Love",
            "Get the highest grade with the lowest effort - by Babyish Storm",
            "Why make life complicated? - Babyish Tank",
            "I encourage people to cheat because your ability to not get caught is also being tested - Babyish Melody",
            "Heaven is for the weak - Babyish Myth",
            "No one cares about it more than you; if you don't care, no one care - Babyish Stealth",
            "Over coming the hell of a near death experience is the true secret behind a monster's explosive growth - Phoenix man",
            "We human beings are strong because we have the ability to change ourselves. - Saitama",
            "If I die here, then I'm a man that could only make it this far - Zoro",
            "Ora Ora Ora",
            "Ora Ora Ora Ora Ora Ora Ora Ora Ora Ora Ora Ora Ora Ora Ora Ora Ora Ora Ora Ora Ora Ora Ora Ora Ora Ora Ora Ora Ora Ora Ora Ora Ora Ora Ora Ora Ora Ora Ora",
            "I REJECT MY HUMANITY, JOJO! - Dio",
            "Don't forget. Always, somewhere, someone is fighting for you. As long as you remember her, you are not alone."

            ]

        self.total = len(self.quotes)


    def get_random_quote(self):

        return self.quotes[random.randint(0,self.total-1)]

