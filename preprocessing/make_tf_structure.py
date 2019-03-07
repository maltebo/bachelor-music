from preprocessing.vanilla_stream import VanillaStream


def make_tf_structure(vanilla_stream: VanillaStream):
    if len(vanilla_stream.parts) == 1:
        make_tf_melody(vanilla_stream)
    else:
        raise ValueError("Too many parts in the melody stream for current implementation")


def make_tf_melody(vanilla_stream: VanillaStream):
    pass
