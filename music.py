import os, sys
import curses
import json
from pygame import mixer


ROOT = "/sdcard"#os.path.abspath(os.sep)
# recursively list all audio files from the root directory
# save file path in a dict
# key: parent directory name
# value: full path of the file
# skip all child files and dirs if dirname starts with "."
def list_files(root) -> dict[str, list[str]]:
    files = {}
    for dirpath, dirnames, filenames in os.walk(root):
        for dirname in dirnames:
            if dirname.startswith("."):
                dirnames.remove(dirname)
        for filename in filenames:
            if filename.endswith(".mp3") or filename.endswith(".m4a"):
                files.setdefault(os.path.basename(dirpath), []).append(
                    os.path.join(dirpath, filename)
                )
    return files


# get indexed song list from "~/.cache/music/songlist.json"
# if not exixts, list files and create the cache
def get_songlist() -> dict[str, list[str]]:
    songlist = os.path.expanduser("~/.cache/music/songlist.json")
    if not os.path.exists(songlist):
        if not os.path.exists(os.path.dirname(songlist)):
            os.makedirs(os.path.dirname(songlist))
        files = list_files(ROOT)
        print(files)
        with open(songlist, "w") as f:
            json.dump(files, f)
    else:
        with open(songlist, "r") as f:
            files = json.load(f)
    return files

def main(stdscr: curses.window):
    curses.curs_set(0)
    stdscr.addstr(0, 0, "Indexing files...")

    files = get_songlist()
    dirs = list(files.keys())
    dirs.sort()
    index = 0
    mixer.init()

    # set color pair 1
    # foreground: white, background: green
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_GREEN)

    while True:
        stdscr.clear()
        # add directory names to the screen
        for i, d in enumerate(dirs):
            if i == index:
                stdscr.addstr(i, 0, d, curses.A_REVERSE)
            else:
                stdscr.addstr(i, 0, d)

        stdscr.refresh()
        key = stdscr.getkey()

        if key == "KEY_UP":
            index -= 1
            if index < 0:
                index = 0

        elif key == "KEY_DOWN":
            index += 1
            if index >= len(dirs):
                index = len(dirs) - 1

        # if key is "r", refresh list and update screen
        elif key == "r":
            files = get_songlist()

            # save update to cache
            with open(os.path.expanduser("~/.cache/music/songlist.json"), "w") as f:
                json.dump(files, f)

            dirs = list(files.keys())
            dirs.sort()
            index = 0

        elif key == "KEY_ENTER" or key == "\n":
            # show all files in the selected directory to the screen
            file_index = 0

            while True:
                stdscr.clear()
                # add directory name to the bottom of the screen with green background
                stdscr.addstr(curses.LINES - 1, 0, dirs[index], curses.color_pair(1))

                # add song names to the screen
                # determine how much lines screen can fit
                # only show the files that can fit in the screen
                # keep others hidden until the cursor moves to the bottom of the screen
                if file_index >= curses.LINES - 2:
                    reduced_list = files[dirs[index]][file_index - 2 - curses.LINES:]
                else:
                    reduced_list = files[dirs[index]][0:curses.LINES - 2]

                for i, f in enumerate(reduced_list):
                    if i == curses.LINES - 2:
                        break
                    if i == file_index:
                        stdscr.addstr(i, 0, os.path.basename(f), curses.A_REVERSE)
                    else:
                        stdscr.addstr(i, 0, os.path.basename(f))

                stdscr.refresh()
                key = stdscr.getkey()

                # if "b" is pressed, go back to the directory list
                if key == "b":
                    break
                # if "q" or "Q" is pressed, quit the program
                elif key == "q" or key == "Q":
                    sys.exit(0)
                # if "KEY_ENTER" or "\n" is pressed, play the selected file
                elif key == "KEY_ENTER" or key == "\n":
                    # play the selected file
                    mixer.music.load(files[dirs[index]][file_index])
                    mixer.music.play()

                    # if RIGHT arrow key is pressed, skip 10 seconds
                    # if LEFT arrow key is pressed, go back 10 seconds
                    while True:
                        key = stdscr.getkey()
                        if key == "KEY_RIGHT":
                            mixer.music.set_pos(mixer.music.get_pos() + 10)
                        elif key == "KEY_LEFT":
                            mixer.music.set_pos(mixer.music.get_pos() - 10)
                        elif key == "KEY_ENTER" or key == "\n":
                            mixer.music.stop()
                            break

                elif key == "KEY_UP":
                    file_index -= 1
                    if file_index < 0:
                        file_index = 0

                elif key == "KEY_DOWN":
                    file_index += 1
                    if file_index >= len(files[dirs[index]]):
                        file_index = len(files[dirs[index]]) - 1

                # if key is "r", reindex only this directory files, save them to songlist.json and update screen
                elif key == "r":

                    files[dirs[index]] = list_files(
                        os.path.dirname(files[dirs[index]][0])
                    )[dirs[index]]

                    with open(
                        os.path.expanduser("~/.cache/music/songlist.json"), "w"
                    ) as f:
                        json.dump(files, f)
                    file_index = 0

        # exit on "q" or "Q"
        elif key == "q" or key == "Q":
            sys.exit(0)


if __name__ == "__main__":
    curses.wrapper(main)
