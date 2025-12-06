from agent.graph.state.state import State
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


class Generator_Agent:
    
    def __init__(
        self, 
        tools, 
        system_prompt, 
        model_name,
        temperature
    ):
        self.tools = tools or []
        self.system_prompt = system_prompt
        self.model_name = model_name
        self.temperature = temperature
        self.chain = self._build_chain()
    
    def _build_chain(self):
        model = ChatGroq(model=self.model_name, temperature= self.temperature)
        
        if self.tools:
            model = model.bind_tools(tools=self.tools)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="messages")
        ])
        
        return prompt | model 
    
    def __call__(self, state: State):
        response = self.chain.invoke({"messages": state["messages"]})
        return {"messages": [response]}
    