from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    print("Root")
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    print(f"Hello {name}")
    return {"message": f"Hello {name}"}
