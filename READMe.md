# Dynamic Dashboard
Built API which update HTML content of dashboard, according to  user instruction, CSV, and HTML for dashboard.

## API Block diagram
![alt text](data/block.png)


## To Run
- install requirements using following command
```
pip install -r requirements.txt
```
- Create `.env` in parent directory and add gemini API key, you can see `.example.env` file for reference.
```
GOOGLE_API_KEY = ""
```
- run api using following command
```
uvicorn main:app --reload
```
## Input API
![alt text](data/input.png)

## Output API
![alt text](data/output.png)
