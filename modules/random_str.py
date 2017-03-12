import random

def random_string():
    string = [
    "Has boiled their goose",
    "Should have thought twice about that one",
    "Is a filthy reposter",
    "Fucked up",
    "Was that Gleb?",
    "Come on man...",
    "'Repost', verb. Post (a letter or parcel) for a second or further time.",
    "I think we have seen this one already",
    "Can you not?",
    "Nice try",
    "Hey I just met you and this is crazy...",
    "Brain the size of a planet and I have to deal with your reposts",
    "Congratulations, this must be the first time you have come second."
    ]
    return string[random.randrange(0,10)]
