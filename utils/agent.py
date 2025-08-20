from utils.csv_handling import CsvHandler
from utils.html_handling import HTMLModifier
from langgraph.graph import END
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Literal, TypedDict
from pydantic import BaseModel
from langgraph.graph import StateGraph, START
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


class State(TypedDict):
    user_instruct: str
    input_html: str
    csv_data: pd.DataFrame


class Router(BaseModel):
    mode: Literal["csv", "html", "both", "none"]


class HtmlOut(TypedDict):
    output_html: str


ROUTER_PROMPT = """Given the user instruction, \
you have to select only one from given four modes depending upon the given instruction. \
The four modes are : "csv", "html", "both", "none".
Following are modes detail.
- "csv" for route instruction for CSV handling only.
- "html" for html modification, related task.
- "both" for both html modification and csv handling task.
- "none" not related to any task.
user instruction: {user_instruct}"""

llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.0)


def handle_csv_query(state: State, df):
    csv_handler = CsvHandler(df, llm)
    out = csv_handler(state["user_instruct"])
    return out


def beautify_html(state: State) -> HtmlOut:
    html_modifier = HTMLModifier(llm)
    updated_html = html_modifier(
        html=state["input_html"],
        user_instruct=state["user_instruct"],
    )
    print(f"updated html: {updated_html}")
    return {"output_html": updated_html}


def route_query(state: State):
    user_instruct = state["user_instruct"]
    prompt = ROUTER_PROMPT.format(user_instruct=user_instruct)
    print(f"router prompt: {prompt}")
    route = llm.with_structured_output(Router).invoke(prompt)
    print("route : ", type(route), route)

    if not route or not route.model_dump().get("mode", None):
        print(f"Ending graph due to no route matching...")
        return END
    route_mode = route.model_dump().get("mode", None)
    print(f"router out: {route_mode}")

    if route_mode == "html":
        return "beautify_html"

    elif route_mode == "csv":
        return "handle_csv_query"

    elif route_mode == "both":
        # TODO: update for both, for only just update for
        return "beautify_html"

    else:
        return END


def update_html_for_csv_out(state: State) -> HtmlOut:
    # TODO: update the html for after getting CSV results
    return {"output_html": state["input_html"]}


def build_graph():
    # Define a new graph
    workflow = StateGraph(State, output_schema=HtmlOut)
    workflow.add_node("handle_csv_query", handle_csv_query)
    workflow.add_node("beautify_html", beautify_html)
    workflow.add_node("update_html", update_html_for_csv_out)

    # Set the entrypoint as conversation
    workflow.add_conditional_edges(
        START, route_query, ["handle_csv_query", "beautify_html", END]
    )
    workflow.add_edge("handle_csv_query", "update_html")
    workflow.add_edge(["update_html", "beautify_html"], END)
    return workflow


class State(TypedDict):
    user_instruct: str
    input_html: str
    csv_data: pd.DataFrame


async def execute(user_instruct, csv_df, input_html):
    # Compile
    workflow = build_graph()
    graph = workflow.compile()
    input_state = {
        "user_instruct": user_instruct,
        "input_html": input_html,
        "csv_data": csv_df,
    }
    print(f"input state to agent: {input_state}")
    output = graph.invoke(input_state)

    # graph ended before
    if not output:
        output = input_html

    return output
