import streamlit as st
import pandas as pd
import datetime
import math

# 1. APPLICATION SETUP
st.set_page_config(page_title="Smart Metal Hub Pro", page_icon="⚙️", layout="wide")
st.title("🏢 SMART METAL HUB PRO — Enterprise Warehouse & Estimator Suite")

st.markdown(
    """
    <div style="background-color:#1e293b; padding:12px; border-radius:6px; margin-bottom:20px;">
        <h4 style="color:#ffffff; margin:0; font-size:14px; font-weight:normal;">🏭 Active Session Mode: Connected to Live Factory Floor Register & Profile Calculator</h4>
    </div>
    """, 
    unsafe_allow_html=True
)

# 2. DENSITY CONFIGURATION (g/cm³ converted to kg/mm³)
DENSITIES = {
    "Stainless Steel (SS)": 0.00000793,
    "Mild Steel (MS)": 0.00000785,
    "Aluminum (Al)": 0.00000270
}

def calculate_sheet_weight(length, width, thickness, material):
    density = DENSITIES.get(material, 0.00000793)
    return round(length * width * thickness * density, 2)

def calculate_rod_weight(diameter, length, material):
    density = DENSITIES.get(material, 0.00000793)
    radius = diameter / 2
    volume = math.pi * (radius ** 2) * length
    return round(volume * density, 2)

def calculate_pipe_weight(outer_diameter, thickness, length, material):
    density = DENSITIES.get(material, 0.00000793)
    outer_radius = outer_diameter / 2
    inner_radius = outer_radius - thickness
    if inner_radius <= 0: return 0.0
    volume = math.pi * ((outer_radius ** 2) - (inner_radius ** 2)) * length
    return round(volume * density, 2)

def calculate_box_weight(height, width, thickness, length, material):
    density = DENSITIES.get(material, 0.00000793)
    outer_area = height * width
    inner_height = height - (2 * thickness)
    inner_width = width - (2 * thickness)
    if inner_height <= 0 or inner_width <= 0: return 0.0
    inner_area = inner_height * inner_width
    volume = (outer_area - inner_area) * length
    return round(volume * density, 2)

# 3. SIDEBAR CONFIGURATION
st.sidebar.header("📊 System Configuration Panel")
st.sidebar.subheader("Live Market Material Rates")
rates = {
    "Stainless Steel (SS)": st.sidebar.number_input("Stainless Steel (SS) Rate / Kg (₹)", min_value=0.0, value=315.0, step=5.0),
    "Mild Steel (MS)": st.sidebar.number_input("Mild Steel (MS) Rate / Kg (₹)", min_value=0.0, value=85.0, step=2.0),
    "Aluminum (Al)": st.sidebar.number_input("Aluminum (Al) Rate / Kg (₹)", min_value=0.0, value=220.0, step=5.0)
}

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Match Tolerance Settings")
tolerance_mm = st.sidebar.slider("Allowable Under-Size Cutting Buffer (mm)", min_value=0, max_value=25, value=5)

# 4. INITIALIZE DATABASES
if 'full_sheets' not in st.session_state:
    st.session_state.full_sheets = pd.DataFrame([
        {"sheet_id": "SHT-001", "material": "Stainless Steel (SS)", "grade": "SS 304", "thickness": 1.2, "length": 2500, "width": 1250, "quantity": 15, "unit_weight_kg": 29.74},
        {"sheet_id": "SHT-002", "material": "Stainless Steel (SS)", "grade": "SS 316", "thickness": 2.0, "length": 2500, "width": 1250, "quantity": 8, "unit_weight_kg": 49.56},
        {"sheet_id": "SHT-003", "material": "Mild Steel (MS)", "grade": "MS Commercial", "thickness": 1.5, "length": 2000, "width": 1000, "quantity": 24, "unit_weight_kg": 23.55},
    ])

if 'bits_inventory' not in st.session_state or 'date_logged' not in st.session_state.bits_inventory.columns:
    st.session_state.bits_inventory = pd.DataFrame([
        {"bit_id": "BIT-001", "material": "Stainless Steel (SS)", "grade": "SS 304", "thickness": 1.2, "length": 1200, "width": 600, "weight_kg": 6.85, "status": "Available", "date_logged": "15-May-2026"},
        {"bit_id": "BIT-002", "material": "Mild Steel (MS)", "grade": "MS Commercial", "thickness": 1.5, "length": 1000, "width": 500, "weight_kg": 5.89, "status": "Available", "date_logged": "19-May-2026"},
    ])

