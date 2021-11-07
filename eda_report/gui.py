import pkgutil

try:
    from tkinter import Button, Canvas, Frame, Label, PhotoImage, StringVar
    from tkinter.colorchooser import askcolor
    from tkinter.filedialog import askopenfilename, asksaveasfilename
    from tkinter.messagebox import (
        askretrycancel,
        askyesno,
        showinfo,
        showwarning,
    )
    from tkinter.simpledialog import askstring
except ImportError as error:
    print(
        f"{error}. Please visit https://tkdocs.com/tutorial/install.html",
        "for help installing it.",
    )

from eda_report.document import ReportDocument
from eda_report.exceptions import TargetVariableError
from eda_report.read_file import df_from_file
from eda_report.validate import validate_target_variable

background_image = pkgutil.get_data(__name__, "images/background.png")
icon = pkgutil.get_data(__name__, "images/icon.png")

description = (
    "A simple application to help speed up exploratory data analysis and "
    "reporting. Select a file to analyse, and it will be automatically "
    "summarised. The result is a report in Word format, complete with summary"
    " statistics and graphs."
)


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

    The :class:`~eda_report.document.ReportDocument` class is then used to
    create the exploratory data analysis report.
    """

    def __init__(self, master=None, **kwargs) -> None:
        super().__init__(master)
        self.master.title("eda-report")
        self.master.geometry("600x360")
        self.master.resizable(False, False)  # Fix window size
        self.master.wm_iconphoto(True, PhotoImage(data=icon))  # Add icon
        self._create_widgets()
        self.pack()

    def _create_widgets(self) -> None:
        """Creates the widgets for the graphical user interface: A Tk *Frame*
        with the *canvas(background image)*, *introductory text*, and a
        *button* to select files to analyse.
        """
        self.canvas = Canvas(self, width=600, height=360)

        # Set background image
        self.bg_image = PhotoImage(data=background_image)
        self.canvas.create_image((0, 0), image=self.bg_image, anchor="nw")

        # Add title
        self.canvas.create_text(
            (90, 45),
            anchor="nw",
            fill="black",
            font=("Courier", 35, "bold"),
            text="eda-report",
        )

        # Add introductory text
        self.canvas.create_text(
            (40, 105),
            anchor="nw",
            fill="black",
            font=("Courier", 12),
            text=description,
            width=500,
        )

        # Add a button to select input files
        self.button = Button(
            self,
            bg="#204060",
            command=self._create_report,
            default="active",
            fg="white",
            font=("Courier", 11),
            relief="flat",
            text="Select a file",
        )
        self.canvas.create_window(
            (175, 250), anchor="nw", height=40, width=250, window=self.button
        )

        # Show current action
        self.current_action = StringVar()
        self.display_current_action = Label(
            self,
            bg="#dfddde",
            font=("Courier", 10, "italic"),
            textvariable=self.current_action,
        )
        self.canvas.create_window(
            (140, 315),
            anchor="nw",
            window=self.display_current_action,
        )

        self.canvas.pack()

    def _create_report(self) -> None:
        """Collects input from the graphical user interface, and uses the
        :class:`~eda_report.document.ReportDocument` object to generate a
        report.
        """
        self.current_action.set("Waiting for input file...")
        self._get_data_from_file()

        if self.data is not None:
            self.current_action.set("Waiting for report title...")
            self._get_report_title()

            self.current_action.set("Waiting for target variable...")
            self._get_target_variable()

            self.current_action.set("Waiting for graph color...")
            self._get_graph_color()

            self.current_action.set("Analysing data & compiling the report...")
            self._get_save_as_name()

            # Generate the report using the collected arguments
            ReportDocument(
                self.data,
                title=self.report_title,
                graph_color=self.graph_color,
                output_filename=self.save_name,
                target_variable=self.target_variable,
            )
            self.current_action.set("")
            showinfo(message=f"Done! Report saved as {self.save_name!r}.")

            # Clear stale data to free up memory
            del self.data

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
            self.data = df_from_file(file_name)
        elif retries > 0:
            if askretrycancel(message="Please select a file to continue"):
                self._get_data_from_file(retries - 1)
            else:
                # No data if retry prompt is cancelled
                self.data = None
        else:
            # No data if no file is selected and retry has been used up
            self.data = None

    def _get_report_title(self) -> None:
        """Creates a simple dialog to capture text input for the desired
        report title.
        """
        report_title = askstring(
            title="Report Title",
            prompt="Please enter your preferred title for the report:",
            initialvalue="Exploratory Data Analysis Report",
        )

        self.report_title = report_title or "Exploratory Data Analysis Report"

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
            except TargetVariableError as error:
                self.target_variable = None
                showwarning(
                    title="Invalid Target Variable", message=error.message
                )
        else:
            self.target_variable = None

    def _get_graph_color(self) -> None:
        """Creates a graphical color picking tool to help set the desired
        color for the generated graphs.
        """
        # Returns a tuple e.g ((255.99609375, 69.26953125, 0.0), '#ff4500').
        color = askcolor(
            color="cyan", title="Please select a color for the graphs"
        )[-1]
        self.graph_color = color or "cyan"

    def _get_save_as_name(self) -> None:
        """Create a file dialog to help select a destination folder and file
        name for the generated report.
        """
        # Propmt user for desired output file-name
        save_name = asksaveasfilename(
            initialdir=".",
            initialfile="eda-report.docx",
            filetypes=(("Word document", "*.docx"),),
            title="Please select Save As file name",
        )
        self.save_name = save_name or "eda-report.docx"
