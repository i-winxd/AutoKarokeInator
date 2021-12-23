"""Generating subtitle files

This is independent by channel, so we will 
need some global variables located in
preferences. The defaults are the variables,
although you can change them on request.

We will assume that we have data in this
format to start with:
    - A text file containing the dialogue
    - A *.json file containing the timings for
    each note. The timings are in ms.
    - We also need the timings for when the
    next subtitle line is reached. This will
    also be included with the json file.
    - If a subtitle line is empty just remove it.
    - In a nutshell: A list of ms timings, and
    a list of ms timings.
    - We also need a measure to prevent
    a line from being too long.
    - Firstly, list to syllable correspondence:
    a backslash character. and spaces.
    just remove all newlines first, because
    we do not care about newlines.
"""
# import logging

import easygui

import helpers as hp
import midi as midi_processor

PREAMBLE_PATH = 'preamble.txt'


class NoSubtitleTimingsError(Exception):
    """Exception raised when inserting a midi file
    where not all of the channels have at least 1 note on
    C6 (72)."""

    def __str__(self) -> str:
        """Return a string representation of this error."""
        return 'You didn\'t place subtitle timings in your midi file.'


def open_file(file: str) -> str:
    """Return file contents of any plain text file in the directory file.
    """
    with open(file) as f:
        file_text = f.read()
    return file_text


def write_file(text: str, filename: str) -> None:
    """Write file with given name.
    """
    with open(filename, 'w') as f:
        f.write(text)


def generate_style_nums(num: int) -> str:
    """Uh"""
    if num == 0:
        return 'Default'
    else:
        return 'Custom' + str(num)


class Preferences:
    """A class representing preferences.

    Instance Attributes:
        - offset: the offset.
        - style: always dependent on channel number.
    """
    offset: int
    style: str
    format_layer: str
    disable_karaoke: bool

    def __init__(self, offset: int, channel: int, disable_karoke: bool) -> None:
        """THE OFFSET IS IN CENTI SECONDS
        """
        self.offset = offset
        self.style = generate_style_nums(channel)
        self.format_layer = 'Dialogue: 0'
        self.disable_karaoke = disable_karoke


class SubtitleLine:
    """A class representing one line of subtitle.
    """
    format_layer: str
    start: str
    end: str
    style: str
    name: str
    margin_L: str
    margin_R: str
    margin_V: str
    effect: str
    text: str

    def __init__(self, subtitle_line_list: list, prefs: Preferences) -> None:
        """Init a subtitle
        line. Input is an instance
        from what is returned from
        create_subtitle_line_list().
        """
        self.start = hp.timestamp_from_ms(subtitle_line_list[0][1])
        self.end = hp.timestamp_from_ms(subtitle_line_list[-1][2])
        line_str = ''
        for syllable in subtitle_line_list:
            dur = int((syllable[2] - syllable[1]) // 10)
            space = '' if syllable[-2] else ' '
            dur_brace = '{\\k' + str(dur) + '}'
            syllable_text = f'{dur_brace}{syllable[0]}{space}'
            line_str += syllable_text
        self.text = line_str
        self.style = prefs.style
        self.name = ''
        self.margin_L = '0'
        self.margin_R = '0'
        self.margin_V = '0'
        self.effect = ''
        self.format_layer = prefs.format_layer

    def generate_line(self) -> str:
        """Return a line."""
        properties = [self.format_layer, self.start, self.end, self.style, self.name,
                      self.margin_L, self.margin_R, self.margin_V, self.effect, self.text.strip()]
        str_line = ','.join(properties)
        return str_line


class Event:
    """A class representing an event.
    """
    line_collection: list[str]
    string_collection: str
    string_collection_with_header: str

    def __init__(self, subtitle_line_list: list[list[tuple[str, float, float, bool, bool]]],
                 prefs: Preferences) -> None:
        header = 'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text'
        self.line_collection = [SubtitleLine(subtitle_line, prefs).generate_line() for
                                subtitle_line in subtitle_line_list]
        self.string_collection = self._joinup()
        self.string_collection_with_header = '[Events]\n' + header + '\n' + self.string_collection

    def _joinup(self) -> str:
        grid = '\n'.join(self.line_collection)
        return grid


class Project:
    """A class representing the project.
    """
    midi_dir: str
    offset: int  # in centi seconds
    events: list[Event]
    events_str: str
    preamble: str
    full_text: str
    disable_karaoke: bool

    midi_channel_info: dict[int, list[float]]
    midi_channel_special: dict[int, list[float]]
    channels: set[int]

    _extracted_midi_info: tuple[dict[int, list[float]], dict[int, list[float]], set[int]]
    _cur_text_dir: str
    _cur_text: str

    def __init__(self, midi_dir: str, offset: int = 0, disable_karaoke: bool = False) -> None:
        self.disable_karaoke = disable_karaoke
        self._extracted_midi_info = midi_processor.primary(midi_dir)
        self.midi_channel_info, self.midi_channel_special, self.channels = self._extracted_midi_info
        self.offset = offset
        self.events = []
        for channel in sorted(self.channels):
            cur_event = self._generate_event(channel)
            self.events.append(cur_event)
        self.events_str = (self._combine_events()).strip()
        self.preamble = open_file(PREAMBLE_PATH).strip()
        self.full_text = self.preamble + '\n' + self.events_str

    def _generate_event(self, channel: int) -> Event:
        """Generate an event from a midi channel
        """
        timings = self.midi_channel_info[channel]
        try:
            special_timings = self.midi_channel_special[channel]
        except KeyError:
            raise NoSubtitleTimingsError
        text_dir_input = f'text directory for channel {channel} (this is zero based)?'
        text_dir = easygui.fileopenbox(msg=text_dir_input,
                                       filetypes=["*.mid"])
        dialogue = open_file(text_dir)
        splitted_dialogue = hp.split_dialogue(dialogue)
        linked_syllables = hp.link_syllables(splitted_dialogue, timings, special_timings)
        subtitle_line_list = create_subtitle_line_list(linked_syllables)
        prefs = Preferences(self.offset, channel, self.disable_karaoke)
        return Event(subtitle_line_list, prefs)

    def _combine_events(self) -> str:
        """Combine all events to a single string
        """
        tot = []
        for event in self.events:
            tot.append(event.string_collection)
        return '\n'.join(tot)

    def export_file(self) -> None:
        """Export the file
        """
        write_file(self.full_text, 'export.ass')


def create_subtitle_line_list(linked_syllables: list[tuple[str, float, float, bool, bool]]) \
        -> list[list[tuple[str, float, float, bool, bool]]]:
    """Return a subtitle line list.
    """
    linelist_so_far = []
    line = []  # a list of syllables
    for i, syllable in enumerate(linked_syllables):
        if syllable[-1] or i == len(linked_syllables) - 1:
            if line != []:
                linelist_so_far.append(line)
            line = []  # reset it
        line.append(syllable)
    return linelist_so_far


if __name__ == '__main__':
    # temp_offset = int(input('State your offset (in ms): '))
    path = easygui.fileopenbox(msg='Select the *.mid file you want to open',
                               filetypes=["*.mid"])
    print('File selected')
    # logging.debug('Path chosen.')
    proj = Project(path)
    proj.export_file()