# Sync active state handles
df_sheets = st.session_state.full_sheets
df_bits = st.session_state.bits_inventory

# Calculate dynamic values
if not df_sheets.empty:
    st.session_state.full_sheets['total_weight_kg'] = round(st.session_state.full_sheets['unit_weight_kg'] * st.session_state.full_sheets['quantity'], 2)
    st.session_state.full_sheets['total_value_inr'] = st.session_state.full_sheets.apply(lambda r: round(r['total_weight_kg'] * rates.get(r['material'], 0.0), 2), axis=1)
    df_sheets = st.session_state.full_sheets

if not df_bits.empty:
    st.session_state.bits_inventory['est_value_inr'] = st.session_state.bits_inventory.apply(lambda r: round(r['weight_kg'] * rates.get(r['material'], 0.0), 2), axis=1)
    df_bits = st.session_state.bits_inventory

# 5. USER INTERFACE THREE-TAB NAVIGATION
tab1, tab2, tab3 = st.tabs(["📋 FULL SHEETS INVENTORY", "✂️ OFF-CUT BITS DATABASE", "📐 STRUCTURAL PROFILE CALCULATOR"])

# ==========================================
# TAB 1: FULL SIZE SHEET INVENTORY
# ==========================================
with tab1:
    st.subheader("Warehouse Fresh Full Sheet Stock")
    if not df_sheets.empty:
        s_col1, s_col2, s_col3 = st.columns(3)
        s_col1.metric("Total Fresh Sheets", f"{int(df_sheets['quantity'].sum())} Sheets")
        s_col2.metric("Total Weight", f"{round(df_sheets['total_weight_kg'].sum(), 2)} Kg")
        s_col3.metric("Stock Valuation", f"₹{df_sheets['total_value_inr'].sum():,.2f}")
        st.dataframe(df_sheets[['sheet_id', 'material', 'grade', 'thickness', 'length', 'width', 'quantity', 'unit_weight_kg', 'total_weight_kg', 'total_value_inr']], use_container_width=True)
    
    st.markdown("---")
    fs_col1, fs_col2 = st.columns([1, 1.3])
    with fs_col1:
        st.subheader("📥 Add New Factory Bundle")
        with st.form("sheet_form", clear_on_submit=True):
            s_id = f"SHT-{len(st.session_state.full_sheets) + 1:03d}"
            s_mat = st.selectbox("Material Type", list(DENSITIES.keys()), key="f_mat")
            s_grade = st.text_input("Grade Specification", value="SS 304", key="f_grade")
            s_thick = st.number_input("Thickness (mm)", min_value=0.1, value=1.2, step=0.1, key="f_thick")
            s_len = st.number_input("Standard Length (mm)", min_value=1, value=2500, step=50)
            s_wid = st.number_input("Standard Width (mm)", min_value=1, value=1250, step=50)
            s_qty = st.number_input("Quantity Received", min_value=1, value=10, step=1)
            
            u_weight = calculate_sheet_weight(s_len, s_wid, s_thick, s_mat)
            st.info(f"⚖️ Calculated Unit Weight: **{u_weight} kg per sheet**")
            
            if st.form_submit_button("Add Bundle to Stock"):
                new_sheet = {"sheet_id": s_id, "material": s_mat, "grade": s_grade, "thickness": s_thick, "length": s_len, "width": s_wid, "quantity": s_qty, "unit_weight_kg": u_weight}
                st.session_state.full_sheets = pd.concat([st.session_state.full_sheets, pd.DataFrame([new_sheet])], ignore_index=True)
                st.rerun()

    with fs_col2:
        st.subheader("⚡ Chop Sheet (Move Leftovers to Bits)")
        if not df_sheets.empty:
            sheet_options = {f"{row['sheet_id']} - {row['grade']} ({row['thickness']}mm)": idx for idx, row in df_sheets.iterrows() if row['quantity'] > 0}
            if sheet_options:
                selected_sheet_label = st.selectbox("Select Parent Sheet to Cut", list(sheet_options.keys()))
                target_idx = sheet_options[selected_sheet_label]
                parent_row = df_sheets.iloc[target_idx]
                
                c1, c2 = st.columns(2)
                with c1: cut_len = st.number_input("Size Cut: Length (mm)", min_value=1, max_value=int(parent_row['length']), value=1000)
                with c2: cut_wid = st.number_input("Size Cut: Width (mm)", min_value=1, max_value=int(parent_row['width']), value=1000)
                
                rem_len = parent_row['length'] - cut_len
                rem_wid = parent_row['width'] - cut_wid
                
                display_scale = 0.15
                p_w_vis = int(parent_row['width'] * display_scale)
                p_l_vis = int(parent_row['length'] * display_scale)
                c_w_vis = int(cut_wid * display_scale)
                c_l_vis = int(cut_len * display_scale)
                
                st.write("📐 **Live Slicing Allocation Map Preview:**")
                st.markdown(f'''
                    <div style="width: {p_l_vis}px; height: {p_w_vis}px; background-color: #e0e0e0; border: 2px dashed #757575; position: relative; margin-bottom: 15px;">
                        <div style="width: {c_l_vis}px; height: {c_w_vis}px; background-color: #ef5350; border-right: 2px solid #b71c1c; border-bottom: 2px solid #b71c1c; position: absolute; top: 0; left: 0; display: flex; align-items: center; justify-content: center; color: white; font-size: 10px; font-weight: bold;">
                            USED ({int(cut_len)}x{int(cut_wid)})
                        </div>
                    </div>
                ''', unsafe_allow_html=True)
                
                if st.button("🔥 Execute Cut Order", use_container_width=True):
                    st.session_state.full_sheets.at[target_idx, 'quantity'] -= 1
                    new_bits_to_add = []
                    if rem_len > 0: new_bits_to_add.append({"length": rem_len, "width": parent_row['width']})
                    if rem_wid > 0 and cut_len > 0: new_bits_to_add.append({"length": cut_len, "width": rem_wid})
                        
                    for bit in new_bits_to_add:
                        bit_num = max([int(x.split('-')[1]) for x in st.session_state.bits_inventory['bit_id']]) + 1 if not st.session_state.bits_inventory.empty else 1
                        new_bit_row = {
                            "bit_id": f"BIT-{bit_num:03d}", "material": parent_row['material'], "grade": parent_row['grade'],
                            "thickness": parent_row['thickness'], "length": bit['length'], "width": bit['width'],
                            "weight_kg": calculate_sheet_weight(bit['length'], bit['width'], parent_row['thickness'], parent_row['material']),
                            "status": "Available", "date_logged": datetime.date.today().strftime("%d-%b-%Y")
                        }
                        st.session_state.bits_inventory = pd.concat([st.session_state.bits_inventory, pd.DataFrame([new_bit_row])], ignore_index=True)
                    st.success("Parent sheet decremented and remnants split smoothly into off-cuts database!")
                    st.rerun()

