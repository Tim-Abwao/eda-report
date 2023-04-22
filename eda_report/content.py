from typing import Any, Dict, Iterable, Union


from eda_report.analysis import _AnalysisResult


class _ReportContent(_AnalysisResult):
    """Prepares textual summaries of analysis results.

    Args:
        data (Iterable): The data to analyze.
        title (str, optional): The title to assign the report. Defaults to
            "Exploratory Data Analysis Report".
        graph_color (str, optional): The color to apply to the graphs.
            Defaults to "cyan".
        groupby_data (Union[str, int], optional): The column to
            use to group values. Defaults to None.
    """

    def __init__(
        self,
        data: Iterable,
        *,
        title: str = "Exploratory Data Analysis Report",
        graph_color: str = "cyan",
        groupby_data: Union[str, int] = None,
    ) -> None:
        super().__init__(
            data, graph_color=graph_color, groupby_data=groupby_data
        )
        self.TITLE = title
        self.intro_text = self._get_introductory_summary()
        self.variable_descriptions = self._describe_variables()

    def _get_introductory_summary(self) -> str:
        """Get an overview of the number of rows and the nature of columns.

        Returns:
            str: Introduction.
        """
        num_rows, num_cols = self.dataset.data.shape

        if num_rows == 1:
            rows = "1 row (observation)"
        else:
            rows = f"{num_rows:,} rows (observations)"

        if num_cols == 1:
            cols = "1 column (feature)"
        else:
            cols = f"{num_cols:,} columns (features)"

        # Get numeric column info
        if self.dataset._numeric_stats is None:
            numeric_descr = ""
        else:
            num_numeric = self.dataset._numeric_stats.shape[0]
            if num_numeric == 1:
                numeric_descr = ", 1 of which is numeric"
            else:
                numeric_descr = f", {num_numeric} of which are numeric"

        return f"The dataset consists of {rows} and {cols}{numeric_descr}."

    def _describe_variables(self) -> Dict[str, Any]:
        """Get summary statistics for a variable.

        Args:
            univariate_stats (Variable): The data to analyze.

        Returns:
            Dict[str, Any]: Summary statistics.
        """
        descriptions = {}
        for name, variable in self.variables.items():
            if variable.num_unique == 1:
                unique_vals = "1 unique value"
            else:
                unique_vals = f"{variable.num_unique:,} unique values"

            descriptions[name] = (
                f"{variable.name.capitalize()} is a {variable.var_type} "
                f"variable with {unique_vals}. {variable.missing} of its "
                "values are missing."
            )
        return descriptions
