from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.page import PageMargins
from datetime import datetime, date

import streamlit as st

def get_finished_parcels(schlag_collection): 
    finished_parcels = []
    for s_id , s in schlag_collection.items(): 
        if "Düngeinformation" in s.keys() and s['Düngeinformation']:
            finished_parcels.append(s_id)
    return finished_parcels            

def build_dbe_excel(schlag_collection , metadata):
    """Create a formatted DBE report from the saved parcel data."""

    wb = Workbook()
    summary = wb.active
    summary.title = "Übersicht"

    green = "245640"
    light_green = "E2F0E8"
    pale = "F5F8F5"
    white = "FFFFFF"
    grey = "667085"
    border_color = "D0D5DD"

    thin = Side(style="thin", color=border_color)

    def setup_sheet(ws):
        ws.sheet_view.showGridLines = False
        ws.freeze_panes = "A5"
        ws.sheet_properties.pageSetUpPr.fitToPage = True
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0
        ws.page_setup.orientation = "landscape"
        ws.page_setup.paperSize = ws.PAPERSIZE_A4
        ws.page_margins = PageMargins(
            left=0.25, right=0.25,
            top=0.5, bottom=0.5
        )
        ws.oddFooter.center.text = "DBE-Bericht"
        ws.oddFooter.right.text = "Seite &P von &N"

    def title_block(ws, title, subtitle, last_col):
        ws.merge_cells(
            start_row=1, start_column=1,
            end_row=1, end_column=last_col
        )
        ws["A1"] = title
        ws["A1"].font = Font(
            name="Aptos Display", size=18,
            bold=True, color=white
        )
        ws["A1"].fill = PatternFill("solid", fgColor=green)
        ws["A1"].alignment = Alignment(vertical="center")
        ws.row_dimensions[1].height = 36

        for col in range(1, last_col + 1):
            ws.cell(1, col).fill = PatternFill(
                "solid", fgColor=green
            )

        ws.merge_cells(
            start_row=2, start_column=1,
            end_row=2, end_column=last_col
        )
        ws["A2"] = subtitle
        ws["A2"].font = Font(
            size=10, italic=True, color=grey
        )
        ws.row_dimensions[2].height = 24

    def write_table(ws, headers, rows, table_name):
        header_row = 4

        for col, header in enumerate(headers, 1):
            cell = ws.cell(header_row, col, header)
            cell.fill = PatternFill("solid", fgColor=green)
            cell.font = Font(bold=True, color=white)
            cell.alignment = Alignment(
                wrap_text=True, vertical="center"
            )
            cell.border = Border(bottom=thin)

        ws.row_dimensions[header_row].height = 42

        for row_idx, values in enumerate(rows, 5):
            for col_idx, value in enumerate(values, 1):
                cell = ws.cell(row_idx, col_idx, value)
                cell.fill = PatternFill(
                    "solid",
                    fgColor=white if row_idx % 2 else pale
                )
                cell.border = Border(bottom=thin)
                cell.alignment = Alignment(
                    vertical="top", wrap_text=True
                )

                if isinstance(value, (int, float)):
                    cell.number_format = '#,##0.00'

        last_col = get_column_letter(len(headers))
        last_row = max(4, 4 + len(rows))


        if rows:
            tab = Table(
                displayName=table_name,
                ref=f"A4:{last_col}{last_row}"
            )
            tab.tableStyleInfo = TableStyleInfo(
                name="TableStyleMedium4",
                showRowStripes=True,
                showColumnStripes=False
            )
            ws.add_table(tab)

        ws.freeze_panes = "A5"
        ws.print_title_rows = "1:4"


        for col_idx, header in enumerate(headers, 1):
            # Width based on header, with a sensible maximum.
            width = min(max(len(str(header)) + 3, 15), 32)
            ws.column_dimensions[
                get_column_letter(col_idx)
            ].width = width

    # --------------------------------------------------
    # 1. Collect saved parcel and DBE data
    # --------------------------------------------------

    parcel_rows = []
    detail_rows = []
    fertilizer_rows = []

    for s_id, s in schlag_collection.items():

        area = s.get("Größe in ha")
        area = float(area) if area is not None else None

        dbe_result = s.get(
            "Stickstoffbedarf durch Dünger in kg / ha"
        )
        args = s.get("DBE_Args", {})

        main_crop = args.get("Hauptfrucht", {})
        catch_crop = args.get("Zwischenfrucht", {})

        # Keep the DBE result as saved by the application.
        n_total_ha = 0.0
        n_total_parcel = 0.0
        fertilizer_data = s.get("Düngeinformation", {}) or {}

        for d_id, f in fertilizer_data.items():
            if not isinstance(f, dict):
                continue

            amount_key = next(
                (
                    k for k in f
                    if k.startswith("Düngemente in ")
                ),
                None
            )
            total_key = next(
                (
                    k for k in f
                    if k.startswith(
                        "Stickstoff Gesamt in "
                    )
                ),
                None
            )
            available_key = next(
                (
                    k for k in f
                    if k.startswith(
                        "Stickstoff Pflanzenverfügbar in "
                    )
                ),
                None
            )

            total_ha = f.get(total_key) if total_key else None
            available_ha = (
                f.get(available_key) if available_key else None
            )

            if isinstance(total_ha, (int, float)):
                n_total_ha += total_ha
                if area is not None:
                    n_total_parcel += total_ha * area

            fertilizer_rows.append([
                s.get("Schlag"),
                s.get("Feldblock-Nummer"),
                area,
                d_id,
                f.get("Datum"),
                f.get("Düngetyp"),
                f.get("Einheit"),
                f.get(amount_key) if amount_key else None,
                total_ha,
                total_ha * area
                if isinstance(total_ha, (int, float))
                and area is not None else None,
                available_ha,
                available_ha * area
                if isinstance(available_ha, (int, float))
                and area is not None else None,
            ])

        # One row per parcel in the main DBE sheet.
        parcel_rows.append([
            s_id,
            s.get("Schlag"),
            s.get("Feldblock-Nummer"),
            area,
            s.get("Kultur"),
            s.get("Vorjahreskultur"),
            s.get("Zwischenfrucht"),
            s.get("Datum der Aussaat"),
            s.get("Datum der Aussaat Zwischenfrucht"),
            main_crop.get("Ertrag laut DüV"),
            main_crop.get("Durchschnittsertrag 5 Jahre Betrieb"),
            main_crop.get("N-Bedarfswert"),
            main_crop.get("Abschlag Ertragsdifferenz"),
            main_crop.get("N_min Probe / Richtwert"),
            main_crop.get("Standort / Humus"),
            main_crop.get("Abschlag Vorfrucht"),
            main_crop.get("Abschlag Zwischenfrucht"),
            dbe_result,
            n_total_ha,
            n_total_parcel if area is not None else None,
            n_total_ha / 10,
            (
                "DBE vorhanden"
                if dbe_result is not None
                else "DBE noch nicht berechnet"
            ),
        ])

        # Long-format audit trail: one row per stored parameter.
        for section, parameters in args.items():
            if not isinstance(parameters, dict):
                continue

            for parameter, value in parameters.items():
                detail_rows.append([
                    s.get("Schlag"),
                    s.get("Feldblock-Nummer"),
                    section,
                    parameter,
                    value.isoformat()
                    if isinstance(value, (date, datetime))
                    else value,
                ])

    # --------------------------------------------------
    # 2. Summary sheet
    # --------------------------------------------------

    setup_sheet(summary)
    title_block(
        summary,
        "Düngebedarfsermittlung | Stickstoff",
        "Bericht und Prüfunterlagen aus den gespeicherten DBE-Daten",
        4
    )

    summary["A4"] = "BERICHTSINFORMATIONEN"
    summary["A4"].font = Font(bold=True, color=green, size=12)


    for row, (label, value) in enumerate(metadata, 5):
        summary.cell(row, 1, label).font = Font(bold=True)
        summary.cell(row, 1).fill = PatternFill(
            "solid", fgColor=light_green
        )
        if isinstance(value, (date, datetime)):
            value = (
                value.strftime("%d.%m.%Y")
                if isinstance(value, date)
                else value
            )
        summary.cell(row, 2, value)

    completed = sum(
        1 for s in schlag_collection.values()
        if s.get("Stickstoffbedarf durch Dünger in kg / ha")
        is not None
    )

    total_area = sum(
        float(s["Größe in ha"])
        for s in schlag_collection.values()
        if isinstance(s.get("Größe in ha"), (int, float))
    )

    summary["A11"] = "KENNZAHLEN"
    summary["A11"].font = Font(bold=True, color=green, size=12)

    metrics = [
        ("Erfasste Schläge", len(schlag_collection)),
        ("Schläge mit DBE", completed),
        ("Gesamte Schlagfläche (ha)", total_area),
        ("Dokumentierte Düngungsereignisse", len(fertilizer_rows)),
    ]

    for row, (label, value) in enumerate(metrics, 12):
        summary.cell(row, 1, label)
        summary.cell(row, 2, value)
        summary.cell(row, 1).font = Font(bold=True)
        summary.cell(row, 1).fill = PatternFill(
            "solid", fgColor=light_green
        )
        summary.cell(row, 2).number_format = '#,##0.00'

    summary["A18"] = "HINWEISE"
    summary["A18"].font = Font(bold=True, color=green, size=12)

    notes = [
        "Die DBE-Ergebnisse werden aus der Anwendung übernommen.",
        "Leere Werte sind nicht automatisch gleich null.",
        "N-Bedarfswerte sind je Hektar angegeben; "
        "Schlaggesamtsummen sind gesondert ausgewiesen.",
        "Die Arbeitsmappe dokumentiert die gespeicherten Werte; "
        "rechtliche Vollständigkeit ist separat zu prüfen.",
    ]

    for row, note in enumerate(notes, 19):
        summary.cell(row, 1, f"• {note}")
        summary.merge_cells(
            start_row=row, start_column=1,
            end_row=row, end_column=4
        )
        summary.cell(row, 1).alignment = Alignment(wrap_text=True)
        summary.row_dimensions[row].height = 28

    summary.column_dimensions["A"].width = 38
    summary.column_dimensions["B"].width = 28
    summary.column_dimensions["C"].width = 18
    summary.column_dimensions["D"].width = 18

    # --------------------------------------------------
    # 3. DBE per parcel
    # --------------------------------------------------

    dbe = wb.create_sheet("DBE je Schlag")
    setup_sheet(dbe)
    title_block(
        dbe,
        "DBE je Schlag",
        "Eingaben, Korrekturen und berechnete Stickstoffbedarfe",
        22
    )

    dbe_headers = [
        "Schlag-ID", "Schlag", "Feldblocknummer", "Fläche (ha)",
        "Kultur", "Vorjahreskultur", "Zwischenfrucht",
        "Aussaat Hauptfrucht", "Aussaat Zwischenfrucht",
        "Ertrag laut DüV (dt/ha)", "5-Jahres-Ertrag (dt/ha)",
        "N-Bedarfswert (kg N/ha)",
        "Korrektur Ertragsdifferenz (kg N/ha)",
        "Nmin (kg N/ha)", "Humuskorrektur (kg N/ha)",
        "Abschlag Vorfrucht (kg N/ha)",
        "Abschlag Zwischenfrucht (kg N/ha)",
        "Düngebedarf (kg N/ha)",
        "N gesamt Düngung (kg N/ha)",
        "N gesamt Düngung (kg N/Schlag)",
        "Folgejahr-Abschlag (kg N/ha)",
        "Status",
    ]

    write_table(dbe, dbe_headers, parcel_rows, "DBEParcelTable")

    # --------------------------------------------------
    # 4. Fertilizer documentation
    # --------------------------------------------------

    fert = wb.create_sheet("Düngungsmaßnahmen")
    setup_sheet(fert)
    title_block(
        fert,
        "Dokumentation der Stickstoffdüngung",
        "Erfasste Düngungsereignisse und Stickstoffmengen",
        12
    )

    fert_headers = [
        "Schlag", "Feldblocknummer", "Fläche (ha)",
        "Düngungs-ID", "Datum", "Düngemittel", "Einheit",
        "Düngermenge je ha", "N gesamt (kg N/ha)",
        "N gesamt (kg N/Schlag)",
        "N verfügbar (kg N/ha)",
        "N verfügbar (kg N/Schlag)",
    ]

    write_table(
        fert, fert_headers, fertilizer_rows,
        "FertilizerTable"
    )

    # --------------------------------------------------
    # 5. Audit details
    # --------------------------------------------------

    audit = wb.create_sheet("Berechnungsdetails")
    setup_sheet(audit)
    title_block(
        audit,
        "Berechnungsdetails",
        "Gespeicherte DBE_Args · Eingaben und Parameter je Schlag",
        5
    )

    audit_headers = [
        "Schlag", "Feldblocknummer", "Berechnungsteil",
        "Parameter", "Gespeicherter Wert",
    ]

    write_table(
        audit, audit_headers, detail_rows,
        "AuditDetailTable"
    )

    # --------------------------------------------------
    # 6. Workbook polish and export
    # --------------------------------------------------

    for ws in wb.worksheets:
        ws.sheet_view.zoomScale = 85
        ws.sheet_properties.tabColor = green
        ws.sheet_properties.pageSetUpPr.fitToPage = True

    wb.properties.title = "DBE-Bericht Stickstoff"
    wb.properties.subject = "Düngebedarfsermittlung und Prüfunterlagen"
    wb.properties.creator = "DBE-Anwendung"

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return output.getvalue()
