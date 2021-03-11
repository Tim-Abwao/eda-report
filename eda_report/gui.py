from eda_report.read_file import df_from_file
from eda_report import get_word_report
from tkinter import Tk, Button, Frame, Canvas, PhotoImage
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.simpledialog import askstring
from tkinter.colorchooser import askcolor
from tkinter.messagebox import showinfo


description = """
A simple application to help speed up exploratory data analysis and reporting.

Select a file to analyse, and it will be automatically summarised. The result\
 is a report in .docx format, complete with summary statistics and graphs.

"""


def run_in_gui():
    """Starts a graphical user interface to the application.
    """
    root = Tk()
    EDA_Gui(master=root)
    root.mainloop()


class EDA_Gui(Frame):
    """[summary]

    :param Frame: [description]
    :type Frame: [type]
    """

    def __init__(self, master=None, **kw):
        super().__init__(master)
        self.master = master
        self.master.title('eda_report')
        self.configure(height=400, width=600)
        self.create_widgets()
        self.pack()

    def create_widgets(self):
        """Creates the widgets for the graphical user interface: A canvas with
        introductory text, a button to select a file, and a background image.
        """
        # Create the canvas
        self.canvas = Canvas(self, width=600, height=400)

        # Set background image
        self.bg_image = PhotoImage(file='eda_report/images/background.png')

        self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")

        # Add introductory text
        self.canvas.create_text(180, 80, text='eda_report', width=500,
                                font=("Courier", 35, 'bold'), fill="black")
        self.canvas.create_text(300, 170, text=description, width=500,
                                font=("Times", 12, 'italic'), fill="black")

        # Add a button
        self.button = Button(
            self, text='Select a file', default='active', bg='teal',
            fg='white', width=30, command=self.create_report, relief='flat',
        )
        self.canvas.create_window(170, 270, anchor='nw', window=self.button)

        self.canvas.pack()

    def create_report(self):
        """Collect input from the graphical user interface, and use the
        :func:`eda_report.get_word_report` function to generate a report.
        """
        self.get_data_from_file()
        self.get_report_title()
        self.get_graph_color()
        self.get_save_as_name()

        # Generate the report using the provided arguments
        get_word_report(self.data, title=self.report_title,
                        graph_color=self.graph_color,
                        output_filename=self.save_name)
        # Pop up message to declare that the report is finished
        showinfo(message=f'Done! Report saved as {self.save_name!r}.')

    def get_data_from_file(self):
        """Creates a file dialog to help navigate to and select a file to
        analyse.
        """
        file_name = askopenfilename(
            title='Select a file to analyse',
            filetypes=(('csv', '*.csv'), ('excel', '*.xlsx'))
        )
        if not file_name:
            showinfo(message='Please select a file to continue')
            file_name = self.get_data_from_file()
        else:
            self.data = df_from_file(file_name)

    def get_report_title(self):
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

    def get_graph_color(self):
        """Creates a graphical color picking tool to help set the desired
        color for the generated graphs.
        """
        # Returns a tuple e.g ((255.99609375, 69.26953125, 0.0), '#ff4500').
        color = askcolor(
            color='orangered',
            title='Please select a color for the graphs'
        )[-1]
        self.graph_color = color if color is not None else 'orangered'

    def get_save_as_name(self):
        """Create a file dialog to help select a destination folder and file
        name for the generated report.
        """
        # Propmt user for desired output-file name
        save_name = asksaveasfilename(
            initialfile='eda-report.docx', filetypes=(('.docx', '*.docx'),),
            title='Please select Save As file name'
        )
        self.save_name = save_name if save_name else 'eda-report.docx'
