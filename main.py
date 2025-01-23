import os
from dotenv import load_dotenv
import openai

load_dotenv()

api_key=os.environ.get("OPENAI_API_KEY", None)
# print(api_key) # will print 'openai_token'

base_url = os.environ.get("BASE_URL", "https://litellm.aks-hs-prod.int.hyperskill.org")
target_model = os.environ.get("MODEL", "gpt-4o-mini")
role = os.environ.get("ROLE", "user")

client = openai.OpenAI(
    api_key=api_key,
    base_url=base_url,
)


MODEL_4_MINI = "gpt-4o-mini"

# prices by
# @link:https://llmpricecheck.com/calculator/
MODELS = {
    MODEL_4_MINI: {
        "input_cost": 0.15 / 1000000,
        "output_cost": 0.6 / 1000000
    },
}


def calculate_tokens_cost(model, chat_completion):
    if model not in MODELS:
        raise ValueError(f"Model {model} is not supported.")

    model_costs = MODELS[model]
    input_tokens_cost = chat_completion.usage.prompt_tokens * model_costs["input_cost"]
    output_tokens_cost = (
            chat_completion.usage.completion_tokens * model_costs["output_cost"]
    )
    return input_tokens_cost + output_tokens_cost


def get_chat_completion(model, role, prompt):
    return client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": role,
                "content": prompt
            }
        ],
        temperature=0.5,
        # seed=12345
    )


if __name__ == '__main__':
    user_prompt = input("Enter a message: ")

    chat_completion = get_chat_completion(
        model=target_model, role=role, prompt=user_prompt
    )

    gpt_response = chat_completion.choices[0].message.content
    total_usage_costs = calculate_tokens_cost(MODEL_4_MINI, chat_completion)
    print(f"You: {user_prompt}")
    print(f"Assistant: {gpt_response}")
    print(f"Cost: ${total_usage_costs:.8f}")