import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("💬 Chatbot")
st.write(
    "This is a simple chatbot that uses OpenAI's GPT-4 model to generate responses. "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
    "You can also learn how to build this app step by step by [following our tutorial](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps)."
)

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
openai_api_key = st.secrets["apikey"]



# Create an OpenAI client.
client = OpenAI(api_key=openai_api_key)

# Create a session state variable to store the chat messages. This ensures that the
# messages persist across reruns.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display the existing chat messages via `st.chat_message`.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Create a chat input field to allow the user to enter a message. This will display
# automatically at the bottom of the page.


context =  [{'role':'system', 'content':"""
                        You are a lawncare expert. Your job is to create a plan/schedule for lawncare, taking into account the weather, the type of grass, the soil temp, and any previous product applications.  I prefer Yard Mastery products. \
                        1. Retrieve the users history, including product application. If this is the first conversation with the user then ask about any applications done for the season so far and their dates. \
                        2. If the user provides a location, look up what type of grass lives in that location and use that information in your answer. \
                        3. Look up the weather for this week in that location, with a focus on temperature and rainfall in inches. \
                        4. Double check the weather info, particularly the rainfall, by searching many sites. \
                        5. Look up the soil temperature for that location. \
                        6. Determine the appropriate amount of additional water that should be applied given the rainfall predicted. This can be calculated by (The amount of rainfall needed for this time of year for the type of grass) - (Rainfall Estimated) \
                        7. Determine what are some appropriate fertilizers and/or micronutrients that should be applied given the following: \
                        A. The NPK ratio. Avoiding high N during times of the year when there are stressful grass conditions. Suggesting K when there are stressful grass conditions. \
                        B. Weather information such as heat or rain \
                        C. Location \
                        D. Type of grass. \
                        8. Determine what are some appropriate weed control products that should be applied given the following: \
                        A. Time of year \
                        B. Weather information \
                        C. Location \
                        D. Type of grass. \
                        9. Determine how the products should be applied. Suggest which day would be best based on weather conditions. \
                        10. Redo all of step 1-9 for the next 3 weeks, with a focus on creating a lawn care schedule. \
                        11. Check if there are any application overlap issues between products. \
                        12. Revise the information if there are any issues between products. \
                        13. Add links to products. \
                        14. Review the plan created from Week 1 and the following 3 weeks and adjust the entire plan as needed. \

                        Use the following format: \
                        Week: <Week of the Year> \
                        Weather Info: \
                        <Temperature> \
                        <Rainfall> \
                        <Soil Temperature> \
                        Applications for this week: \
                        <Watering Recommendation> \
                        <Mowing> \
                        <Weed Control> \
                        <Products> <Link> \
                        <Application Instructions> \
                        <Fertilization> \
                        <Products> <Link> \
                        <Application Instructions> """},    
                        {'role':'user', 'content':'I live in Oceanside,NY'}]


if prompt := st.chat_input("What is up?"):

    # Store and display the current prompt.
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    context.append({'role':'user', 'content':prompt})

    # Generate a response using the OpenAI API.
    messages =  context.copy()

    stream = client.chat.completions.create(
        model="gpt-4",
         messages=[
            {"role": m["role"], "content": m["content"]}
            for m in messages
        ],   
                        
        stream=True,
    )

    # Stream the response to the chat using `st.write_stream`, then store it in 
    # session state.
    with st.chat_message("assistant"):
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