# ==========================================
# TAB 2: OFF-CUT BITS DATABASE
# ==========================================
with tab2:
    st.subheader("Custom Layout Sizes & Off-Cuts Engine")
    if not df_bits.empty:
        b_col1, b_col2, b_col3 = st.columns(3)
        b_col1.metric("Available Scrap Pieces", f"{len(df_bits)} Bits")
        b_col2.metric("Scrap Tonnage Weight", f"{round(df_bits['weight_kg'].sum(), 2)} Kg")
        b_col3.metric("Tied Scrap Capital", f"₹{df_bits['est_value_inr'].sum():,.2f}")
        st.dataframe(df_bits[['bit_id', 'material', 'grade', 'thickness', 'length', 'width', 'weight_kg', 'est_value_inr', 'status', 'date_logged']], use_container_width=True)
    
    st.markdown("---")
    bc1, bc2 = st.columns([1, 1.3])
    with bc1:
        st.subheader("📥 Log Manual External Off-Cut")
        with st.form("manual_bit_form", clear_on_submit=True):
            bit_num = max([int(x.split('-')[1]) for x in st.session_state.bits_inventory['bit_id']]) + 1 if not st.session_state.bits_inventory.empty else 1
            m_id = f"BIT-{bit_num:03d}"
            m_mat = st.selectbox("Material Type", list(DENSITIES.keys()), key="bm_mat")
            m_grade = st.text_input("Grade Specification", value="SS 304", key="bm_grade")
            m_thick = st.number_input("Thickness (mm)", min_value=0.1, value=1.2, key="bm_thick")
            m_len = st.number_input("Length (mm)", min_value=1, value=600, key="bm_len")
            m_wid = st.number_input("Width (mm)", min_value=1, value=400, key="bm_wid")
            
            b_weight = calculate_sheet_weight(m_len, m_wid, m_thick, m_mat)
            if st.form_submit_button("Save Bit to Stock"):
                new_bit = {"bit_id": m_id, "material": m_mat, "grade": m_grade, "thickness": m_thick, "length": m_len, "width": m_wid, "weight_kg": b_weight, "status": "Available", "date_logged": datetime.date.today().strftime("%d-%b-%Y")}
                st.session_state.bits_inventory = pd.concat([st.session_state.bits_inventory, pd.DataFrame([new_bit])], ignore_index=True)
                st.rerun()

    with bc2:
        st.subheader("🔍 Match Custom Customer Order")
        if 't2_len' not in st.session_state: st.session_state.t2_len = 600
        if 't2_wid' not in st.session_state: st.session_state.t2_wid = 300

        bsc1, bsc2, bsc3, bsc4 = st.columns(4)
        with bsc1: req_mat = st.selectbox("Search Material", list(DENSITIES.keys()), key="s_mat")
        with bsc2: req_thick = st.number_input("Thickness (mm)", min_value=0.1, value=1.2, key="s_thick", step=0.1)
        with bsc3: req_len = st.number_input("Min Length (mm)", min_value=1, value=st.session_state.t2_len, key="s_len_input")
        with bsc4: req_wid = st.number_input("Min Width (mm)", min_value=1, value=st.session_state.t2_wid, key="s_wid_input")
            
        if st.button("🔄 Swap Search Length ⇄ Width Parameters", use_container_width=True):
            st.session_state.t2_len, st.session_state.t2_wid = req_wid, req_len
            st.rerun()

        if not df_bits.empty:
            matches = df_bits[(df_bits['material'] == req_mat) & (df_bits['thickness'].round(2) == round(req_thick, 2)) & (df_bits['length'] >= (req_len - tolerance_mm)) & (df_bits['width'] >= (req_wid - tolerance_mm)) & (df_bits['status'] == "Available")]
            if not matches.empty:
                sorted_matches = matches.sort_values(by=['length', 'width'])
                st.success(f"🎉 Found {len(sorted_matches)} matching piece(s)!")
                st.dataframe(sorted_matches[['bit_id', 'grade', 'length', 'width', 'weight_kg', 'est_value_inr', 'date_logged']], use_container_width=True)
                
                best_match = sorted_matches.iloc[0]
                whatsapp_msg = f"⚙️ *MATERIAL STOCK MATCH* ⚙️\n\n" \
                               f"• *Material:* {best_match['material']}\n" \
                               f"• *Item ID:* {best_match['bit_id']} ({best_match['grade']})\n" \
                               f"• *Dimensions:* {int(best_match['length'])} x {int(best_match['width'])} mm\n" \
                               f"• *Calculated Weight:* {best_match['weight_kg']} Kg\n" \
                               f"• *Est. Value:* ₹{best_match['est_value_inr']} (@ ₹{rates.get(best_match['material'])}/kg)"
                st.code(whatsapp_msg, language="markdown")
            else:
                st.error("❌ No matching scrap sizes found matching that specific material profile.")

