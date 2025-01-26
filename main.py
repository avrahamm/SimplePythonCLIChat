import os, json
from dotenv import load_dotenv
import openai

load_dotenv()

api_key=os.environ.get("OPENAI_API_KEY", None)
# print(api_key) # will print 'openai_token'

base_url = os.environ.get("BASE_URL", "https://litellm.aks-hs-prod.int.hyperskill.org")
target_model = os.environ.get("MODEL", "gpt-4o-mini")

USER_ROLE = "user"
SYSTEM_ROLE = "system"

# This flag variable is changed by end_conversation function call
# invoked by a model in tool_calls
is_terminated = False

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
    global is_terminated
    is_terminated = True

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


def perform_function_calls( assistant_message):
    if not assistant_message.tool_calls:
        return
    # First create a dictionary to map the function name string to actual function
    function_list = {
        "end_conversation":end_conversation
    }

    # Extract the tool_calls contenttool_call = {ChatCompletionMessageToolCall} ChatCompletionMessageToolCall(id='call_YRmk34X7B0q5orzR1c3FwxLQ', function=Function(arguments='{}', name='end_conversation'), type='function')
    for tool_call in assistant_message.tool_calls:
        # Extract the function name and the arguments
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)

        # Get the actual function
        function_to_call = function_list[function_name]

        # Call the function with the parameter(s) and store the function response
        function_response = function_to_call()
        debug = 1


if __name__ == '__main__':
    messages_list=[]
    caller_role = None

    while not is_terminated:
        user_prompt = input("Enter a message: ")
        caller_role = USER_ROLE
        tools = None
        tool_choice = "auto"

        if user_prompt == TERMINATION_MESSAGE:
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

        gpt_response_message = chat_completion.choices[0].message
        perform_function_calls(assistant_message=gpt_response_message)

        if is_terminated:
            # print(f"Assistant message: {gpt_response_message}")
            print(f"{gpt_response_message.tool_calls[0].id}")

        print(f"You: {user_prompt}")
        print(f"Assistant: {gpt_response}")
        print(f"Cost: ${total_usage_costs:.8f}")