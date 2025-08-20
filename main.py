from fastapi import FastAPI, UploadFile, File, Form
import pandas as pd
from typing import Annotated
from utils.agent import execute

app = FastAPI()


@app.post("/beautify_dashboad")
async def beautify_dashboad(
    csv_data: Annotated[UploadFile, File()],
    user_instruct: Annotated[str, Form()],
    dashboard_html: Annotated[str, Form()],
):
    print("user instruction: ", user_instruct)
    print("dashboard_html: ", dashboard_html)
    print(f"csv_data type: {type(csv_data)}")
    csv_df = pd.read_csv(csv_data.file)
    print(f"csv df shape: {csv_df}")
    output = await execute(
        user_instruct=user_instruct,
        input_html=dashboard_html,
        csv_df=csv_df,
    )
    return output


@app.get("/")
async def hello_world():
    return "Welcome to dynamic dashboard creation project!"
