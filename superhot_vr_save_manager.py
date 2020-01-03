#!/usr/bin/python3

license = """
    superhot_vr_save_manager: A small save manager for managing Superhot VR save files.
    Copyright (C) 2019  hammy3502

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import sys
import platform
import os
import json

try:
    import tkinter
    del tkinter  # Let it import with PySimpleGUI
except ImportError:
    print("Tkinter not installed! Exiting...")
try:
    import PySimpleGUI as sg
except ImportError:
    print("PySimpleGUI not installed! Exiting...")

db = {}
max_path_chars = 247

def full(file_name):
    """Full Path.

    Converts ~'s, .'s, and ..'s to their full paths (~ to /home/username)

    Args:
        file_name (str): Path to convert

    Returns:
        str: Converted path

    """
    return os.path.abspath(os.path.expanduser(os.path.expandvars(file_name)))


def write_db():
    """Write Database to File."""
    try:
        with open(full("%userprofile%\AppData\LocalLow\SUPERHOT_Team\SUPERHOT_VR\SaveManagerConfig.json"), "w") as dbf:
            json.dump(db, dbf)
        print("Database written!")
    except FileNotFoundError:
        print(json.dumps(db))
        print("Database failed to be written and is dumped to screen!")


def get_db():
    """Get Database."""
    global db
    nprint("Attempting database load: ")
    if not os.path.isfile(full("%userprofile%\AppData\LocalLow\SUPERHOT_Team\SUPERHOT_VR\SaveManagerConfig.json")):
        print("Doesn't exist! Loading empty one.")
        db = {}
    else:
        try:
            with open(full("%userprofile%\AppData\LocalLow\SUPERHOT_Team\SUPERHOT_VR\SaveManagerConfig.json")) as f:
                db = json.load(f)
                print("Loaded!")
        except json.decoder.JSONDecodeError:
            print("Failed to decode!")
            sys.exit(1)


def nprint(to_print):
    """Print without newline.

    Args:
        to_print (str): String to print.

    """
    print(to_print, end="")


def get_input(question, answers, title="Unofficial Superhot VR Save Manager"):
    """Get Input from User.

    Args:
        question (str): Question to ask
        answers (str[]): List of answers

    Returns:
        str: Answer

    """
    layout = [
        [sg.Text(question)],
        [sg.Combo(answers, key="option"), sg.Button("Submit")]
    ]
    window = sg.Window(title, layout, disable_close=True)
    while True:
        event, values = window.Read()
        if event == "Submit":
            if values["option"] in answers:
                window.Close()
                return values["option"]

def run_checks():
    """Run Checks for Valid System.

    Returns:
        str: "first_time" if first time being run, "pass" otherwise.
    """
    print("Running checks...")
    nprint("On Windows: ")
    if platform.system() != "Windows":
        print("Nope")
        sg.Popup("This program currently only supports Windows!")
        sys.exit(1)
    else:
        print("Yep!")
    nprint("Save folder exists: ")
    if not os.path.isdir(full("%userprofile%\AppData\LocalLow\SUPERHOT_Team\SUPERHOT_VR")):
        print("Missing")
        sg.Popup("You haven't created a savefile for Superhot VR!")
        sys.exit(1)
    else:
        print("Good to go!")
    nprint("Database file exists: ")
    if not os.path.isfile(full("%userprofile%\AppData\LocalLow\SUPERHOT_Team\SUPERHOT_VR\SaveManagerConfig.json")):
        print("Not found! Will be created on first save... ")
        return "first_time"
    else:
        print("Database found!")
        return "pass"


def wizard():
    """Main Wizard for Save Manager."""
    current_profile = None
    try:
        current_profile = db["current_profile"]
    except KeyError:
        print("New user! Get name for current savefile...")
        while current_profile is None:
            current_profile = sg.PopupGetText("You already have a save file! Please type in a name to give it: ")
            if not str(current_profile).replace("-", "").replace("_", "").isalnum():
                sg.Popup("Name can only contain letters, numbers, -'s, and _'s!")
                current_profile = None
            if len(full("%userprofile%\AppData\LocalLow\SUPERHOT_Team\SUPERHOT_VR\VRsuper.hot.{}".format(current_profile))) > max_path_chars:
                sg.Popup("Filename too long!")
                current_profile = None
        db["current_profile"] = current_profile
        write_db()
    action = "a"
    while action != "Exit":
        files = []
        save_labels = []
        nprint("Getting files in Superhot VR directory: ")
        for f in os.listdir(full("%userprofile%\AppData\LocalLow\SUPERHOT_Team\SUPERHOT_VR")):
            if os.path.isfile(full("%userprofile%\AppData\LocalLow\SUPERHOT_Team\SUPERHOT_VR\{}".format(f))) and f.startswith("VRsuper.hot."):
                files.append(f)
                save_labels.append(f[12:]) 
        print("Done!")
        action = get_input("Current Profile: {}\nPick an option: ".format(current_profile), ["Rename current profile", "Change profile", "Create new profile", "Delete profile", "Exit"])
        if action == "Rename current profile":
            if not os.path.isfile(full("%userprofile%\AppData\LocalLow\SUPERHOT_Team\SUPERHOT_VR\VRsuper.hot")):
                sg.Popup("You have no savefile!")
            else:
                current_profile = None
                while current_profile is None:
                    current_profile = sg.PopupGetText("Please type a new name for the save file: ")
                    if not str(current_profile).replace("-", "").replace("_", "").isalnum():
                        sg.Popup("Name can only contain letters, numbers, -'s, and _'s!")
                        current_profile = None
                    if len(full("%userprofile%\AppData\LocalLow\SUPERHOT_Team\SUPERHOT_VR\VRsuper.hot.{}".format(current_profile))) > max_path_chars:
                        sg.Popup("Filename too long!")
                        current_profile = None
                db["current_profile"] = current_profile
                write_db()
        elif action == "Change profile":
            new_profile = None
            while new_profile == None:
                new_profile = get_input("Please select the save file to change to", save_labels)
            if os.path.isfile(full("%userprofile%\AppData\LocalLow\SUPERHOT_Team\SUPERHOT_VR\VRsuper.hot")):
                os.rename(full("%userprofile%\AppData\LocalLow\SUPERHOT_Team\SUPERHOT_VR\VRsuper.hot"), full("%userprofile%\AppData\LocalLow\SUPERHOT_Team\SUPERHOT_VR\VRsuper.hot.{}".format(current_profile)))
            current_profile = new_profile
            db["current_profile"] = current_profile
            write_db()
            os.rename(full("%userprofile%\AppData\LocalLow\SUPERHOT_Team\SUPERHOT_VR\VRsuper.hot.{}".format(current_profile)), full("%userprofile%\AppData\LocalLow\SUPERHOT_Team\SUPERHOT_VR\VRsuper.hot"))
        elif action == "Create new profile":
            if os.path.isfile(full("%userprofile%\AppData\LocalLow\SUPERHOT_Team\SUPERHOT_VR\VRsuper.hot")):
                os.rename(full("%userprofile%\AppData\LocalLow\SUPERHOT_Team\SUPERHOT_VR\VRsuper.hot"), full("%userprofile%\AppData\LocalLow\SUPERHOT_Team\SUPERHOT_VR\VRsuper.hot.{}".format(current_profile)))
            current_profile = None
            while current_profile is None:
                current_profile = sg.PopupGetText("Please type a new name for the save file: ")
                if not str(current_profile).replace("-", "").replace("_", "").isalnum():
                    sg.Popup("Name can only contain letters, numbers, -'s, and _'s!")
                    current_profile = None
                if len(full("%userprofile%\AppData\LocalLow\SUPERHOT_Team\SUPERHOT_VR\VRsuper.hot.{}".format(current_profile))) > max_path_chars:
                    sg.Popup("Filename too long!")
                    current_profile = None
            db["current_profile"] = current_profile
            write_db()
            sg.Popup("Please start Superhot VR to finish the creation of your save file!")
            sys.exit(0)
        elif action == "Delete profile":
            del_profile = None
            while del_profile == None:
                del_profile = get_input("Please select the save file to delete: ", save_labels)
            os.remove(full("%userprofile%\AppData\LocalLow\SUPERHOT_Team\SUPERHOT_VR\VRsuper.hot.{}".format(del_profile)))
        elif action == "Exit":
            sys.exit(0)
    

    
            
    


def main():
    """Main Entrypoint."""
    check = run_checks()
    if check == "first_time":
        license_check = sg.PopupYesNo("Welcome to the UNOFFICIAL Superhot VR Save Manager! By using this save manager, you agree to the following license:\n" + license + "\nIf you agree, click \"Yes\". Otherwise, click \"No\".")
        if license_check == "No":
            sys.exit(0)
    get_db()
    wizard()




if __name__ == "__main__":
    main()

