import pkgutil
from tkinter import Button, Canvas, Frame, Label, PhotoImage
from tkinter.colorchooser import askcolor
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import askretrycancel, askyesno, showinfo, showwarning
from tkinter.simpledialog import askstring

from eda_report.document import ReportDocument
from eda_report.exceptions import InputError
from eda_report.read_file import df_from_file
from eda_report.validate import validate_target_variable

# Load background image and icon
background_image = pkgutil.get_data(__name__, "images/background.png")
icon = pkgutil.get_data(__name__, "images/icon.png")

# Introductory text
description = """
A simple application to help speed up exploratory data analysis and reporting.

Select a file to analyse, and it will be automatically summarised. The result\
 is a report in .docx format, complete with summary statistics and graphs.
"""


class EDAGUI(Frame):  # pragma: no cover
    """This is the blueprint for the :mod:`tkinter` - based *graphical user
    interface* to the application.

    The graphical window is a :class:`tkinter.Frame`, with a brief description
    of what the application does, and a *button*.

    .. figure:: _static/screencast.*
       :alt: an image of the graphical user interface

    The button launches a *file-dialog* to navigate to and select a file to
    analyse.

    If a valid file is selected, *text-input widgets* and a *color-picker
    tool* pop up to help set the report's *title*, *target variable(optional)*
    and *graph color*.

    Afterwards, a file-dialog to set the desired location and name for the
    report appears.

    The :class:`~eda_report.document.ReportDocument` object is then used to
    create the exploratory data analysis report.
    """

    def __init__(self, master=None, **kwargs) -> None:
        super().__init__(master)
        self.master.title("eda_report")
        self.master.geometry("600x360")
        self.master.resizable(False, False)  # Fix window size
        self.master.wm_iconphoto(True, PhotoImage(data=icon))  # Add icon
        self._create_widgets()
        self.pack()

    def _create_widgets(self) -> None:
        """Creates the widgets for the graphical user interface: A *canvas*
        with the a *background image*, *introductory text*, and a *button* to
        select a file.
        """
        self.canvas = Canvas(self, width=600, height=400)

        # Set background image
        self.bg_image = PhotoImage(data=background_image)
        self.canvas.create_image((0, 0), image=self.bg_image, anchor="nw")

        # Add title
        self.canvas.create_text(
            (180, 80),
            text="eda_report",
            width=500,
            font=("Courier", 35, "bold"),
            fill="black",
        )

        # Add introductory text
        self.canvas.create_text(
            (300, 190),
            text=description,
            width=500,
            font=("Times", 13, "italic"),
            fill="black",
        )

        # Add a button to select input files
        self.button = Button(
            self,
            text="Select a file",
            default="active",
            bg="teal",
            fg="white",
            command=self._create_report,
            relief="flat",
        )
        self.canvas.create_window(
            (170, 260), anchor="nw", height=40, width=250, window=self.button
        )

        # Display current action
        self.current_action = Label(
            self, font=("Courier", 10, "italic"), bg="#dfddde"
        )
        self.canvas.create_window(
            (140, 325),
            anchor="nw",
            window=self.current_action,
        )

        self.canvas.pack()

    def _create_report(self) -> None:
        """Collects input from the graphical user interface, and uses the
        :class:`~eda_report.document.ReportDocument` object to generate a
        report.
        """
        self.current_action["text"] = "Waiting for input file..."
        self._get_data_from_file()
        if hasattr(self, "data"):
            self.current_action["text"] = "Waiting for report title..."
            self._get_report_title()
            self.current_action["text"] = "Waiting for target variable..."
            self._get_target_variable()
            self.current_action["text"] = "Waiting for graph color..."
            self._get_graph_color()
            self.current_action[
                "text"
            ] = "Analysing data & compiling the report..."
            self._get_save_as_name()

            # Generate the report using the collected arguments
            ReportDocument(
                self.data,
                title=self.report_title,
                graph_color=self.graph_color,
                output_filename=self.save_name,
                target_variable=self.target_variable,
            )

            self.current_action["text"] = ""
            showinfo(message=f"Done! Report saved as {self.save_name!r}.")
            del self.data  # Clear stale data

    def _get_data_from_file(self, retries=1) -> None:
        """Creates a file dialog to help navigate to and select a file to
        analyse.
        """
        file_name = askopenfilename(
            title="Select a file to analyse",
            filetypes=(
                ("All supported formats", ("*.csv", "*.xlsx")),
                ("csv", "*.csv"),
                ("excel", "*.xlsx"),
            ),
        )
        if file_name:
            # Load the file's data as a DataFrame
            self.data = df_from_file(file_name)
        elif not file_name and retries > 0:  # If no file is selected
            # Ask the user whether they'd like to retry
            if askretrycancel(message="Please select a file to continue"):
                self._get_data_from_file(retries - 1)
            else:
                self.master.quit()  # Quit if the user turns down retry prompt
        else:
            self.master.quit()  # Quit if no file selected and retry is spent

    def _get_report_title(self) -> None:
        """Creates a simple dialog to capture text input for the desired
        report title.
        """
        # Prompt user for report title
        report_title = askstring(
            title="Report Title",
            prompt="Please enter your preferred title for the report:",
            initialvalue="Exploratory Data Analysis Report",
        )

        self.report_title = (
            report_title
            if report_title
            else "Exploratory Data Analysis Report"
        )

    def _get_target_variable(self) -> None:
        """Inquire about the target variable, and create a text box to
        collect input.
        """
        if askyesno(message="Would you like to specify a target variable?"):
            self.target_variable = askstring(
                title="Target Variable",
                prompt="Please enter the name of the target variable:",
            )
            try:
                validate_target_variable(
                    data=self.data, target_variable=self.target_variable
                )
            except InputError as error:
                self.target_variable = None
                showwarning(
                    title="Invalid Target Variable", message=error.message
                )
        else:  # If user doesn't wish to supply a target variable
            self.target_variable = None

    def _get_graph_color(self) -> None:
        """Creates a graphical color picking tool to help set the desired
        color for the generated graphs.
        """
        # Returns a tuple e.g ((255.99609375, 69.26953125, 0.0), '#ff4500').
        color = askcolor(
            color="cyan", title="Please select a color for the graphs"
        )[-1]
        self.graph_color = color if color is not None else "orangered"

    def _get_save_as_name(self) -> None:
        """Create a file dialog to help select a destination folder and file
        name for the generated report.
        """
        # Propmt user for desired output file-name
        save_name = asksaveasfilename(
            initialfile="eda-report.docx",
            filetypes=(("Word document", "*.docx"),),
            title="Please select Save As file name",
        )
        self.save_name = save_name if save_name else "eda-report.docx"


def run_in_gui() -> None:
    """Starts the *graphical user interface* to the application.

    This provides the entry point for the ``eda_report`` console script
    (command).
    """
    app = EDAGUI()
    app.mainloop()
