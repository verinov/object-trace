from object_trace import trace, print_traces


def producer_of_X(cache):
    cache["X"] = trace(42.42, "X")


def inscrutable_user_of_X(cache):
    cache["Y"] = cache["X"] + 1
    cache["X"] = 15.1


with print_traces():
    d = {}
    producer_of_X(d)
    inscrutable_user_of_X(d)
