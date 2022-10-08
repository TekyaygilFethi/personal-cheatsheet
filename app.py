import streamlit as st
from tinydb import TinyDB, Query, where
import pandas as pd
from redis_manager import RedisManager
import json


db = TinyDB("db.json")
redis_manager = RedisManager()

def insert_db(payload):
    db.insert(payload)
    __refreshDbCache()

def __refreshDbCache():
    db_data = db.all()
    redis_manager.Set("alldb", json.dumps(db_data))

def load_db():
    return pd.DataFrame(db.all())

def get_random():
    all_db_json = redis_manager.Get("alldb")

    all_db = pd.json_normalize(json.loads(all_db_json))
    return all_db.sample()

def __queryByDesc(desc):
    row = Query()
    return db.search(row.desc == desc)[0]

def find_doc_id_from_db(desc):
    desc_cache_key = f"desc_{desc.replace(' ','_')}_docid"
    result = redis_manager.Get(desc_cache_key)

    if result is not None:
        return result

    found = __queryByDesc(desc)
    print("Resultquery",found.doc_id)
    redis_manager.Set(desc_cache_key, found.doc_id)

    return found.doc_id


def delete_record_from_db(id_key):
    db.remove(doc_ids=[id_key])
    __refreshDbCache()


tab1, tab2, tab3 = st.tabs(["Submit", "List", "Edit"])

with tab1:
    st.title("👋 Welcome to NeatSheets")
    st.caption(
        "📘 SheatCheet is a reminder for developers and a place to take note of shortcodes."
    )
    st.caption(" ⬆️ ➡️ You can see other tabs for list all cheatsheet, edit or delete.")
    st.caption(" ⬇️ You can add new one-liner below")
    with st.container():
        st.markdown("---")
        st.button("Another")
        value = get_random().to_dict(orient="list")
        st.subheader(value["desc"][0])
        st.code(value["cmd"][0])

    st.markdown("---")

    st.subheader("🚀 Input new entry")
    with st.form("insert_form", clear_on_submit=True):
        st.write("Insert new entry")
        payload = {}
        payload["type"] = st.text_input(
            label="Type", help="e.g. Docker", placeholder="Image"
        )
        payload["desc"] = st.text_input(
            label="Description", placeholder="PNG Sequence to MP4"
        )
        payload["cmd"] = st.text_area(
            label="Command",
            placeholder='for f in *.mp4; do ffmpeg -i "$f" -vf fps=2 png-exports/${f%.*}_%06d.png; done',
        )

        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit")
        if submitted:
            insert_db(payload)
            st.success("Done!")


with tab2:

    for index, value in load_db().iterrows():
        st.subheader(value["desc"])
        st.code(value["cmd"])
    st.markdown("---")
    st.button("♻️ Refresh")

with tab3:
    df = load_db()
    options = [value["desc"] for index, value in df.iterrows()]
    st.header("👇 Select entry for deleting or editing")
    selection = st.selectbox("", options=options)
    selected_row = df[df["desc"] == selection]
    st.dataframe(selected_row, use_container_width=True)
    st.subheader("✍️ Edit")
    st.info("⚠️ Update function not implemented yet ⚠️")
    with st.form("edit_form", clear_on_submit=True):
        st.text_input("New Type", selected_row["type"].values[0])
        st.text_input("New Description", selected_row["desc"].values[0])
        st.text_area("New Command", selected_row["cmd"].values[0])
        update = st.form_submit_button("Update")
        if update:
            st.success("Done!")

    st.subheader("🗑 Delete")
    with st.expander("Open to delete entry"):
        delete_status = st.checkbox("I'm sure")
        if delete_status:
            if st.button("Delete"):
                doc_id = find_doc_id_from_db(selected_row["desc"].values[0])
                delete_record_from_db(doc_id)
                redis_manager.Delete(f"desc_{selected_row['desc'].values[0].replace(' ','_')}_docid")
                st.info("Deleted!", icon="🔥")
