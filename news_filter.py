from bs4 import BeautifulSoup
from selenium import webdriver
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import os
import webbrowser

NEWS_channel = ""
NEWS_URL = r""
BROWSER = r""
BROWSER_PATH = r""


def display_result(link_url_list, headline_text_list):
    result_window = Tk()
    result_window.title("Filter result")
    result_window.geometry("1000x800")
    canvas = Canvas(result_window)
    ver_bar = Scrollbar(result_window, orient='vertical', command=canvas.yview)
    hor_bar = Scrollbar(result_window, orient='horizontal', command=canvas.xview)
    # ver_bar.config(command=canvas.yview) also possible
    hyperlink_id_list = []

    for i in range(len(headline_text_list)):
        hyperlink = Label(canvas, text=headline_text_list[i], font="Helvetica 10 bold", fg="blue", cursor="hand2")
        article_url = link_url_list[i]
        hyperlink.bind("<Button-1>", lambda event, article_url=article_url: webbrowser.open(article_url))
        hyperlink.pack()
        id = canvas.create_window((0, i * 40), anchor='center', window=hyperlink, height=30)
        hyperlink_id_list.append(id)

    # this "dummy_window" is required because without it,
    # the last headline is covered by the horizontal scrollbar
    dummy_window = Label(canvas, text=" ", font="Helvetica 10 bold")
    dummy_window.pack()
    dummy_id = canvas.create_window((0, len(headline_text_list) * 40), anchor='center', window=dummy_window, height=30)
    hyperlink_id_list.append(dummy_id)

    canvas.configure(scrollregion=canvas.bbox('all'), yscrollcommand=ver_bar.set)
    canvas.configure(scrollregion=canvas.bbox('all'), xscrollcommand=hor_bar.set)

    result_window.grid_columnconfigure(0, weight=1)
    result_window.grid_columnconfigure(1, weight=1)
    result_window.grid_columnconfigure(2, weight=1)
    # column 3 will be left alone to avoid the canvas not being in the center
    result_window.grid_rowconfigure(0, weight=1)
    result_window.grid_rowconfigure(1, weight=1)

    canvas.grid(row=0, column=1, columnspan=3, rowspan=2, sticky="nsew")
    hor_bar.grid(row=1, column=0, columnspan=4, sticky=E + W + S)
    ver_bar.grid(row=0, column=3, rowspan=2, sticky=N + S + E)

    def _on_mousewheel(event):
        canvas.yview_scroll(-1 * int(event.delta / 100), "units")

    canvas.bind("<MouseWheel>", _on_mousewheel)
    result_window.mainloop()


def scan_headline_text(headline_text, filter_tuple):
    match_result = list()

    for i in range(len(filter_tuple)):
        if headline_text.lower().find(filter_tuple[i].lower()) != -1:
            match_result.append(filter_tuple[i])

    return match_result


def extract_tag_from_fox(main_soup):
    headline_container = []

    for i in range(19):
        temp = main_soup.find_all(class_=("article story-" + str(i)))
        for k in range(len(temp)):
            headline_container.append(temp[k])

    return headline_container


