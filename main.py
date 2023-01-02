import os
import codecs
import sys
import key_strings as k
from preferences import *


def get_file_reader(filename):
    return codecs.open(filename, 'r', encoding='utf-8')


def get_file_writer(filename):
    return codecs.open(filename, 'w', encoding='utf-8')


def truncate_player_name(name, truncation_limit=NAME_LENGTH_LIMIT):
    return name[:truncation_limit]


def write_single_entry(writer, entry):
    writer.write(entry_to_line(entry))


def entry_to_line(entry):
    new_number = entry[k.NEW_NUMBER]
    opponent_key = entry[k.OPPONENT]
    my_key = entry[k.PLAYER]
    opponent_name = entry[opponent_key][k.NAME]
    opponent_fighters = entry[opponent_key][k.FIGHTERS]
    my_fighters = entry[my_key][k.FIGHTERS]
    note = entry[k.NOTE]

    padded_name = opponent_name + ' ' * (NAME_LENGTH_LIMIT - len(opponent_name))
    values = tuple([new_number, padded_name] + opponent_fighters + my_fighters + [note])
    socketed_string = "%s %s | %s %s %s  vs  %s %s %s  | %s\n"
    return socketed_string % values


def parse_ini_file(filename):
    result = {
        k.INITIAL_NUMBER: extract_padded_number_from_filename(filename),
        k.PLAYER_1: {
            k.NAME: '',
            k.FIGHTERS: []
        },
        k.PLAYER_2: {
            k.NAME: '',
            k.FIGHTERS: []
        },
        k.PLAYER: '',
        k.OPPONENT: ''
    }
    # Player 1's fighters are always listed first in the .ini file.
    player_key = k.PLAYER_1
    with get_file_reader(filename) as f:
        for line in f:
            line = line.strip()
            if line == 'Player 2':
                player_key = k.PLAYER_2
            elif line.startswith('Fighter'):
                fighter = line[8:]
                fighter_abbreviation = FIGHTER_ABBREVIATIONS[fighter]
                result[player_key][k.FIGHTERS].append(fighter_abbreviation)
            elif line[2:6] == 'Name':
                player_key = line[:2]
                player_name = line[7:]
                if player_name == OWNER_NAME:
                    result[k.PLAYER] = player_key
                else:
                    result[k.OPPONENT] = player_key
                result[player_key][k.NAME] = truncate_player_name(player_name)
    pad_fighters_list(result[k.PLAYER_1][k.FIGHTERS])
    pad_fighters_list(result[k.PLAYER_2][k.FIGHTERS])
    return result


def extract_padded_number_from_filename(filename):
    return filename[-8:-4]


def pad_fighters_list(fighters, pad_to=3):
    fighters += [EMPTY_FIGHTER] * (pad_to - len(fighters))


def map_replay_files(filenames):
    result = {k.NUMBERS: []}
    # a bit weird, but this setup lets us pluck two files at a time.
    iterator = iter(filenames)
    for ini_filename in iterator:
        rnd_filename = next(iterator)
        padded_number = extract_padded_number_from_filename(ini_filename)
        result[padded_number] = {k.INI_FILE: ini_filename, k.RND_FILE: rnd_filename}
        result[k.NUMBERS].append(padded_number)
    return result


def pad_number(n):
    return str(n).zfill(4)


def parse_delete_line(line):
    try:
        split_line = line.split('-')
        if len(split_line) == 1:
            # For example, act like "25" is actually "25-25"
            split_line += [int(split_line[0])]
        numbers = [i for i in range(int(split_line[0]), int(split_line[1])+1)]
        return [n for n in map(pad_number, numbers)]
    except ValueError as e:
        sys.stderr.write("Exiting prematurely due to unparseable delete line: %s\n" % line)
        sys.exit(1)


