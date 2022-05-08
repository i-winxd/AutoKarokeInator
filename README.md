# Auto Karoke Inator
This app allows you to quickly create substation alpha subtitle files using existing ``.txt`` files
and a `.mid` file. Your `.txt` files control what is being said, and your `.mid` files control when the subtitles are
being shown.

This is best paired with YTSubConverter.

## How do I use this?

Read the instructions below.

### Creating your text file

Your text file contains the **transcript** of your video, so transcribe it. Use backslashes (``\``) to denote syllables,
and space characters to seperate words. There is **no** escape character for these two, so if you want two words to be
treated as one word, use an invisible unicode character.

Here's an example:
```Your text file con\tains the tran\script of your vi\deo, so tran\scribe it. Use back\slashes to de\note syl\lab\les, and space cha\ra\cters to se\per\ate words.```

Make sure you track every syllable accurately.

### Creating your MIDI file

Create your midi file using a midi editor, like FL Studio (strongly recommended). Put the audio you want to transcribe
in the timeline, create a midi out channel in the channel rack (or anything else provided that you'll put it in a MIDI
out channel), and 'chart' your voice in the piano roll like you were making a Friday Night Funkin' chart **(each note
represents a syllable)**. It doesn't matter what note you choose or how long your note is when charting your vocals -
only the start time of the note matters. **The only exception** is that the note isn't C6 (72) - we'll need that for
later.

Afterwards, only in the C6 note, any note you place there will be seen as new subtitle line starters. For example, if
the only notes in C6 play at 0:00, 0:04, and 0:07, your subtitles will switch at 0:00, 0:04, and 0:07. **It is strongly
recommended to only place notes in C6 such that they are timed with another syllable.**

**NOTE: YOU MAY NEED TO USE GHOST CHARACTERS (a.k.a. "-" and remove that post editing) TO DEAL WITH LONG RESTS**

**ABOUT INITINAL SONG DELAYS: THIS PROGRAM DOES NOT OFFER A WAY TO CREATE AN OFFSET. THIS MEANS YOU MUST DELAY THE LYRICS YOURSELF
BY INSERTING A GHOST LINE.**

**THIS PROGRAM WILL ALWAYS DROP THE LAST LINE. THIS ENSURES THAT THE ACTUAL LAST LINE WON'T GO ON FOREVER.
THIS MEANS YOUR LAST LINE SHOULD ALSO BE A GHOST LINE.**

## Running the .py file
If you don't like running .exe files randomly, you can run the .py files.
Here's how you do it:

1. Make sure python is installed on your computer.
2. Run the following commands: ``pip install mido`` and ``pip install easygui``
3. Run ``main.py``. One way is to open CMD with the directory where your .py file is at and type ``python main.py``.

Keep track of your syllables!!

## Running the program

Run the .EXE file. You'll first be asked to open the midi file you created. You will then be asked to open your
corresponding text file.

If the program isn't asking you to do anything for over 10 seconds it is likely stuck. Close and re-open it.

## Multiple midi channels

Best used if you have two different characters and want them both talking at the same time alongside have different
presets.

If you want to have over two text presets that you can edit in aegisub, here's how to do it:

1. Create another midi out channel
2. Assign that midi out channel a number other than 1 (hopefully do this in ascending order)
3. Chart that channel for that character
4. Export the midi (containing both characters)
5. When you open the midi with this program, it will prompt you to select a text file for each midi channel (a.k.a. for
   each character). The program will always prompt you in ascending order (always channel 1, 2, and so on.) Keep in mind
   that this program counts midi channels from **zero** while FL Studio counts midi channels from 1, so make conversions
   appropriately.

## A note about styles
Use the style manager to define styles. You may need to define
styles that are already present on your ``.ass`` file, like ``Custom1``.
You can find the styles manager on the top bar of Aegisub.

![image](https://user-images.githubusercontent.com/31808925/147286583-c2c9bc0d-68ae-48d8-8c87-430121907727.png)

