"""Contains helper functions
that take too much space
in main.py

How syllable timings work:
    If a syllable lasts 0.61 seconds
    on the 0.62th second, the syllable
    shifts to the next.
    Though I would rather deduce it based
    on differences
"""

import logging
import math


def split_dialogue(text: str) -> list[tuple[str, bool]]:
    """Return a list of dialogue that
    has been split.
    
    The nth index of the returned list
    is the nth syllable.

    Each syllable is associated with a boolean
    which tells us whether or not the syllable
    does NOT end with a space."""

    start_from = 0
    ordering_so_far = []
    # False if char after syllable is ' ', true if '\\'
    text = text.replace('\n', ' ')  # no newlines
    while True:
        logging.debug('In split_dialogue while loop')
        nearest_space = text.find(' ', start_from)
        nearest_backslash = text.find('\\', start_from)
        # assert nearest_space != nearest_backslash
        if nearest_space == -1 and nearest_backslash != -1:
            temp = True
            start_from = nearest_backslash + 1
        elif nearest_space != -1 and nearest_backslash == -1:
            temp = False
            start_from = nearest_space + 1
        elif nearest_space != -1 and nearest_backslash != -1:
            temp = nearest_space > nearest_backslash
            start_from = min(nearest_space, nearest_backslash) + 1
        else:
            break
        ordering_so_far.append(temp)
    text = text.replace('\\', ' ')  # syllables
    syllable_list = text.split(' ')
    master = []
    for syllable, backslash in zip(syllable_list, ordering_so_far):
        temp = (syllable, backslash)
        master.append(temp)

    return master


def link_syllables(syllable_bool: list[tuple[str, bool]], timings: list[float],
                   newline_timings: list[float]) -> list[tuple[str, float, float, bool, bool]]:
    """Return list of tuple, with the format:
    (syllable, timing in ms, end time in ms, whether it is an end of word, toggle_next_line)
    timing is where the syllable starts.
    toggle_next_line is whether
    we expect newline_timings to include a value at 0ms.
    Indexes:
        1. the current syllable.
        2. when the syllable starts, in ms.
        3. when the syllable ends, in ms.
        4. whether or not the syllable does NOT end with a space.
        5. whether or not the syllable is the first syllable of a new line.
    """
    syllable = [syllable_b[0] for syllable_b in syllable_bool]
    cur_bool = [syllable_b2[1] for syllable_b2 in syllable_bool]
    if len(syllable) > len(timings):
        logging.warning('More syllables than timings')
    elif len(syllable) < len(timings):
        logging.warning('More timings than syllables')
    totals = []
    cur_line = 0  # start at 0
    first_iteration = True
    timings.append(timings[-1] + 10000.0)  # for our last line
    # for syllables, time in zip(syllable, timings):
    for i in range(0, min(len(syllable), len(timings))):
        try:
            next_line_time = newline_timings[cur_line]
            toggle_next_line = False
            if math.isclose(timings[i], next_line_time) or timings[i] > next_line_time:
                cur_line += 1
                toggle_next_line = True
            if first_iteration:
                toggle_next_line = True
                first_iteration = False  # and that only happens once
            instance = (syllable[i], timings[i]*1000, timings[i + 1]*1000, cur_bool[i], toggle_next_line)
            totals.append(instance)
        except IndexError:
            break
    return totals


def timestamp_from_ms(ms: float) -> str:
    """0:00:08.17
    h:mi:se.cs

    e.g. 1234ms, 123cs

    """
    cs = int((ms // 10) % 100)
    s = int((ms // 1000) % 60)
    minutes = int((ms // 60000) % 60)
    hr = int((ms // 3600000))  # typically zero
    string = f'{hr:01}:{minutes:02}:{s:02}.{cs:02}'
    return string
