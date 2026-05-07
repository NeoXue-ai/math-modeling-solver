import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = SKILL_ROOT / "assets" / "cumcm_template.tex"
PAPER_STRUCTURE = SKILL_ROOT / "references" / "paper_structure.md"


class PaperAssetsTests(unittest.TestCase):
    def test_template_is_cumcm_like_without_external_class_dependency(self):
        text = TEMPLATE.read_text(encoding="utf-8")

        self.assertIn(r"\documentclass[UTF8,a4paper,12pt]{ctexart}", text)
        self.assertNotIn("cumcmthesis", text)
        for required in [
            r"\usepackage{appendix}",
            r"\newcommand{\contestproblem}",
            r"\newcommand{\registrationnumber}",
            r"\newcommand{\schoolname}",
            r"\newcommand{\teammembera}",
            r"\newcommand{\makecoverinfo}",
            r"\keywords",
            r"\section{问题重述}",
            r"\section{问题分析}",
            r"\section{模型假设}",
            r"\section{符号说明}",
            r"\section{模型的建立与求解}",
            r"\subsection{问题一}",
            r"\subsubsection{模型建立}",
            r"\subsubsection{模型求解}",
            r"\subsubsection{求解结果}",
            r"\section{模型的检验与敏感性分析}",
            r"\section{模型的评价与改进}",
            r"\begin{thebibliography}",
            r"\begin{appendices}",
            r"\section{文件列表}",
            r"\section{代码}",
        ]:
            self.assertIn(required, text)

    def test_paper_structure_reference_requires_competition_style_outputs(self):
        text = PAPER_STRUCTURE.read_text(encoding="utf-8")

        for required in [
            "逐问题摘要",
            "模型建立",
            "模型求解",
            "求解结果",
            "符号说明表",
            "文件列表",
            "代码附录",
            "result_registry.json",
        ]:
            self.assertIn(required, text)


if __name__ == "__main__":
    unittest.main()
