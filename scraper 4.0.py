from scraperClass import Scraper
import sys
from cx_Freeze import setup, Executable
from tkinter import *
from tkinter import filedialog

"""
Name: prepare_scrape
Input: None
Returns: None
Effects:    changes the saved location of the CSV file for better accessibility
"""
def prepare_scrape():
    save_csv()

    start_scrape()

"""
Name: save_csv
Input: None
Returns: None
Effects:    changes the saved location of the CSV file for better accessibility
"""
def save_csv():
    filename = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV files', '*.csv')])

    scraper.file_name = filename


"""
Name: start_scrape
Input: None
Returns: None
Effects:    combines all input data from different fields and 
            organizes them in preparation for the scraper

            double checks if all input data are the correct format
"""
def start_scrape():
    attributes = {"roll_id": 1, "username": 2, "password": 3, "time": 4}

    attributes["roll_id"] = rollIdField[1].get().replace(" ", '').split(",")
    attributes["username"] = usernameField[1].get()
    attributes["password"] = passwordField[1].get()
    attributes["time"] = timeSlider.get()

    checking = error_checking(attributes)

    if checking != True:
        return
    else:
        print("failed")

        for key, value in attributes.items():
            setattr(scraper, key, value)

        scraper.start()


"""
Name: error_checking
Input: a dictionary with list of int, string, string, integer
Returns: boolean
Effects:    checks if Roll ID is a list of integers
            checks if username and password are strings
            checks if geckoFile is selected
"""
def error_checking(attributes: dict[list[int], str, str, int]) -> bool:
    if isinstance(attributes["roll_id"], list):
        for i in attributes["roll_id"]:
            if not isinstance(i, int):
                pop_up_error("Roll ID is not a list of numbers, please check again")
                return False
    else:
        pop_up_error("Roll ID is not a list, please check again.")
        return False

    if (not isinstance(attributes["username"], str)) or (not isinstance(attributes["password"], str)):
        pop_up_error("Username/Password is incorrect format, please check again.")
        return False
    
    try:
        geckoFile
    except Exception:
        pop_up_error("GeckoDriver not selected, please try selecting again.")
        return False


"""
Name: pop_up_error
Input: string
Returns: None
Effects:    creates a pop-up window that displays the error message
"""
def pop_up_error(error_string: str):
    popup = Toplevel()
    popup.title("Error")
    popup.geometry("300x100")

    # add a label with the message
    label = Label(popup, text= error_string)
    label.pack(pady=10)

    # display the popup and wait for it to be closed
    popup.wait_window()


"""
Name: select_gecko
Input: None
Returns: None
Effects:    allows the selection of GeckoDriver location on 
            local device
"""
def select_gecko():
    global geckoFile
    geckoFile = filedialog.askopenfilename(filetypes=[("Executable files", "*.exe")])

    setattr(scraper, 'path', geckoFile)

    geckoField[1].config(text = geckoFile, fg = "blue", wraplength = 300)
    
    print("Selected GeckoDriver file:", scraper.path)


"""
Name: insert_background_text
Input: Tkinter Entry, string
Returns: None
Effects:    creates a grey background text in text field
"""
def insert_background_text(entry: Entry, text: str):
    entry.insert("0", text)
    entry.config(foreground="grey")


"""
Name: insert_background_text
Input: Tkinter Entry, string
Returns: None
Effects:    clears the background text of the entry
            if the text in the entry matches the
            input text
"""
def clear_background_text(entry: Entry, text: str):
    if entry.widget.get() == text:
        entry.widget.delete("0", "end")
        entry.widget.config(foreground="black")



"""
Name: make_frame
Input: Tkinter Entry, string, string, int
Returns: Tuple(Tkinter Label, Tkinter Entry)
Effects:    creates a field within the input frame with the given
            input strings as field name and background text for 
            the field

            sets the input/entry field with a size of input integer
"""
def make_frame(input_frame: Frame, input_text: str, input_value: str, size: int) -> tuple[Label, Entry]:
    label = Label(input_frame, text=input_text)

    if (size != 0):
        entry = Entry(input_frame, width = size)
    else:
        entry = Entry(input_frame)

    insert_background_text(entry, input_value)
    entry.bind("<FocusIn>", lambda entry: clear_background_text(entry, input_value))
    entry.bind("<FocusOut>", lambda entry: insert_background_text(Entry(entry), input_value))
    return (label, entry)


