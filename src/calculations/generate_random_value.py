import random
import string


def generate_random_value(value_type: str, value_name: str = "", seed=None):
    """Given a name of a type, return random data in that type.

    value_type: the name of the type as a string. The type will
    will be checked and the appropriate value will be generated.

    value_name: the name of the value, eg. team_number, preloaded_gamepiece

    seed: optional but will be used to set the random seed for tests.
    """
    if seed is not None:
        random.seed(seed)

    if type(value_type) is str:
        value_type = value_type.lower()
    else:
        raise TypeError('value_type must be a string (eg. "bool")')

    if value_type == "str":
        value = ""
        if "start_position" in value_name:
            return random.sample(["0", "1", "2", "3", "4"], random.randint(1, 3))
        # Generate specific random values relevant to the variable
        if value_name == "team_number":
            value = "".join([str(random.choice([j for j in range(10)])) for i in range(4)])
        elif "charge_level" in value_name:
            value = random.choice(["P", "D", "E"])
        elif "preloaded_gamepiece" in value_name:
            value = random.choice(["U", "O"])
        # if variable does not require a set of predefined constants, generate a random string
        # used for variables such as scout_name or other forgotten variables
        else:
            # Get the maximum length that the ascii_letters has for use to index it later
            max_length = len(string.ascii_letters) - 1
            # Repeat for a random amount of characters in a reasonable range
            for character in range(random.randint(5, 16)):
                # Also adds the seed if its defined, the random seed resets after use
                # this sets up the seed for each iteration
                if seed is not None:
                    random.seed(seed)
                # Get a random character from string.ascii_letters (a string of all ascii letters) and
                # add the char to the value, the final string
                value += string.ascii_letters[random.randint(0, max_length)]
        return value

    elif value_type == "int":
        return random.randint(0, 100)

    elif value_type == "float":
        return round(random.uniform(0, 100), 4)

    elif value_type == "bool":
        # Cast randint to bool
        return bool(random.randint(0, 1))

    elif value_type == "list":
        # For certain lists of strings, it is possible to generate a list of random specific enum values
        # generate random data for auto_pieces_start_position in match_collection_qr_schema
        if "auto_pieces_start_position" in value_name:
            return [random.choice([0, 1]) for i in range(4)]
        # generate random data for modes (which are lists) in calc_obj_team_schema
        elif "mode" in value_name:
            if "start_position" in value_name:
                return random.sample(["0", "1", "2", "3", "4"], random.randint(1, 3))
            elif "preloaded_gamepiece" in value_name:
                return random.sample(["U", "O"], random.randint(1, 2))
            elif "charge_level" in value_name:
                return random.sample(["P", "D", "E"], random.randint(1, 3))
        # other (unknown) lists
        else:
            return []

    elif "enum" in value_type:
        # for string Enums, generate more specific data relevant to that Enum
        if value_type.lower() == "enum[str]":
            if "charge_level" in value_name:
                if "auto" in value_name:
                    return random.choice(["N", "D", "E"])
                elif "tele" in value_name:
                    return random.choice(["N", "P", "D", "E"])
            elif "start_position" in value_name:
                return random.choice(["0", "1", "2", "3", "4"])
            elif "preloaded_gamepiece" in value_name:
                return random.choice(["U", "O"])
        # for other integer Enums, return an int
        else:
            return 1
