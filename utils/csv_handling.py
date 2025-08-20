from langchain_core.prompts import ChatPromptTemplate
from langchain_experimental.tools import PythonAstREPLTool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers.openai_tools import JsonOutputKeyToolsParser


class CsvHandler:
    def __init__(self, df, llm):
        self.df = df
        self.llm = llm
        self.tool = PythonAstREPLTool(locals={"df": self.df})
        self.llm_with_tool = self.__init_llm_with_tool()

    def __init_llm_with_tool(self):
        llm = ChatGoogleGenerativeAI(model=self.llm, temperature=self.temperature)
        llm_with_tools = llm.bind_tools([self.tool], tool_choice=self.tool.name)
        return llm_with_tools

    def get_tool_query(self, user_instruct):
        parser = JsonOutputKeyToolsParser(key_name=self.tool.name, first_tool_only=True)
        system = f"""You have access to a pandas dataframe `df`. \
        Here is the output of `df.head().to_markdown()`:
        ```
        {self.df.head().to_markdown()}
        ```
        Given a user question, write the Python code to answer it. \
        Return ONLY the valid Python code and nothing else. \
        Don't assume you have access to any libraries other than built-in Python ones and pandas."""
        prompt = ChatPromptTemplate.from_messages(
            [("system", system), ("human", "{question}")]
        )
        chain = prompt | self.llm_with_tool | parser
        output = chain.invoke({"question": user_instruct})
        return output.get("query", "")

    def __call__(self, user_instruct):
        tool_query = self.get_tool_query(user_instruct)
        if not tool_query:
            print(f"CSV query tool return empty response: {tool_query}")
        response = self.tool.invoke(tool_query)
        return response