def extract_article_urls(filter_tuple):
    print("BROWSER: " + BROWSER)
    if BROWSER == "CHROME":
        driver = webdriver.Chrome(executable_path=BROWSER_PATH)
    else:
        driver = webdriver.Firefox(executable_path=BROWSER_PATH)
    driver.get(NEWS_URL)
    html = driver.page_source
    main_soup = BeautifulSoup(html, 'html.parser')
    headline_container = None
    if NEWS_channel == "CNN":
        headline_container = main_soup.find_all(class_="cd__headline")
    elif NEWS_channel == "FOX":
        headline_container = extract_tag_from_fox(main_soup)
    else:
        assert False

    driver.close()

    link_url_list = []
    headline_text_list = []
    no_of_headlines_filtered = 0

    for i in range(len(headline_container)):
        current_headline = headline_container[i]
        if NEWS_channel == "CNN":
            headline_text = current_headline.find(class_="cd__headline-text").text
        elif NEWS_channel == "FOX":
            headline_text = current_headline.find(class_="title").a.text
        else:
            assert False

        match_result = scan_headline_text(headline_text, filter_tuple)
        if len(match_result) == 0:
            try:
                if NEWS_channel == "CNN":
                    #CNN features a live screen with no headline text but has the class cd__headline.
                    #This needs to be skipped.
                    href_obj = current_headline.a["href"]
                elif NEWS_channel == "FOX":
                    href_obj = current_headline.find(class_="title").a["href"]
                else:
                    assert False
            except:
                print("unable to find url for: " + headline_text)
                continue
            headline_text_list.append(headline_text)
            print("Headline: " + headline_text)
            link_url = href_obj
            if NEWS_channel == "CNN":
                link_url = r"https://edition.cnn.com" + link_url
            link_url_list.append(link_url)
            print("Link: " + link_url)
        else:
            print("Filtered a headline with the word(s):", end="")
            for k in range(len(match_result)):
                print(" \"" + match_result[k] + "\"", end="")
                no_of_headlines_filtered += 1
            print()
        print()

    root = Tk()
    root.withdraw()
    messagebox.showinfo("Filtering complete",
                        "A total number of " + str(no_of_headlines_filtered) + " article(s) were filtered.")
    root.destroy()
    display_result(link_url_list, headline_text_list)


def submit(E1_in, filter_list_in):
    E1_text = E1_in.get()

    if len(E1_text) == 0:
        messagebox.showerror("Error", "Please enter a word before continuing")

    else:
        input_text = E1_text.lower().capitalize()
        print("E1's current text to add: " + input_text)
        try:
            filter_list_in.get(0, END).index(input_text)
            messagebox.showerror("Error", "\"" + E1_text + "\" already exists in the list.")
        except ValueError:
            filter_list_in.insert(END, input_text)

        E1_in.delete(0, 'end')


def remove(E1_in, filter_list_in):
    E1_text = E1_in.get()

    if len(E1_text) == 0:
        messagebox.showerror("Error", "Please enter a word before continuing")

    else:
        input_text = E1_text.lower().capitalize()
        print("E1's current text to remove: " + input_text)
        try:
            index = filter_list_in.get(0, END).index(input_text)
            filter_list_in.delete(index)
        except ValueError:
            messagebox.showerror("Error", "\"" + E1_text + "\" does not exist in the list.")

        E1_in.delete(0, 'end')


def begin_filtering(confirm_window, filter_tuple):
    confirm_window.destroy()
    extract_article_urls(filter_tuple)


def display_word_removal_screen(confirm_window, filter_tuple):
    confirm_window.destroy()
    word_removal_window = Tk()
    word_removal_window.geometry("450x360")
    word_removal_window.title("Remove words from the filter list")

    top_frame = Frame(word_removal_window)
    middle_frame = Frame(word_removal_window)
    bottom_frame = Frame(word_removal_window)

    top_frame.pack(side=TOP)
    middle_frame.pack(side=TOP)
    bottom_frame.pack(side=BOTTOM)

    blank_line = Label(middle_frame, text='\n')
    blank_line.pack(side=TOP)

    scrollbar = Scrollbar(middle_frame, orient="vertical")
    scrollbar.pack(side=RIGHT, fill=Y)

    filter_list = Listbox(middle_frame, yscrollcommand=scrollbar.set)
    for i in range(len(filter_tuple)):
        filter_list.insert(END, filter_tuple[i])
    filter_list.pack(side=LEFT, fill=BOTH)
    scrollbar.config(command=filter_list.yview)

    L1 = Label(top_frame, text="\n Please enter the words you wish to remove.\n", font="Helvetica 12 bold")
    L2 = Label(top_frame, text="Words to filter out:", font="Helvetica 10 bold")
    E1 = Entry(top_frame, bd=5, width=35)
    remove_button = Button(top_frame, text="Remove", command=lambda: remove(E1, filter_list))
    next_button = Button(bottom_frame, text="Next",
                         command=lambda: display_confirm_screen(word_removal_window, filter_list.get(0, END)), width=10)

    L1.pack(side=TOP)
    L2.pack(side=LEFT)
    remove_button.pack(side=RIGHT)
    E1.pack(side=RIGHT)

    blank_line = Label(bottom_frame, text="")
    blank_line.pack(side=BOTTOM)

    next_button.pack(side=BOTTOM)

    word_removal_window.resizable(width=False, height=False)
    word_removal_window.mainloop()
    print("")


