import streamlit as st
from annotated_text import annotated_text

from ptp.eventrefparser import EventReferenceParser

st.title("Event Reference Parser")
st.text_input("Event Reference",key="eventRef", placeholder="Please enter an event reference")
parser = EventReferenceParser()
if st.session_state.eventRef:
    with st.spinner('Parsing event reference...'):
        with st.container():
            tokenSeq = parser.parse(st.session_state.eventRef, "eventRefParser", show=True)
            # show parsing
            lut = {}
            for token in tokenSeq.matchResults:
                if token.name not in ["first Letter", "word"]:
                    if token.pos in lut:
                        lut[token.pos].append(token)
                    else:
                        lut[token.pos] = [token]
            annText=[]
            for i, word in enumerate(st.session_state.eventRef.split(" ")):
                if i in lut:
                    name = "/".join([c.name for c in lut[i]])
                    annText.append((word, name))
                else:
                    annText.append(f"{word} ")
            annotated_text(*annText)
            # show stats
            with st.expander("Show the statistics"):
                for category in parser.categories:
                    with st.container():
                        st.header(category.name)
                        st.markdown(category.mostCommonTable(tablefmt="github"))
