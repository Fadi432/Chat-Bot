import streamlit as st
import os
import asyncio
import threading
from dotenv import load_dotenv
import time

# Load environment variables (for local development)
load_dotenv()

# Get secrets from Streamlit secrets or environment variables (fallback for local dev)
try:
    PASSWORD = st.secrets["APP_PASSWORD"]
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except:
    # Fallback to environment variables for local development
    PASSWORD = os.getenv("APP_PASSWORD")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Try to import your agents module, but use mock if it fails
try:
    from agents import Agent, Runner
    AGENTS_AVAILABLE = True
    st.sidebar.success("✅ Agents module imported successfully")
except ImportError as e:
    st.sidebar.warning(f"⚠️ Agents module not available: {e}")
    st.sidebar.info("🔄 Using mock agent instead")
    AGENTS_AVAILABLE = False

# Simple mock agent for testing
class MockAgent:
    def __init__(self, name, instructions, model):
        self.name = name
        self.instructions = instructions
        self.model = model
    
    def get_response(self, message):
        """Mock response - replace with your actual agent logic"""
        roast_responses = [
            f"Yaar {message}? Seriously? 😂 Anyway, here's your answer:",
            f"Bhai ye kya sawal hai {message}? 🤔 But let me help you:",
            f"Areh yaar {message} puch rahe ho? Koi baat nahi, answer ye hai:",
            f"Toba toba {message}! 😄 Chalein answer deta hun:",
            f"Bhai sahab {message} ka jawab? Thik hai, sun lo:"
        ]
        
        import random
        roast = random.choice(roast_responses)
        
        if "hello" in message.lower() or "hi" in message.lower():
            return f"{roast} Hello! Main tumhara AI assistant hun. Kya help chahiye?"
        elif "how are you" in message.lower():
            return f"{roast} Main bilkul theek hun! Bas tumhare sawalon ka intezaar kar rahi thi."
        elif "what can you do" in message.lower():
            return f"{roast} Main bohot kuch kar sakti hun - questions answer kar sakti hun, help kar sakti hun, aur tumhe roast bhi kar sakti hun! 😄"
        else:
            return f"{roast} That's an interesting question! I'd be happy to help you with that."

# Initialize the agent
@st.cache_resource
def initialize_agent():
    if AGENTS_AVAILABLE and OPENAI_API_KEY:
        try:
            agent = Agent(
                name="Assistant",
                instructions="You are a helpful assistant and when someone asks you a question you roast them in roman urdu and make fun of them and then give answer",
                model="gpt-4o-mini",
            )
            return agent, True
        except Exception as e:
            st.sidebar.error(f"⚠️ Failed to initialize real agent: {e}")
            return MockAgent("Assistant", "Mock instructions", "gpt-4o-mini"), False
    else:
        return MockAgent("Assistant", "Mock instructions", "gpt-4o-mini"), False

agent, is_real_agent = initialize_agent()

def get_response(message):
    """Get response from agent"""
    try:
        if is_real_agent:
            # Use real agent with threading approach
            result_container = {}
            
            def run_agent_in_thread():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = Runner.run_sync(agent, message.strip())
                    result_container['result'] = result.final_output if hasattr(result, 'final_output') else str(result)
                except Exception as e:
                    result_container['error'] = str(e)
                finally:
                    if 'loop' in locals():
                        loop.close()
            
            thread = threading.Thread(target=run_agent_in_thread)
            thread.start()
            thread.join(timeout=30)
            
            if 'result' in result_container:
                return result_container['result']
            elif 'error' in result_container:
                return f"Agent Error: {result_container['error']}"
            else:
                return "Timeout: Agent took too long to respond"
        else:
            return agent.get_response(message.strip())
    except Exception as e:
        return f"Error: {str(e)}"

# Custom CSS for beautiful styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Poppins', sans-serif;
    }
    
    .main-header {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 30px 25px;
        margin-bottom: 25px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    
    .main-title {
        background: linear-gradient(45deg, #ff6b6b, #feca57, #48dbfb, #ff9ff3);
        background-size: 300% 300%;
        animation: gradientShift 3s ease infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0 0 15px 0;
    }
    
    .subtitle {
        color: rgba(255, 255, 255, 0.8);
        font-size: 1.1rem;
        margin: 0;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .chat-message {
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }
    
    .user-message {
        background: rgba(255, 255, 255, 0.15);
        border-left: 4px solid #48dbfb;
        color: white;
    }
    
    .bot-message {
        background: rgba(255, 255, 255, 0.1);
        border-left: 4px solid #ff6b6b;
        color: white;
    }
    
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.15);
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-radius: 15px;
        color: white;
        font-family: 'Poppins', sans-serif;
    }
    
    .stButton > button {
        background: linear-gradient(45deg, #ff6b6b, #feca57);
        border: none;
        border-radius: 15px;
        color: white;
        font-weight: 600;
        font-family: 'Poppins', sans-serif;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(255, 107, 107, 0.4);
    }
    
    .sidebar .sidebar-content {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(15px);
    }
</style>
""", unsafe_allow_html=True)

# Password protection (optional)
def check_password():
    # Skip password check if no password is set
    if not PASSWORD or PASSWORD == "your_secure_password_here":
        return True
        
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        password = st.text_input("Enter Password", type="password")
        if st.button("Login"):
            if password == PASSWORD:
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("Incorrect password")
        return False
    return True

# Main app
def main():
    # Header
    st.markdown("""
    <div class='main-header'>
        <h1 class='main-title'>🤖 AI Chat Assistant</h1>
        <p class='subtitle'>Made By Fawad Amin</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ✨ Features")
        st.markdown("🧠 Intelligent responses")
        st.markdown("💬 Natural conversation")
        st.markdown("🎯 Context awareness")
        st.markdown("🚀 Fast responses")
        st.markdown("🎨 Beautiful interface")
        st.markdown("📱 Mobile friendly")
        
        st.markdown("### 🎮 Try asking:")
        if st.button("What can you do?"):
            st.session_state.messages.append({"role": "user", "content": "What can you do?"})
        if st.button("Tell me a fun fact"):
            st.session_state.messages.append({"role": "user", "content": "Tell me a fun fact"})
        if st.button("Help me brainstorm"):
            st.session_state.messages.append({"role": "user", "content": "Help me brainstorm ideas"})
        
        st.markdown("---")
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.rerun()
    
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class='chat-message user-message'>
                <strong>👤 You:</strong><br>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='chat-message bot-message'>
                <strong>🤖 Assistant:</strong><br>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)
    
    # Chat input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Get bot response
        with st.spinner("Thinking..."):
            response = get_response(user_input)
        
        # Add bot response
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Rerun to update the display
        st.rerun()

# Run the app
if __name__ == "__main__":
    if check_password():
        main()