def display_confirm_screen(word_addition_window, filter_tuple):
    word_addition_window.destroy()
    confirm_window = Tk()
    confirm_window.geometry("450x340")
    confirm_window.title("Confirm screen")

    top_frame = Frame(confirm_window)
    middle_frame = Frame(confirm_window)
    bottom_frame = Frame(confirm_window)
    top_frame.pack(side=TOP)
    middle_frame.pack(side=TOP)
    bottom_frame.pack(side=BOTTOM)

    L1 = Label(top_frame, text="\nDo you wish to proceed and filter out these words?\n", font="Helvetica 12 bold")
    L1.pack(side=TOP)

    L2 = Label(top_frame, text="Words to filter out:", font="Helvetica 10")
    L2.pack(side=TOP)

    scrollbar = Scrollbar(middle_frame, orient="vertical")
    scrollbar.pack(side=RIGHT, fill=Y)

    filter_list = Listbox(middle_frame, yscrollcommand=scrollbar.set, height=13)
    for i in range(len(filter_tuple)):
        filter_list.insert(END, filter_tuple[i])
    filter_list.pack(side=LEFT, fill=BOTH)
    scrollbar.config(command=filter_list.yview)

    yes_button = Button(bottom_frame, text="Proceed to filtering",
                        command=lambda: begin_filtering(confirm_window, filter_tuple), width=17)
    no_button_remove = Button(bottom_frame, text="Remove items",
                              command=lambda: display_word_removal_screen(confirm_window, filter_tuple), width=17)
    no_button_add = Button(bottom_frame, text="Add items",
                           command=lambda: display_word_addition_screen(confirm_window, filter_tuple), width=17)

    no_button_remove.pack(side=LEFT)
    no_button_add.pack(side=LEFT)
    yes_button.pack(side=LEFT)

    blank_line = Label(bottom_frame, text="\n\n")
    blank_line.pack(side=BOTTOM)

    confirm_window.resizable(width=False, height=False)
    confirm_window.mainloop()


def display_word_addition_screen_helper(filter_tuple):
    word_addition_window = Tk()
    word_addition_window.geometry("450x360")
    word_addition_window.title("Add words to the filter list")

    top_frame = Frame(word_addition_window)
    middle_frame = Frame(word_addition_window)
    bottom_frame = Frame(word_addition_window)

    top_frame.pack(side=TOP)
    middle_frame.pack(side=TOP)
    bottom_frame.pack(side=BOTTOM)

    blank_line = Label(middle_frame, text='\n')
    blank_line.pack(side=TOP)

    scrollbar = Scrollbar(middle_frame, orient="vertical")
    scrollbar.pack(side=RIGHT, fill=Y)

    filter_list = Listbox(middle_frame, yscrollcommand=scrollbar.set)
    for i in range(len(filter_tuple)):
        filter_list.insert(END, filter_tuple[i])
    filter_list.pack(side=LEFT, fill=BOTH)
    scrollbar.config(command=filter_list.yview)

    L1 = Label(top_frame, text="\n Please enter the words you wish to filter out.\n", font="Helvetica 12 bold")
    L2 = Label(top_frame, text="Words to filter out:", font="Helvetica 10 bold")
    E1 = Entry(top_frame, bd=5, width=35)
    submit_button = Button(top_frame, text="Submit", command=lambda: submit(E1, filter_list))
    next_button = Button(bottom_frame, text="Next",
                         command=lambda: display_confirm_screen(word_addition_window, filter_list.get(0, END)),
                         width=10)

    L1.pack(side=TOP)
    L2.pack(side=LEFT)
    submit_button.pack(side=RIGHT)
    E1.pack(side=RIGHT)

    blank_line = Label(bottom_frame, text="")
    blank_line.pack(side=BOTTOM)

    next_button.pack(side=BOTTOM)

    word_addition_window.resizable(width=False, height=False)
    word_addition_window.mainloop()