def parse_notes_line(line):
    try:
        i = line.find(' ')
        number = pad_number(line[:i])
        note = line[i:].strip()
        return [number, note]
    except IndexError as e:
        sys.stderr.write("Exiting prematurely due to unparseable notes line: %s\n" % line)
        sys.exit(2)


def parse_inputfile():
    result = {
        k.INPUT_DELETIONS: [],
        k.INPUT_NOTES: {}
    }
    if not os.path.exists(INPUT_FILENAME):
        return result
    with get_file_reader(INPUT_FILENAME) as f:
        key = ''
        for line in f:
            line = line.strip()
            if line in result.keys():
                key = line
            elif key == '' or line.startswith(COMMENT_PREFIX) or len(line) == 0:
                continue
            else:
                if key == k.INPUT_DELETIONS:
                    result[k.INPUT_DELETIONS] += parse_delete_line(line)
                elif key == k.INPUT_NOTES:
                    parsed = parse_notes_line(line)
                    result[k.INPUT_NOTES][parsed[0]] = parsed[1]
        return result


def decorate_entry(entry, new_number, input_file_dict):
    initial_number = entry[k.INITIAL_NUMBER]
    entry[k.NEW_NUMBER] = new_number
    entry[k.NOTE] = input_file_dict[k.INPUT_NOTES].get(initial_number, '.')


def delete_files(number, replay_file_dict):
    ini_file = replay_file_dict[number][k.INI_FILE]
    rnd_file = replay_file_dict[number][k.RND_FILE]
    os.remove(ini_file)
    os.remove(rnd_file)


def rename_files(number, new_number, replay_file_dict):
    if number == new_number:
        return
    ini_file = replay_file_dict[number][k.INI_FILE]
    rnd_file = replay_file_dict[number][k.RND_FILE]
    new_ini_file = ini_file.replace(number, new_number)
    new_rnd_file = rnd_file.replace(number, new_number)
    os.rename(ini_file, new_ini_file)
    os.rename(rnd_file, new_rnd_file)


def reset_input_file(entries):
    with get_file_writer(INPUT_FILENAME) as writer:
        writer.write(k.INPUT_DELETIONS + "\n")
        writer.write("\n")
        writer.write(k.INPUT_NOTES + "\n")
        for new_number, entry in entries.items():
            note = entry[k.NOTE]
            if note == '.':
                continue
            writer.write("%s %s\n" % (int(new_number), note))


def pluralize(collection_size, singular="", plural="s"):
    return singular if collection_size == 1 else plural


if __name__ == '__main__':
    os.chdir(REPLAYS_DIRECTORY)
    filenames = os.listdir('.')
    replay_file_dict = map_replay_files(filenames)
    replay_count = len(replay_file_dict[k.NUMBERS])
    print("Parsed and mapped %s replay%s." % (replay_count, pluralize(replay_count)))
    input_file_dict = parse_inputfile()
    with get_file_writer(OUTPUT_FILENAME) as output_writer:
        entries = {}
        output_number = 0
        for number in replay_file_dict[k.NUMBERS]:
            if number in input_file_dict[k.INPUT_DELETIONS]:
                delete_files(number, replay_file_dict)
            else:
                output_number += 1
                entry = parse_ini_file(replay_file_dict[number][k.INI_FILE])
                new_number = pad_number(output_number)
                decorate_entry(entry, new_number, input_file_dict)
                entries[new_number] = entry

                write_single_entry(output_writer, entry)
                rename_files(number, new_number, replay_file_dict)
        deletion_count = len(input_file_dict[k.INPUT_DELETIONS])
        print("Deleted %s replay%s." % (deletion_count, pluralize(deletion_count)))
        annotation_count = len(input_file_dict[k.INPUT_NOTES])
        print("Annotated %s replay%s." % (annotation_count, pluralize(annotation_count)))
        print("%s replay%s remain%s." % (output_number,
                                         pluralize(output_number),
                                         pluralize(output_number, singular="s", plural="")))
        reset_input_file(entries)

