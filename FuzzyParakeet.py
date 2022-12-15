"""A Tkinter app that notifies you when a website has changed"""
import tkinter as tk
import tkinter.messagebox as tkmb
import tkinter.simpledialog as tkd
import json
import os
import platform
import requests
from bs4 import BeautifulSoup


def notify_website_change(website):
    """Notify the user that a website has changed"""
    system = platform.system()
    if system == "Darwin":
        os.system(f"osascript -e 'display notification "
                  f"\"There is new activity on {website}\"'")
    else:
        tkmb.showinfo(
            "Website Change",
            f"There is new activity on {website}"
        )


class FuzzyParakeet:
    """A class to manage the app"""

    def __init__(self):
        """Initialise the app"""
        self.master = tk.Tk()
        self.master.title("Fuzzy Parakeet")
        self.master.geometry("300x300")

        self.websites = []
        self.websites = self.load_websites()
        self.lbl_websites = tk.Label(self.master, text="My Websites:")
        self.lbl_websites.pack()
        self.listbox = tk.Listbox(self.master, width=1)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar = tk.Scrollbar(self.master)
        self.scrollbar.pack(side=tk.LEFT, fill=tk.BOTH)
        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.listbox.yview)
        self.btn_new = tk.Button(
            self.master,
            text="+",
            command=self.add_website
        )
        self.btn_new.pack(side=tk.BOTTOM, fill=tk.X)
        self.btn_remove = tk.Button(
            self.master,
            text="-",
            command=self.remove_website
        )
        self.btn_remove.pack(side=tk.BOTTOM, fill=tk.X)

        self.listbox.bind(
            "<KeyPress-BackSpace>",
            lambda event: self.remove_website()
        )

        for website in self.websites:
            self.listbox.insert(tk.END, website)

        self.update_websites()
        self.master.mainloop()

    def update_websites(self):
        """Check if any of the websites have changed"""
        for website in self.websites:
            try:
                website_text = BeautifulSoup(
                    requests.get(website).text,
                    'html.parser'
                ).text
            except:
                tkmb.showerror("Error", f"Could not access {website}")
                continue
            if os.path.exists(f"Websites/{website.replace('/', '_')}"):
                with open(f"Websites/{website.replace('/', '_')}") as file:
                    if website_text != file.read():
                        notify_website_change(website)
            with open(f"Websites/{website.replace('/', '_')}", "w") as file:
                file.write(website_text)
        self.master.after(300000, self.update_websites)

    def load_websites(self):
        """Load the websites from the config file"""
        try:
            with open("Websites.json") as file:
                websites = json.load(file)
            return websites
        except FileNotFoundError:
            with open("Websites.json", "w") as file:
                json.dump(self.websites, file)
            return self.websites
        except json.JSONDecodeError:
            with open("Websites.json", "w") as file:
                json.dump(self.websites, file)
            return self.websites

    def save_websites(self):
        """Save the websites to the config file"""
        with open("Websites.json", "w") as file:
            json.dump(self.websites, file)

    def remove_website(self):
        """Remove a website from the list"""
        try:
            website = self.listbox.get(self.listbox.curselection())
        except tk.TclError:
            tkmb.showwarning("No Website Selected", "Please select a website")
            return
        if tkmb.askyesnocancel("Remove Website",
                               f"Are you sure you want to remove {website}?"):
            self.listbox.delete(self.websites.index(website))
            self.websites.remove(website)
            self.save_websites()
            os.remove(f"Websites/{website.replace('/', '_')}")

    def add_website(self):
        """Get a website name and add it to the list"""
        website = tkd.askstring("Add Website", "Enter the website name:")
        if website:
            self.websites.append(website)
            self.listbox.insert(tk.END, website)
            self.save_websites()
            tkmb.showinfo("Website Added", f"{website} has been added")


def main():
    """Run the app"""
    FuzzyParakeet()


if __name__ == "__main__":
    main()