def cnn_selected(news_channel_selection_window, filter_tuple):
    news_channel_selection_window.destroy()
    global NEWS_channel
    global NEWS_URL

    NEWS_channel = "CNN"
    NEWS_URL = r"https://edition.cnn.com"
    display_word_addition_screen_helper(filter_tuple)


def fox_selected(news_channel_selection_window, filter_tuple):
    news_channel_selection_window.destroy()
    global NEWS_channel
    global NEWS_URL

    NEWS_channel = "FOX"
    NEWS_URL = r"https://www.foxnews.com"
    display_word_addition_screen_helper(filter_tuple)


def news_channel_selection(web_browser_selection_window, filter_tuple):
    web_browser_selection_window.destroy()

    news_channel_selection_window = Tk()
    news_channel_selection_window.geometry("300x300")
    news_channel_selection_window.title("News channel selection")

    top_frame = Frame(news_channel_selection_window)
    middle_frame = Frame(news_channel_selection_window)

    top_frame.pack(side=TOP)
    middle_frame.pack(side=TOP)

    L1 = Label(top_frame, text="\n Please select your news channel.\n", font="Helvetica 12 bold")
    L1.pack(side=TOP)

    CNN_button = Button(middle_frame, text="CNN",
                        command=lambda: cnn_selected(news_channel_selection_window, filter_tuple), width=17, height=2)
    FOX_button = Button(middle_frame, text="FOX",
                        command=lambda: fox_selected(news_channel_selection_window, filter_tuple), width=17, height=2)

    blank_line = Label(middle_frame, text='\n', height=1)
    CNN_button.pack(side=TOP)
    blank_line.pack(side=TOP)
    FOX_button.pack(side=TOP)

    news_channel_selection_window.resizable(width=False, height=False)
    news_channel_selection_window.mainloop()


def display_word_addition_screen(confirm_window, filter_tuple):
    confirm_window.destroy()
    display_word_addition_screen_helper(filter_tuple)

def request_web_driver_path(web_browser_selection_window, browser, filter_tuple):
    global BROWSER
    BROWSER= browser
    currdir = os.getcwd()
    global BROWSER_PATH
    BROWSER_PATH = filedialog.askopenfilename(parent=web_browser_selection_window, initialdir=currdir, title="Please select the browser's driver.")
    if len(BROWSER_PATH) > 0:
        print("You chose %s" % BROWSER_PATH)
        news_channel_selection(web_browser_selection_window, filter_tuple)


def web_browser_selection(filter_tuple):
    web_browser_selection_window = Tk()
    web_browser_selection_window.geometry("300x300")
    web_browser_selection_window.title("Web Browser selection")

    top_frame = Frame(web_browser_selection_window)
    middle_frame = Frame(web_browser_selection_window)

    top_frame.pack(side=TOP)
    middle_frame.pack(side=TOP)

    L1 = Label(top_frame, text="\n Please select your Web Browser.\n", font="Helvetica 12 bold")
    L1.pack(side=TOP)

    CHROME_button = Button(middle_frame, text="Google Chrome",
                        command=lambda: request_web_driver_path(web_browser_selection_window, "CHROME", filter_tuple), width=17, height=2)
    FIREFOX_button = Button(middle_frame, text="Mozilla Firefox",
                        command=lambda: request_web_driver_path(web_browser_selection_window, "FIREFOX", filter_tuple), width=17, height=2)

    blank_line = Label(middle_frame, text='\n', height=1)
    CHROME_button.pack(side=TOP)
    blank_line.pack(side=TOP)
    FIREFOX_button.pack(side=TOP)

    web_browser_selection_window.resizable(width=False, height=False)
    web_browser_selection_window.mainloop()

###########################main###########################
filter_tuple = tuple()
web_browser_selection(filter_tuple)

print("Program ended")
