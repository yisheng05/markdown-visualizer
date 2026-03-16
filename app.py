import streamlit as st

def main():
    st.set_page_config(
        page_title="Markdown Visualizer",
        page_icon="📝",
        layout="wide"
    )

    st.title("📝 Markdown Visualizer")
    st.markdown("Upload a `.md` file to see its rendered output.")

    # Sidebar for additional options
    st.sidebar.title("Settings")
    show_raw = st.sidebar.checkbox("Show Raw Content", value=False)
    
    # File uploader
    uploaded_file = st.file_uploader("Choose a Markdown file", type=["md"])

    if uploaded_file is not None:
        try:
            # Read and decode the file content
            file_content = uploaded_file.read().decode("utf-8")
            
            # Display file name and size
            st.info(f"Viewing: **{uploaded_file.name}** ({uploaded_file.size} bytes)")
            
            if show_raw:
                st.subheader("Raw Markdown Source")
                st.code(file_content, language="markdown")
                st.divider()

            # Render the markdown content
            st.subheader("Rendered Visualization")
            st.markdown(file_content, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error reading file: {e}")
    else:
        st.info("Please upload a Markdown file to get started.")

if __name__ == "__main__":
    main()
