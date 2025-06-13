import streamlit as st
import streamlit.components.v1 as components

st.title("⬅️➡️ Arrow Key Navigation Demo")

# JS snippet to capture key presses and redirect via query params
components.html("""
<script>
document.addEventListener('keydown', function(event) {
    if (event.key === "ArrowRight") {
        window.location.search = '?move=next';
    }
    if (event.key === "ArrowLeft") {
        window.location.search = '?move=prev';
    }
});
</script>
""", height=0)

# Read query param
move = st.query_params.get("move", [None])[0]

if move == "next":
    st.success("➡️ Next match triggered via ArrowRight")
elif move == "prev":
    st.success("⬅️ Previous match triggered via ArrowLeft")
