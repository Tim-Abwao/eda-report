from pandas import DataFrame

from eda_report.analysis import _AnalysisResult
from eda_report.content import _ReportContent

data = DataFrame(
    {"A": range(48), "B": list(range(16)) * 3, "C": list("abcd") * 12}
)


class TestReportContent:
    content = _ReportContent(data, title="Some Title")

    def test_general_attributes(self):
        assert isinstance(self.content, _AnalysisResult)
        assert self.content.GRAPH_COLOR == "cyan"
        assert self.content.TITLE == "Some Title"
        assert self.content.GROUPBY_DATA is None

    def test_intro(self):
        assert self.content.intro_text == (
            "The dataset consists of 48 rows (observations) and 3 columns "
            "(features), 2 of which are numeric."
        )

    def test_variable_descriptions(self):
        assert self.content.variable_descriptions == {
            "A": (
                "A is a numeric variable with 48 unique values."
                " None of its values are missing."
            ),
            "B": (
                "B is a numeric variable with 16 unique values."
                " None of its values are missing."
            ),
            "C": (
                "C is a categorical variable with 4 unique values."
                " None of its values are missing."
            ),
        }

    def test_bivariate_summaries(self):
        assert self.content.bivariate_summaries == {
            ("A", "B"): "A and B have weak positive correlation (0.33)."
        }


def test_limiting_bivariate_summaries():
    content = _ReportContent([range(12), [1, 2, 3, 4] * 3])
    # content has 66 var_pairs (66 possible pairs from 12 numeric cols)
    # but the limit for summaries is 20
    assert len(content.bivariate_summaries) == 20
