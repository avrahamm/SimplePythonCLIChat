import os
from dotenv import load_dotenv
import openai
from openai.types.chat.chat_completion_tool_choice_option_param import ChatCompletionToolChoiceOptionParam

load_dotenv()

api_key=os.environ.get("OPENAI_API_KEY", None)
# print(api_key) # will print 'openai_token'

base_url = os.environ.get("BASE_URL", "https://litellm.aks-hs-prod.int.hyperskill.org")
target_model = os.environ.get("MODEL", "gpt-4o-mini")

USER_ROLE = "user"
SYSTEM_ROLE = "system"

client = openai.OpenAI(
    api_key=api_key,
    base_url=base_url,
)


MODEL_4_MINI = "gpt-4o-mini"
TERMINATION_MESSAGE = "End conversation"

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


def get_chat_completion(model,
                        messages=[],
                        tools=None,
                        tool_choice= "auto"
                        ):
    debug = True
    if tools:
        return client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice= "auto",
            temperature=0.5,
            # seed=12345
        )

    return client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.5,
        # seed=12345
    )


def end_conversation():
    pass

functions_list = [
    {
        "type": "function",
        "function": {
            "name": "end_conversation",
            "description": "end_conversation",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    }
]

if __name__ == '__main__':
    messages_list=[]
    is_terminated = False
    caller_role = None

    while not is_terminated:
        user_prompt = input("Enter a message: ")
        caller_role = USER_ROLE
        tools = None
        tool_choice = "auto"

        if user_prompt == TERMINATION_MESSAGE:
            is_terminated = True
            caller_role = SYSTEM_ROLE
            tools = functions_list

        messages_list.append({
                "role": caller_role,
                "content": user_prompt,
            },
        )
        chat_completion = get_chat_completion(
            model=target_model,
            messages=messages_list,
            tools=tools,
            tool_choice=tool_choice
        )

        gpt_response = chat_completion.choices[0].message.content
        total_usage_costs = calculate_tokens_cost(MODEL_4_MINI, chat_completion)

        if is_terminated:
            gpt_response_message = chat_completion.choices[0].message
            # print(f"Assistant message: {gpt_response_message}")
            print(f"{gpt_response_message.tool_calls[0].id}")

        print(f"You: {user_prompt}")
        print(f"Assistant: {gpt_response}")
        print(f"Cost: ${total_usage_costs:.8f}")