"""
Name: frame1
Input: None
Returns: None
Effects:    creates the basic fields for every Entry and Label
            fits them all inside a grid for better organization
"""
def frame1():
    global rollIdField
    global usernameField
    global passwordField
    global geckoField
    global timeSlider

    frame1 = Frame(root, padx = 15)
    frame1.grid(row = 0, column = 0, sticky = "w")

    rollIdField = make_frame(frame1, "Roll ID:", "Eg. 123456, 987654, 00000", 40)

    usernameField = make_frame(frame1, "Username:", "Enter your Username", 0)

    passwordField = make_frame(frame1, "Password:", "Enter your Password", 0)

    geckoField = (Label(frame1, text = "GeckoDriver Location:", wraplength=100), Label(frame1, text = "Location", fg = "grey"))

    buttonScrape = Button(frame1, text="Scrape", command=start_scrape)

    subFrame1 = Frame(frame1)

    timeSlider = Scale(subFrame1, from_=0, to=60, orient=HORIZONTAL)
    timeSlider.pack(side="left", padx = 10)

    sliderLabel = Label(subFrame1, text="seconds")
    sliderLabel.pack(side="left")

    timeField = (Label(frame1, text = "ReCaptcha Time Needed:", wraplength=100), subFrame1)

    buttonSelect = Button(frame1, text="Select GeckoDriver Location", command = select_gecko)

    rollIdField[0].grid(row=0, column=0)
    rollIdField[1].grid(row=0, column=1, sticky= 'w')

    usernameField[0].grid(row=1, column=0)
    usernameField[1].grid(row=1, column=1, sticky= 'w')

    passwordField[0].grid(row=2, column=0)
    passwordField[1].grid(row=2, column=1, sticky= 'w')

    geckoField[0].grid(row=3, column=0)
    geckoField[1].grid(row=3, column=1, sticky = "w")
    buttonSelect.grid(row=4, column=1, sticky = "w")

    timeField[0].grid(row=5, column=0)
    timeField[1].grid(row=5, column=1, sticky = "w")

    buttonScrape.grid(row=6, column=1, sticky = "w")
    

"""
Name: instructionFrame
Input: None
Returns: None
Effects:    Creates a set of instructions for the usage of the scraper
            Instructions are numbered and organized below all the entry fields
"""
def instructionFrame():
    frame2 = Frame(root, padx= 15)
    frame2.grid(row = 1, column = 0, sticky = "w")
    instructionTitle = Label(frame2, text="Instructions", font = ("bold", 24))

    instructions = ["Enter the Roll ID from Jondo Website into the \"Roll ID\" box above separated by commas \n Eg. 921706, 921705, 921733",
                    "Enter your login username and password to the Jondo Website",
                    "Click the select \"GeckoDriver Location Button\" to choose the location of your local GeckoDriver",
                    "Change the \"ReCaptcha Time Needed\" to a more suitable one (Higher the number, longer the time needed)",
                    "A FireFox window will open with a ReCaptcha that needs to be completed, please complete it to proceed",
                    "Please let scraper automatically access the webpages and scrape the information without interference",
                    "A prompt to download a file will pop up upon completing the scrape, the file would be a .csv file containing the scraped information",
                    "You may enter more Roll ID for scraping or exit the application"]

    for i, instruction in enumerate(instructions):
        instructionLabel = Label(frame2, text = f"{i + 1}. {instruction}", wraplength= 350, justify="left")
        instructionLabel.grid(row = i + 1, column = 0, sticky = "w")

    instructionTitle.grid(row = 0, column = 0)



scraper = Scraper()

root = Tk()
root.geometry("400x500")
root.title("Jondo WebScraper")

frame1()
instructionFrame()

root.mainloop()