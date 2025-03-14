class ResearchReport:
    def __init__(self, title, outline, citations):
        self.title = title
        self.outline = outline
        self.citations = citations
        self.content = ""

    def generate_title(self):
        return self.title

    def generate_outline(self):
        return self.outline

    def add_citation(self, citation):
        self.citations.append(citation)

    def compile_content(self, facts):
        self.content = "\n".join(facts)

    def get_report(self):
        report = f"Title: {self.generate_title()}\n\n"
        report += "Outline:\n" + "\n".join(self.generate_outline()) + "\n\n"
        report += "Content:\n" + self.content + "\n\n"
        report += "Citations:\n" + "\n".join(self.citations)
        return report