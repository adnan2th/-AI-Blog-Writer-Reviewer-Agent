
import os
import streamlit as st
import autogen
from dotenv import load_dotenv

load_dotenv()

# -------------------------
# Streamlit UI
# -------------------------

st.set_page_config(
    page_title="AI Blog Writer",
    page_icon="✍️",
    layout="wide"
)

st.title("✍️ AI Blog Writer & Reviewer")
st.write("Multi-Agent Blog Generation using Groq + AutoGen")

# -------------------------
# Groq Configuration
# -------------------------

api_key = os.environ.get("GROQ_API")

if not api_key:
    st.error("Groq API key missing in .env")
    st.stop()

llm_config = {
    "config_list": [
        {
            "model": "openai/gpt-oss-20b",
            "api_key": GROQ_API,
            "base_url": "https://api.groq.com/openai/v1",
        }
    ]
}

# -------------------------
# Create Agents
# -------------------------

writer = autogen.AssistantAgent(
    name="Writer",
    system_message="""
    You are a professional writer.
    Write engaging and concise blog posts with titles.
    Improve your writing based on reviewer feedback.
    """,
    llm_config=llm_config,
)

critic = autogen.AssistantAgent(
    name="Critic",
    system_message="""
    You are a professional writing critic.
    Review grammar, clarity, structure and engagement.
    Give constructive feedback.
    """,
    llm_config=llm_config,
)

SEO_reviewer = autogen.AssistantAgent(
    name="SEO_Reviewer",
    system_message="""
    You are an SEO expert.
    Review keywords, headings and search optimization.
    Give maximum 3 concise suggestions.
    """,
    llm_config=llm_config,
)

legal_reviewer = autogen.AssistantAgent(
    name="Legal_Reviewer",
    system_message="""
    You are a legal reviewer.
    Identify misleading claims, copyright concerns
    and possible legal risks.
    Give maximum 3 suggestions.
    """,
    llm_config=llm_config,
)

ethics_reviewer = autogen.AssistantAgent(
    name="Ethics_Reviewer",
    system_message="""
    You are an ethics reviewer.
    Review fairness, accuracy, bias and ethical concerns.
    Give maximum 3 suggestions.
    """,
    llm_config=llm_config,
)

meta_reviewer = autogen.AssistantAgent(
    name="Meta_Reviewer",
    system_message="""
    You are the final editor.
    Combine the feedback from all reviewers.
    Improve the original blog post.
    Return only the final polished blog post.
    Follow the requested word limit.
    """,
    llm_config=llm_config,
)

# -------------------------
# User Input
# -------------------------

topic = st.text_input(
    "Blog Topic",
    value="DeepLearning.AI"
)

word_limit = st.number_input(
    "Maximum Words",
    min_value=50,
    max_value=1000,
    value=100
)

# -------------------------
# Generate Blog
# -------------------------

if st.button("Generate Blog", type="primary"):

    task = f"""
    Write an engaging blog post about {topic}.
    Maximum word limit: {word_limit} words.
    Include an attractive title.
    """

    try:

        # Writer
        with st.spinner("Writer is creating the blog..."):

            draft = writer.generate_reply(
                messages=[
                    {"role": "user", "content": task}
                ]
            )

        st.subheader("📝 Initial Blog")
        st.write(draft)

        # Reviewers
        reviewers = {
            "Critic": critic,
            "SEO Reviewer": SEO_reviewer,
            "Legal Reviewer": legal_reviewer,
            "Ethics Reviewer": ethics_reviewer
        }

        feedback = {}

        st.subheader("🔍 Reviewers Feedback")

        for name, agent in reviewers.items():

            with st.spinner(f"{name} is reviewing..."):

                review = agent.generate_reply(
                    messages=[
                        {
                            "role": "user",
                            "content": f"""
                            Review this blog post:

                            {draft}

                            Give constructive feedback.
                            """
                        }
                    ]
                )

                feedback[name] = review

            with st.expander(f"📌 {name}", expanded=True):
                st.write(review)

        # Meta Reviewer
        with st.spinner("Meta Reviewer is improving the blog..."):

            all_feedback = "\n\n".join(
                f"{name}:\n{review}"
                for name, review in feedback.items()
            )

            final_blog = meta_reviewer.generate_reply(
                messages=[
                    {
                        "role": "user",
                        "content": f"""
                        Original blog:

                        {draft}

                        Reviewers feedback:

                        {all_feedback}

                        Create a polished final blog post.
                        Maximum words: {word_limit}.
                        Return only the final blog.
                        """
                    }
                ]
            )

        # Final Result
        st.success("Blog generation completed!")

        st.subheader("🚀 Final Improved Blog")

        st.markdown(final_blog)

        st.download_button(
            "⬇️ Download Blog",
            data=final_blog,
            file_name="final_blog.txt",
            mime="text/plain"
        )

    except Exception as e:
        st.error(f"Error: {str(e)}")
