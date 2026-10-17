from CROPS import N_BEDARF , ERTRAEGE 

def get_duev_ertrag(crop):
    return ERTRAEGE[crop]

def get_n_bedarf(crop):
    return N_BEDARF[crop]

def get_ertrag_correction(crop, crop_5y_mean):  # A_Delta_Y
    Delta_Y = crop_5y_mean - ERTRAEGE[crop]

    if Delta_Y < -50:
        return -10
    elif Delta_Y > 50:
        return 10
    else:
        return 0

def get_humus_correction(h): # N_humus 
    if h > 0.04: 
        return 20 
    else: 
        return 0 

def get_N_prev_correction(N_prev): # O_prev 
    return 0.1*N_prev 

def get_correction_term(N_min, humus, N_prev, N_VJ, N_ZF):
    N_humus = get_humus_correction(humus)
    O_prev = get_N_prev_correction(N_prev)
    return sum((N_min, N_humus, O_prev, N_VJ, N_ZF))

def get_dbe(N_Bedarf , A_Delta_Y , N_correction):
    return N_Bedarf + A_Delta_Y - N_correction 
    
def streamlit_bde_wrapper(schlag , mean_5_yrs , N_min , humus , N_prev , N_vor , N_zw):

    A_Delta_Y = get_ertrag_correction(schlag , mean_5_yrs) 
    N_Correction = get_correction_term(N_min , humus , N_prev, N_vor, N_zw)
    N_Bedarf = N_BEDARF[schlag]
    DBE =get_dbe(N_Bedarf , A_Delta_Y , N_Correction)
    return DBE 