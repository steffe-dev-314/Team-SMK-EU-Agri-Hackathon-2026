import pandas as pd 
import streamlit as st 

top_col_1 = ['Düngejahr' , 'DÜNGEJAHR_PLACEHOLDER'] + [None] + ['Schlag' , 'SCHLAG_PLACEHOLDER'] + [None]*4 + ['Vorjahreskultur' , 'VORJAHRESKULTUR_PLACEHOLDER']

top_col_2 = ['Betriebsnummer','BETRIEBSNUMMER_PLACEHOLDER'] + [None] + ['Feldblocknummer' , 'FELDBLOCKNUMMER_PLACEHOLDER'] + [None]*4 + ['Zwischenfrucht' , 'ZWISCHENFRUCHT_PLACEHOLDER']

top_col_3 = ['Betrieb' , 'BETRIEB_PLACEHOLDER'] + [None] + ['Schlaggröße' , 'SCHLAGGRÖßE_PLACEHOLDER'] + [None]*6

head_cols_dbe = ['Datum' , 
                 'Kultur' , 
                 'DüV Ertrag (dt / ha)' , 
                 '5 Jahres Durchschnitt Betrieg (dt / ha)' , 
                 'N-Bedarf (kg / ha)',
                 'Zu/Abschlag Ertragsdifferenz (kg / ha)' ,
                 'Abschlag Nmin / Richtwert (kg / ha)',
                 'Abschlag Standort / Humus (kg / ha)',
                 'Abschlag org. Dünnung Vorjahr (kg / ha)',
                 'Abschlag Vor / Zwischenfrucht (kg / ha)',
                 'N-Düngebedarf (kg / ha)']

max_len = len(head_cols_dbe)

header_dbe = [None]*5 + ['Düngebedarfsermittlung Stickstoff'] + [None]*5

header_fert_doc = [None]*5 + ['Düngebedarfsermittlung Stickstoff'] + [None]*3 + ['Summe DBE / ha'] + ['Summe DBE / Fläche']

head_cols_fert_doc = ['Datum',
                      'Düngemittel',
                      'Nährstoffträger',
                      'Menge Einheit / ha',
                      'Nges kg / ha',
                      'Nges kg / Fläche',
                      'NPflanzenverfuegbar kg / ha',
                      'Npflanzenverfuegbar kg / Fläche'
] + [None] + ['Summe DBE / ha_PLACEHOLDER']+ ['Summe DBE / Fläche_PLACEHOLDER']

fert_data_cols = [
                ['DATE' , 'FERT' , 'NÄHR' , 'MENGE' , 'GES HA' , 'GES A', 'PF HA' , 'PF A'] + [None]*3 ,

                ['DATE' , 'FERT' , 'NÄHR' , 'MENGE' , 'GES HA' , 'GES A', 'PF HA' , 'PF A'] + [None]*1 + ['Aufgebr. N Pflanzenverfügbar / ha'] + ['Aufgebr. N Pflanzenverfügbar / Fläche'],

                ['DATE' , 'FERT' , 'NÄHR' , 'MENGE' , 'GES HA' , 'GES A', 'PF HA' , 'PF A'] + [None]*1 + ['Aufgebr. N Pflanzenverfügbar / ha_PLACEHOLDER'] + ['Aufgebr. N Pflanzenverfügbar / Fläche_PLACEHOLDER'],

                ['DATE' , 'FERT' , 'NÄHR' , 'MENGE' , 'GES HA' , 'GES A', 'PF HA' , 'PF A'] + [None]*1 + ['Aufgebr. N-org kg / ha'] + ['Aufgebr. N-org kg / Fläche'],

                ['DATE' , 'FERT' , 'NÄHR' , 'MENGE' , 'GES HA' , 'GES A', 'PF HA' , 'PF A'] + [None]*1 + ['Aufgebr. N-org kg / ha_PLACEHOLDER'] + ['Aufgebr. N-org kg / Fläche_PLACEHOLDER'],

                ['DATE' , 'FERT' , 'NÄHR' , 'MENGE' , 'GES HA' , 'GES A', 'PF HA' , 'PF A'] + [None]*2 + ['Abschlag Düngung Folgejahr kg / ha'],

                ['DATE' , 'FERT' , 'NÄHR' , 'MENGE' , 'GES HA' , 'GES A', 'PF HA' , 'PF A'] + [None]*2 + ['Abschlag Düngung Folgejahr kg / ha_PLACEHOLDER']
]

fert_data_cols_in = [[f'{F[i]}_{i}' if i < 8 else F[i] for i in range(len(F))] for F in fert_data_cols]

empty_list = [None]*max_len

template = pd.DataFrame([top_col_1 , top_col_2, top_col_3, header_dbe , head_cols_dbe ,empty_list, header_fert_doc , head_cols_fert_doc , fert_data_cols_in])

