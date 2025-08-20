from pydantic import BaseModel


HTML_MODIFIER_PROMPT = """You are expert HTML developer. Given user instruction, \
your task is update given HTML according to user instruction.
user instruction: ```{user_instruct}```
HTML: ```{html}```"""


class HtmlOut(BaseModel):
    html: str


class HTMLModifier:
    def __init__(self, llm):
        self.llm = llm

    def __call__(self, html, user_instruct):
        prompt = HTML_MODIFIER_PROMPT.format(
            user_instruct=user_instruct,
            html=html,
        )
        out = self.llm.with_structured_output(HtmlOut).invoke(prompt)
        if not out or not out.model_dump().get("html", None):
            print(
                f"""Failed to Modify the html as per user instruction, so returning original HTML
user instruction: {user_instruct}
HTML out by LLM: {out}
HTML modifier prompt: {prompt}"""
            )
            return html
        html_out = out.model_dump().get("html", None)
        return html_out