# ==========================================
# TAB 3: UNIVERSAL PROFILE CALCULATOR (Updated)
# ==========================================
with tab3:
    st.subheader("📐 Universal Section Weight Estimation Hub")
    p_col1, p_col2, p_col3 = st.columns(3)
    
    with p_col1:
        st.markdown("### 🪵 Round Bar / Rod")
        with st.container(border=True):
            rod_mat = st.selectbox("Select Rod Metal", list(DENSITIES.keys()), key="rod_m")
            rod_dia = st.number_input("Outer Diameter (mm)", min_value=1.0, value=25.0, step=1.0)
            rod_len = st.number_input("Length Per Piece (mm)", min_value=1.0, value=1000.0, step=100.0, key="rod_l")
            
            # ITEM COUNT UPGRADE
            rod_qty = st.number_input("Number of Items / Pieces", min_value=1, value=1, step=1, key="rod_q")
            
            single_rod_w = calculate_rod_weight(rod_dia, rod_len, rod_mat)
            total_rod_w = round(single_rod_w * rod_qty, 2)
            rod_cost = round(total_rod_w * rates.get(rod_mat, 0.0), 2)
            
            st.metric("⚖️ Total Weight", f"{total_rod_w} Kg", help=f"{single_rod_w} kg per item")
            st.metric("💰 Total Material Cost", f"₹{rod_cost:,.2f}")
            
            rod_string = f"📐 *SOLID ROUND ROD QUOTE*\n• Metal: {rod_mat}\n• Size: ⌀{rod_dia}mm x {int(rod_len)}mm\n• Number of Items: {rod_qty}\n• Total Weight: {total_rod_w} Kg\n• Value: ₹{rod_cost}"
            st.code(rod_string, language="markdown")

    with p_col2:
        st.markdown("### 🫙 Round Hollow Pipe")
        with st.container(border=True):
            pipe_mat = st.selectbox("Select Pipe Metal", list(DENSITIES.keys()), key="pipe_m")
            pipe_dia = st.number_input("Outer Diameter (OD) (mm)", min_value=1.0, value=50.0, step=1.0)
            pipe_thick = st.number_input("Wall Thickness (mm)", min_value=0.5, value=3.0, step=0.5, key="pipe_t")
            pipe_len = st.number_input("Length Per Piece (mm)", min_value=1.0, value=1000.0, step=100.0, key="pipe_l")
            
            # ITEM COUNT UPGRADE
            pipe_qty = st.number_input("Number of Items / Pieces", min_value=1, value=1, step=1, key="pipe_q")
            
            single_pipe_w = calculate_pipe_weight(pipe_dia, pipe_thick, pipe_len, pipe_mat)
            total_pipe_w = round(single_pipe_w * pipe_qty, 2)
            pipe_cost = round(total_pipe_w * rates.get(pipe_mat, 0.0), 2)
            
            st.metric("⚖️ Total Weight", f"{total_pipe_w} Kg", help=f"{single_pipe_w} kg per item")
            st.metric("💰 Total Material Cost", f"₹{pipe_cost:,.2f}")
            
            pipe_string = f"📐 *HOLLOW PIPE QUOTE*\n• Metal: {pipe_mat}\n• Size: OD ⌀{pipe_dia}mm x Thick {pipe_thick}mm x {int(pipe_len)}mm\n• Number of Items: {pipe_qty}\n• Total Weight: {total_pipe_w} Kg\n• Value: ₹{pipe_cost}"
            st.code(pipe_string, language="markdown")

    with p_col3:
        st.markdown("### 🔲 Square / Box Section")
        with st.container(border=True):
            box_mat = st.selectbox("Select Box Metal", list(DENSITIES.keys()), key="box_m")
            box_h = st.number_input("Section Height (mm)", min_value=1.0, value=40.0, step=1.0)
            box_w = st.number_input("Section Width (mm)", min_value=1.0, value=40.0, step=1.0)
            box_t = st.number_input("Wall Thickness (mm)", min_value=0.5, value=2.5, step=0.5, key="box_t")
            box_l = st.number_input("Length Per Piece (mm)", min_value=1.0, value=1000.0, step=100.0, key="box_l")
            
            # ITEM COUNT UPGRADE
            box_qty = st.number_input("Number of Items / Pieces", min_value=1, value=1, step=1, key="box_q")
            
            single_box_w = calculate_box_weight(box_h, box_w, box_t, box_l, box_mat)
            total_box_w = round(single_box_w * box_qty, 2)
            box_cost = round(total_box_w * rates.get(box_mat, 0.0), 2)
            
            st.metric("⚖️ Total Weight", f"{total_box_w} Kg", help=f"{single_box_w} kg per item")
            st.metric("💰 Total Material Cost", f"₹{box_cost:,.2f}")
            
            box_string = f"📐 *BOX SECTION QUOTE*\n• Metal: {box_mat}\n• Size: {int(box_h)}x{int(box_w)}mm x Thick {box_t}mm x {int(box_l)}mm\n• Number of Items: {box_qty}\n• Total Weight: {total_box_w} Kg\n• Value: ₹{box_cost}"
            st.code(box_string, language="markdown")