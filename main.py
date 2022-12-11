from services.assemble_data import get_speeches
import markovify
import fastapi
import uvicorn
import asyncio


GREAT_NUM = 3
speeches = asyncio.run(get_speeches())
model_combination = None


def run_model_with_max_input():
    global model_combination
    models = list(
        markovify.Text(speech, state_size=GREAT_NUM)
        for speech in speeches.values()
    )
    model_combination = markovify.combine(models).compile(inplace=True)


run_model_with_max_input()
app = fastapi.FastAPI()


@app.get("/random_sentence")
async def generate_random_sentence(
        init_state: str = None,
        min_words: int = None,
        max_words: int = None
):
    try:
        if init_state:
            if len(init_state.split(" ")) + init_state.count(",") > GREAT_NUM:
                return f"Max input words is {GREAT_NUM}."
            return model_combination.make_sentence_with_start(
                init_state,
                strict=False,
                max_words=max_words,
                min_words=min_words,
                tries=10**5,
            )
        return model_combination.make_sentence(
            max_words=max_words,
            min_words=min_words,
            tries=10**5,
        )
    except markovify.text.ParamError as error:
        print(error)
        return "Unable to create sentence with " + init_state


@app.patch("/change_max_input")
async def change_max_input(max_input: int):
    global GREAT_NUM
    GREAT_NUM = max_input
    run_model_with_max_input()
    return "Success"


if __name__ == "__main__":
    uvicorn.run(app)
