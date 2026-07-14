import json
import os
import streamlit as st
from datetime import datetime

# Persistent Local Databases
STUDENT_DB = "students.json"
TEACHER_DB = "teachers.json"
STUDENT_TRANSACTIONS_DB = "student_transactions.json"
TEACHER_PAYROLL_DB = "teacher_payroll.json"

def read_db(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {}
    return {}

def write_db(filepath, data):
    with open(filepath, "w") as file:
        json.dump(data, file, indent=4)

def read_list_db(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []
    return []

def append_to_list_db(filepath, new_entry):
    db_list = read_list_db(filepath)
    db_list.append(new_entry)
    with open(filepath, "w") as file:
        json.dump(db_list, file, indent=4)

# ==================== STUDENT LOGIC ====================

def add_student(stu_id, name, grade):
    if not stu_id.strip() or not name.strip() or not grade.strip():
        return "⚠️ Error: All fields are required.", "error"
    db = read_db(STUDENT_DB)
    if stu_id in db:
        return f"⚠️ Error: Student ID '{stu_id}' already exists.", "error"

    db[stu_id] = {"name": name, "grade": grade, "balance": 0.0}
    write_db(STUDENT_DB, db)
    return f"✅ Success: Added student {name} ({grade})", "success"

def delete_student(stu_id):
    if not stu_id.strip():
        return "⚠️ Error: Please enter a Student ID.", "error"
    db = read_db(STUDENT_DB)
    if stu_id in db:
        name = db[stu_id]["name"]
        del db[stu_id]
        write_db(STUDENT_DB, db)
        return f"🗑️ Success: Deleted student {name} from the portal.", "success"
    return "⚠️ Error: Student ID not found.", "error"

def transact_tuition(stu_id, transaction_type, amount, description):
    if not stu_id.strip() or amount <= 0:
        return "⚠️ Error: Valid Student ID and Amount greater than 0 are required.", "error", None
    db = read_db(STUDENT_DB)
    if stu_id not in db:
        return "⚠️ Error: Student ID not found.", "error", None

    amount = float(amount)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    transaction_record = {
        "stu_id": stu_id,
        "type": transaction_type,
        "amount": amount,
        "description": description.strip() if description.strip() else ("Tuition Fee" if transaction_type == "Charge Fee (+)" else "Tuition Payment"),
        "timestamp": current_time
    }

    if transaction_type == "Charge Fee (+)":
        db[stu_id]["balance"] += amount
        transaction_record["final_balance"] = db[stu_id]["balance"]
        append_to_list_db(STUDENT_TRANSACTIONS_DB, transaction_record)
        write_db(STUDENT_DB, db)
        return f"✅ Charged ${amount:.2f} to {db[stu_id]['name']}. Current balance: ${db[stu_id]['balance']:.2f}", "success", None

    else:  # Payment Collection & Receipt Generation
        db[stu_id]["balance"] -= amount
        transaction_record["final_balance"] = db[stu_id]["balance"]
        append_to_list_db(STUDENT_TRANSACTIONS_DB, transaction_record)
        write_db(STUDENT_DB, db)

        receipt_content = (
            "============================================\n"
            "       PREVAILING WORD SCHOOL SYSTEM - TUITION RECEIPT       \n"
            "============================================\n"
            f"Receipt Reference: REC-{stu_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}\n"
            f"Student Name:      {db[stu_id]['name']}\n"
            f"Class/Grade:       {db[stu_id]['grade']}\n"
            "--------------------------------------------\n"
            f"Description:       {transaction_record['description']}\n"
            f"Amount Paid:       ${amount:.2f}\n"
            f"Transaction Time:  {current_time}\n"
            "--------------------------------------------\n"
            f"REMAINING BALANCE OWING: ${db[stu_id]['balance']:.2f}\n\n"
            "Status: RECEIVED / SYSTEM COMPLETED\n"
            "============================================\n"
        )
        return f"✅ Payment recorded for {db[stu_id]['name']}!", "success", receipt_content

def search_student(query):
    if not query.strip():
        return "⚠️ Error: Please enter a search query.", "error", None
    
    db = read_db(STUDENT_DB)
    results = {}
    query_lower = query.lower()

    for stu_id, data in db.items():
        if query_lower in stu_id.lower() or query_lower in data['name'].lower():
            results[stu_id] = data

    if not results:
        return "No students found matching your query.", "warning", None

    # Format results as a neat terminal table
    formatted_results = "ID        Name             Grade   Balance\n------------------------------------------------\n"
    for stu_id, data in results.items():
        formatted_results += f"{stu_id:<9} {data['name']:<16} {data['grade']:<7} ${data['balance']:.2f}\n"

    return "Search complete.", "success", formatted_results


# ==================== STREAMLIT UI ====================
st.set_page_config(page_title="School Management System", page_icon="🏫", layout="wide")
st.title("🏫 School Portal & Tuition Management System")

# Initialize Session State values to safely store background transaction calculations
if 'receipt_text' not in st.session_state:
    st.session_state['receipt_text'] = None
if 'receipt_filename' not in st.session_state:
    st.session_state['receipt_filename'] = ""

tab1, tab2, tab3 = st.tabs(["Student Management", "Tuition & Billing", "Search & Reports"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Add New Student")
        # Kept in forms to handle clean keyboard entries without page resets
        with st.form("add_student_form", clear_on_submit=True):
            stu_id = st.text_input("Student ID")
            name = st.text_input("Full Name")
            grade = st.text_input("Grade / Class")
            submitted = st.form_submit_button("Add Student")
            
            if submitted:
                msg, status_type = add_student(stu_id, name, grade)
                if status_type == "success":
                    st.success(msg)
                else:
                    st.error(msg)
                
    with col2:
        st.subheader("Delete Student")
        with st.form("delete_student_form", clear_on_submit=True):
            del_id = st.text_input("Student ID to Delete")
            submitted = st.form_submit_button("Delete Student")
            
            if submitted:
                msg, status_type = delete_student(del_id)
                if status_type == "success":
                    st.success(msg)
                else:
                    st.error(msg)

with tab2:
    st.subheader("Record Transaction")
    col1, col2 = st.columns(2)
    
    with col1:
        # Forms removed here to ensure instantaneous state retention for downloads
        trans_id = st.text_input("Student ID Key", key="t_id")
        trans_type = st.radio("Type", ["Charge Fee (+)", "Collect Payment (-)"])
        trans_amount = st.number_input("Amount ($", min_value=0.0, step=0.01, format="%.2f")
        trans_desc = st.text_input("Description (Optional)")
        
        if st.button("Submit Transaction", type="primary"):
            msg, status_type, receipt = transact_tuition(trans_id, trans_type, trans_amount, trans_desc)
            if status_type == "success":
                st.success(msg)
                if receipt:
                    st.session_state['receipt_text'] = receipt
                    st.session_state['receipt_filename'] = f"receipt_{trans_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
                else:
                    st.session_state['receipt_text'] = None
            else:
                st.error(msg)
                    
    with col2:
        st.write("### Transaction Output & Actions")
        if st.session_state['receipt_text'] is not None:
            st.info("📄 Active Receipt Generated Successfully")
            st.download_button(
                label="📥 Download Receipt Text File",
                data=st.session_state['receipt_text'],
                file_name=st.session_state['receipt_filename'],
                mime="text/plain"
            )
        else:
            st.write("No transaction payments pending download.")

with tab3:
    st.subheader("Lookup Student Accounts")
    search_query = st.text_input("Search by ID or Name")
    
    if search_query:
        msg, status_type, table_data = search_student(search_query)
        if table_data:
            st.code(table_data, language="text")
        else:
            st.warning(msg)
