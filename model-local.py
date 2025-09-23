# # https://claude.ai/share/14526b1a-c61d-46f8-9e0c-cebbbef432c8

# # https://claude.ai/public/artifacts/d5149358-7ff6-40b4-851f-d00a06625b44

# # test_colab_api.py
# # Client code to test your Colab-hosted API from VS Code

# import requests
# import json

# # Your API details
# API_BASE = "https://f07eaf312f7a.ngrok-free.app/v1"
# MODEL_NAME = "microsoft/DialoGPT-medium"

# def test_health():
#     """Test if the API is responding"""
#     try:
#         response = requests.get("https://f07eaf312f7a.ngrok-free.app/health", timeout=10)
#         print(f"Health Check: {response.status_code}")
#         print(f"Response: {response.json()}")
#         return response.status_code == 200
#     except Exception as e:
#         print(f"Health check failed: {e}")
#         return False

# def chat_with_model(message, max_tokens=100, temperature=0.7):
#     """Send a chat message to your API"""
#     try:
#         payload = {
#             "model": MODEL_NAME,
#             "messages": [
#                 {"role": "user", "content": message}
#             ],
#             "max_tokens": max_tokens,
#             "temperature": temperature
#         }
        
#         response = requests.post(f"{API_BASE}/chat/completions", 
#                                json=payload, 
#                                timeout=30)
        
#         print(f"Status: {response.status_code}")
        
#         if response.status_code == 200:
#             result = response.json()
#             return result['choices'][0]['message']['content']
#         else:
#             print(f"Error: {response.text}")
#             return None
            
#     except Exception as e:
#         print(f"Request failed: {e}")
#         return None

# def interactive_chat():
#     """Interactive chat session with your model"""
#     print("=== Chat with your Colab-hosted DialoGPT model ===")
#     print("Type 'quit' to exit\n")
    
#     while True:
#         user_input = input("You: ")
        
#         if user_input.lower() in ['quit', 'exit', 'q']:
#             print("Goodbye!")
#             break
            
#         print("AI is thinking...")
#         response = chat_with_model(user_input)
        
#         if response:
#             print(f"AI: {response}\n")
#         else:
#             print("Sorry, I couldn't process that request.\n")

# def run_tests():
#     """Run various tests on your API"""
#     print("=== Testing Your Colab API ===\n")
    
#     # Test 1: Health check
#     print("1. Health Check:")
#     if not test_health():
#         print("❌ API is not responding. Check if Colab is still running.")
#         return
#     print("✅ API is healthy\n")
    
#     # Test 2: Simple chat
#     print("2. Simple Chat Test:")
#     response = chat_with_model("Hello! How are you today?", max_tokens=50)
#     if response:
#         print(f"✅ Response: {response}\n")
#     else:
#         print("❌ Chat test failed\n")
    
#     # Test 3: Longer conversation
#     print("3. Longer Response Test:")
#     response = chat_with_model("Tell me about artificial intelligence", max_tokens=100)
#     if response:
#         print(f"✅ Response: {response}\n")
#     else:
#         print("❌ Longer response test failed\n")
    
#     # Test 4: Different temperature
#     print("4. Creative Response Test (higher temperature):")
#     response = chat_with_model("Write a short poem about technology", max_tokens=80, temperature=0.9)
#     if response:
#         print(f"✅ Response: {response}\n")
#     else:
#         print("❌ Creative response test failed\n")

# def benchmark_api():
#     """Benchmark your API performance"""
#     print("=== API Performance Benchmark ===\n")
    
#     import time
    
#     test_messages = [
#         "What is machine learning?",
#         "Explain neural networks",
#         "How does deep learning work?",
#         "What is natural language processing?",
#         "Tell me about computer vision"
#     ]
    
#     total_time = 0
#     successful_requests = 0
    
#     for i, message in enumerate(test_messages, 1):
#         print(f"Test {i}: {message[:30]}...")
        
#         start_time = time.time()
#         response = chat_with_model(message, max_tokens=50)
#         end_time = time.time()
        
#         if response:
#             request_time = end_time - start_time
#             total_time += request_time
#             successful_requests += 1
#             print(f"✅ Response time: {request_time:.2f}s")
#         else:
#             print("❌ Failed")
#         print()
    
#     if successful_requests > 0:
#         avg_time = total_time / successful_requests
#         print(f"📊 Average response time: {avg_time:.2f}s")
#         print(f"📊 Success rate: {successful_requests}/{len(test_messages)} ({successful_requests/len(test_messages)*100:.1f}%)")

# if __name__ == "__main__":
#     print("Choose an option:")
#     print("1. Run tests")
#     print("2. Interactive chat")
#     print("3. Benchmark performance")
#     print("4. Single question")
    
#     choice = input("\nEnter choice (1-4): ").strip()
    
#     if choice == "1":
#         run_tests()
#     elif choice == "2":
#         interactive_chat()
#     elif choice == "3":
#         benchmark_api()
#     elif choice == "4":
#         question = input("Ask your question: ")
#         response = chat_with_model(question)
#         if response:
#             print(f"\nAI: {response}")
#         else:
#             print("\nSorry, couldn't get a response.")
#     else:
#         print("Invalid choice. Running tests by default.")
#         run_tests()


import asyncio
from pathlib import Path

from browser_use import Agent
from browser_use import ChatGoogle


async def main():
	# Example task to demonstrate history saving and rerunning
	history_file = Path('agent_history.json')
	task = 'Go to https://browser-use.github.io/stress-tests/challenges/ember-form.html and fill the form with example data.'
	llm = ChatGoogle(model='gemini-2.5-flash', api_key="AIzaSyDsnVoeD0yvURLRo38V6jfcRiSuObTs1_w")

	agent = Agent(task=task, llm=llm, max_actions_per_step=1)
	await agent.run(max_steps=5)
	agent.save_history(history_file)

	rerun_agent = Agent(task='', llm=llm)

	await rerun_agent.load_and_rerun(history_file)


if __name__ == '__main__':
	asyncio.run(main())