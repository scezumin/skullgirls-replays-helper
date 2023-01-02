#### _Delete, defragment, and annotate the Skullgirls replays files without breaking the brittle file structure -- even while Skullgirls is running._

## PRE-REQUISITES
You're gonna need Python 3.  Go install the latest one.


# GETTING STARTED
First, make a `preferences.py` file, based on the `preferences_TEMPLATE.py`, and fill it out with the values corresponding to your Steam name, your own computer, and your own, well, preferences.
Then, try running `main.py`, which should generate for you an `input.txt` and an `output.txt`.  If it doesn't work, you either have some invalid preferences or I haven't tested this script enough.  Thanks for helping me beta test it!

## HOW TO EDIT YOUR `input.txt`
This file has two parts: DELETIONS and NOTES.  A line in the DELETIONS section can have a number corresponding to a single replay number or a range of numbers.  NOTES has a single number and a note you want to leave for yourself about that game.  You can leave empty lines if you want, as well as comments that don't live beyond a single run of the script by prefixing the line with the `COMMENT_PREFIX` string configurable in your `preferences.py`.  For example:
```
DELETIONS:
2
# These matches were too easy to learn from.
5-10

NOTES:
4 what a fun game!
```

## HOW TO READ YOUR `output.txt`
This file should be pretty self-explanatory, but you _can_ set the `NAME_LENGTH_LIMIT` as well as customize the abbreviations for every fighter, including the spacer for a roster with only one or two fighters.  You probably shouldn't set anything to an empty string or spaces though -- if you do, you're on your own, as those waters are untested.  The output file will have lines that look something like this, corresponding to the file number, your opponent's name (truncated if necessary), your opponent's roster, your roster, and your notes (if you left any.)
```
0018 Opponent      | Pea ... ...  vs  MsF Cer ...  | too easy
0019 Opponent      | Pea ... ...  vs  Sqg ... ...  | quite a comeback!
```
