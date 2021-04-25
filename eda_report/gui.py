import pkgutil
from tkinter import Button, Canvas, Frame, PhotoImage, Tk, Label
from tkinter.colorchooser import askcolor
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showinfo
from tkinter.simpledialog import askstring

from eda_report import get_word_report
from eda_report.read_file import df_from_file

# Load background image and icon
background_image = pkgutil.get_data(__name__, "images/background.png")
icon = pkgutil.get_data(__name__, "images/icon.png")

# Introductory text
description = """
A simple application to help speed up exploratory data analysis and reporting.

Select a file to analyse, and it will be automatically summarised. The result\
 is a report in .docx format, complete with summary statistics and graphs.

"""


def run_in_gui():
    """Starts the *graphical user interface* to the application.

    This provides the entry point for the ``eda_report`` console script
    (command).
    """
    root = Tk()
    root.title('eda_report')
    root.geometry('600x400')
    root.resizable(0, 0)
    root.wm_iconphoto(True, PhotoImage(data=icon))
    EDAGUI(master=root)
    root.mainloop()


class EDAGUI(Frame):
    """This is the blueprint for the `tkinter`_ - based *graphical user
    interface* to the package/application.

    The graphical window is a *tkinter* ``Frame``, with a *button* that
    opens a *file-dialog* to navigate to and select a file to analyse.

    Once a file is selected, a *text-input widget* and *color-picker tool* pop
    up to help set the report's *title* and *graph color* respectively.
    Finally, a file-dialog to set the desired location and name for the report
    is shown.

    The collected *input file-path*, *title*, *color* and *output file-path*
    are then passed to the :func:`~eda_report.get_word_report` function to
    create the exploratory data analysis report document. A message-box will
    be shown when the report is ready, or when an exception occurs.

    .. _`tkinter`: https://docs.python.org/3/library/tkinter.html
    """

    def __init__(self, master=None, **kw):
        super().__init__(master)
        self.master = master
        self.configure(height=400, width=600)
        self._create_widgets()
        self.pack()

    def _create_widgets(self):
        """Creates the widgets for the graphical user interface: A *canvas*
        with the a *background image*, *introductory text*, and a *button* to
        select a file.
        """
        # Create the canvas
        self.canvas = Canvas(self, width=600, height=400)

        # Set background image
        self.bg_image = PhotoImage(data=background_image)

        self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")

        # Add introductory text
        self.canvas.create_text(180, 80, text='eda_report', width=500,
                                font=("Courier", 35, 'bold'), fill="black")
        self.canvas.create_text(300, 190, text=description, width=500,
                                font=("Times", 13, 'italic'), fill="black")

        # Add a button
        self.button = Button(
            self, text='Select a file', default='active', bg='teal',
            fg='white', command=self.create_report, relief='flat',
        )
        self.canvas.create_window(170, 270, anchor='nw', height=40, width=250,
                                  window=self.button)
        # Display current action
        self.current_action = Label(font=("Courier", 10, 'italic'))
        self.canvas.create_window(
            140, 350, anchor='nw', window=self.current_action,
        )

        self.canvas.pack()

    def create_report(self):
        """Collects input from the graphical user interface, and uses the
        :func:`~eda_report.get_word_report` function to generate a report.
        """
        self.current_action['text'] = 'Waiting for input file...'
        self._get_data_from_file()

        if hasattr(self, 'data'):
            self.current_action['text'] = 'Waiting for report title...'
            self._get_report_title()
            self.current_action['text'] = 'Waiting for graph color...'
            self._get_graph_color()
            self.current_action['text'] = \
                'Analysing data & compiling the report...'
            self._get_save_as_name()

            # Generate the report using the provided arguments
            get_word_report(self.data, title=self.report_title,
                            graph_color=self.graph_color,
                            output_filename=self.save_name)

            # Pop up message to declare that the report is finished
            self.current_action['text'] = ''
            showinfo(message=f'Done! Report saved as {self.save_name!r}.')

    def _get_data_from_file(self, retries=2):
        """Creates a file dialog to help navigate to and select a file to
        analyse.
        """
        file_name = askopenfilename(
            title='Select a file to analyse',
            filetypes=(('csv', '*.csv'), ('excel', '*.xlsx'))
        )
        if not file_name:
            showinfo(message='Please select a file to continue')
            if retries > 0:
                file_name = self._get_data_from_file(retries - 1)
            else:
                self.master.quit()
        else:
            self.data = df_from_file(file_name)

    def _get_report_title(self):
        """Creates a simple dialog to capture text input for the desired
        report title.
        """
        # Prompt user for report title
        report_title = askstring(
            title='Report Title',
            prompt='Please enter your preferred title for the report:',
            initialvalue='Exploratory Data Analysis Report')

        self.report_title = report_title if report_title else \
            'Exploratory Data Analysis Report'

    def _get_graph_color(self):
        """Creates a graphical color picking tool to help set the desired
        color for the generated graphs.
        """
        # Returns a tuple e.g ((255.99609375, 69.26953125, 0.0), '#ff4500').
        color = askcolor(
            color='orangered',
            title='Please select a color for the graphs'
        )[-1]
        self.graph_color = color if color is not None else 'orangered'

    def _get_save_as_name(self):
        """Create a file dialog to help select a destination folder and file
        name for the generated report.
        """
        # Propmt user for desired output-file name
        save_name = asksaveasfilename(
            initialfile='eda-report.docx', filetypes=(('.docx', '*.docx'),),
            title='Please select Save As file name'
        )
        self.save_name = save_name if save_name else 'eda-report.docx'
