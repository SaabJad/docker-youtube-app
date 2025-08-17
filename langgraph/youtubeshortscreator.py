import os
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

# Set your Google API key
os.environ["GOOGLE_API_KEY"] = "AIzaSyCdTrLUnRwUT4EA3ahHpBpKV6mhB0SWOfw"

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

# Initialize model
model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash" ,
    temperature=0.7
)

# Single node that creates the script
def create_script_node(state: AgentState):
    # Get the user's topic from the last message
    user_message = state["messages"][-1].content
    topic = user_message.replace("Create a YouTube Short script for: ", "")
    
    # giving the prompt div into 3 main categories (hook main content and the CTA)
    prompt = f"""Create a simple 60-second YouTube Shorts script for the topic: {topic}

Format it like this:
HOOK (0-3 seconds): [Attention-grabbing opening]
MAIN CONTENT (4-50 seconds): [Key points about the topic]  
CALL TO ACTION (51-60 seconds): [Ask for likes/follows]

Keep it simple and engaging!"""
    
    # Get response from model make sure it is *HUMAN FORM* it wraps the data to form it in humanized words
    response = model.invoke([HumanMessage(content=prompt)])
    
    return {"messages": [response]}

# buiding the graph, 1 node or layer used calling my creat_script_node function above to retreive the data from the user, 
#then it will follow the prompt provided above use model gemini 1.5 Flash generate the content by the invoke method to which basically calls my api
# transform to human form and the return the message
#layout start--->create_script_station--->end
workflow = StateGraph(AgentState)
workflow.add_node("create_script", create_script_node)
workflow.set_entry_point("create_script")
workflow.add_edge("create_script", END)

#compiling said graph
graph = workflow.compile()

def create_short(topic):
    print(f"\nCreating YouTube Short script for: '{topic}'")
    
    # running  the graph
    inputs = {"messages": [HumanMessage(content=f"Create a YouTube Short script for: {topic}")]}
    result = graph.invoke(inputs)
    
    # Get the final script
    final_message = result["messages"][-1]
    print(final_message.content)

def main():
    print("Please enter your topic to generate script")
    
    while True:
        try:
            topic = input(" Enter your topic ('exit if you want to stop'): ").strip()
            
            if topic.lower() in ['exit']:
                print("Stopped")
                break
            
            if not topic:
                print(" Please enter a topic")
                continue
            
            create_short(topic)
            
        except KeyboardInterrupt:
            print("\n stopped")
            break
        except Exception as e:
            print(f" Error: {e}")

if __name__ == "__main__":
    main()

#please find below a list of references
# https://python.langchain.com/docs/integrations/chat/google_generative_ai/
# https://langchain-ai.github.io/langgraph/
# https://aistudio.google.com/apikey
# https://langchain-ai.github.io/langgraph/concepts/low_level/