def fill_summary_placeholders(head_cols_fert_doc, fert_data_cols_in, dbe_cols, fert_cols, area):
    dbe_per_ha = dbe_cols[0][10] if dbe_cols else None
    dbe_total = dbe_per_ha * area if dbe_per_ha is not None else None

    n_available_per_ha = sum(
        (row[6] or 0) for row in fert_cols
    )
    n_available_total = sum(
        (row[7] or 0) for row in fert_cols
    )

    replacements = {
        "Summe DBE / ha_PLACEHOLDER": dbe_per_ha,
        "Summe DBE / Fläche_PLACEHOLDER": dbe_total,

        "Aufgebr. N Pflanzenverfügbar / ha_PLACEHOLDER": n_available_per_ha,
        "Aufgebr. N Pflanzenverfügbar / Fläche_PLACEHOLDER": n_available_total,

        "Aufgebr. N-org kg / ha_PLACEHOLDER": sum(
            (row[4] or 0) for row in fert_cols
        ),
        "Aufgebr. N-org kg / Fläche_PLACEHOLDER": sum(
            (row[5] or 0) for row in fert_cols
        ),

        "Abschlag Düngung Folgejahr kg / ha_PLACEHOLDER" : sum(
            (row[4] or 0) for row in fert_cols
        ) / 10
    }

    filled_header = [
        replacements.get(value, value)
        for value in head_cols_fert_doc
    ]

    filled_fert_rows = [
        [
            replacements.get(value, value)
            if isinstance(value, str)
            else value
            for value in row
        ]
        for row in fert_data_cols_in
    ]

    return filled_header, filled_fert_rows

def fill_top_rows(schlag_data, farm_metadata):
    replacements = {
        "DÜNGEJAHR_PLACEHOLDER": farm_metadata.get("Fert_Year"),
        "BETRIEBSNUMMER_PLACEHOLDER": farm_metadata.get("farm_id"),
        "BETRIEB_PLACEHOLDER": farm_metadata.get("farm_name"),
        "SCHLAG_PLACEHOLDER": schlag_data.get("Schlag"),
        "FELDBLOCKNUMMER_PLACEHOLDER": schlag_data.get("Feldblock-Nummer"),
        "SCHLAGGRÖßE_PLACEHOLDER": schlag_data.get("Größe in ha"),
        "VORJAHRESKULTUR_PLACEHOLDER": schlag_data.get("Vorjahreskultur"),
        "ZWISCHENFRUCHT_PLACEHOLDER": schlag_data.get("Zwischenfrucht"),
    }

    def replace_row(row):
        return [replacements.get(value, value) for value in row]

    return [
        replace_row(top_col_1),
        replace_row(top_col_2),
        replace_row(top_col_3),
    ]


def add_rows(dbe_cols, fert_cols, top_rows, area):
    filled_header, filled_fert_rows = fill_summary_placeholders(
        head_cols_fert_doc=head_cols_fert_doc,
        fert_data_cols_in=fert_data_cols_in,
        dbe_cols=dbe_cols,
        fert_cols=fert_cols,
        area=area,
    )

    all_rows = [
        *top_rows,
        [None] * 11,
        header_dbe,
        head_cols_dbe,
        *dbe_cols,
        [None] * 11,
        header_fert_doc,
        filled_header,
        *fill_fert_rows(fert_cols, template_rows=filled_fert_rows),
    ]

    return pd.DataFrame(all_rows)

"""
def add_rows(dbe_cols, fert_cols, top_rows):
    all_rows = [
        *top_rows,
        [None] * 11,
        header_dbe,
        head_cols_dbe,
        *dbe_cols,
        [None] * 11,
        header_fert_doc,
        head_cols_fert_doc,
        *fill_fert_rows(fert_cols),
    ]

    return pd.DataFrame(all_rows)
"""
def get_dbe_rows(schlag_data):
    dbe_args = schlag_data.get("DBE_Args")

    if not dbe_args:
        return []

    h = dbe_args["Hauptfrucht"]

    return [[
        h.get("Datum"),
        h.get("Kultur"),
        h.get("Ertrag laut DüV"),
        h.get("Durchschnittsertrag 5 Jahre Betrieb"),
        h.get("N-Bedarfswert"),
        h.get("Abschlag Ertragsdifferenz"),
        h.get("N_min Probe / Richtwert"),
        h.get("Standort / Humus"),
        h.get("Abschlag Vorfrucht"),
        h.get("Abschlag Zwischenfrucht"),
        schlag_data.get("Stickstoffbedarf durch Dünger in kg / ha"),
    ]]


def get_fert_rows(schlag_id, schlag_data):
    fert_events = st.session_state.fert_collection.get(
        schlag_id, {}
    )

    area = schlag_data["Größe in ha"]
    rows = []

    for event in fert_events.values():
        unit = event["Einheit"]
        amount = event[f"Düngemente in {unit} / ha"]
        n_total = event[f"Stickstoff Gesamt in {unit} / ha"]
        n_available = event[
            f"Stickstoff Pflanzenverfügbar in {unit} / ha"
        ]

        rows.append([
            event["Datum"],
            event["Düngetyp"],
            event["Düngetyp"],  # Temporary: replace with nutrient carrier
            f"{amount} {unit} / ha",
            n_total,
            n_total * area,
            n_available,
            n_available * area,
        ])

    return rows

def fill_fert_rows(fert_cols, template_rows=None):
    if template_rows is None:
        template_rows = fert_data_cols_in

    n_rows = max(len(template_rows), len(fert_cols))
    rows = []

    for i in range(n_rows):
        row = (
            template_rows[i].copy()
            if i < len(template_rows)
            else [None] * 11
        )

        # Fill the eight fertilizer-event columns.
        for j in range(8):
            row[j] = (
                fert_cols[i][j]
                if i < len(fert_cols)
                else None
            )

        rows.append(row)

    return rows
if __name__ == '__main__':
                # 
    dbe_cols = [['21.10.26' , 'Weizen' , '100' , '50' ,  '200' , '10' , '30' , '0', '-15' , '0 / 0' , '130'],
                ['15.10.26' , 'Weizen' , '100' , '50' ,  '200' , '10' , '-37' , '-20', '-15' , '0 / -20' , '100']]

    fert_cols = [[None]*9]

    test = add_rows(dbe_cols=dbe_cols)

    
            


