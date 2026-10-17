import streamlit as st

st.set_page_config(page_title="FAQ", layout="wide")

st.logo('.streamlit/logo.png' , size = 'large')

st.title("Häufig gestellte Fragen (FAQ) – SMK Düngebedarfsermittlung (DBE)")

# 1. Rechtliche Grundlagen & Praxis der DBE

st.header("1. Rechtliche Grundlagen & Praxis der Düngebedarfsermittlung (DBE)")

with st.expander("Was ist die Düngebedarfsermittlung (DBE) überhaupt und warum muss ich sie machen?"):
    st.markdown("""
    Die Düngebedarfsermittlung ist die gesetzlich vorgeschriebene Kalkulation, wie viel Stickstoff-Düngebedarf deine Kulturen auf einem bestimmten Acker tatsächlich haben. Bevor du mit der Düngung startest, musst du diesen Bedarf verbindlich ermitteln und dokumentieren, um die gesetzlichen Vorgaben (Compliance) zu erfüllen.
    """)

with st.expander("Muss ich die Berechnung für meinen gesamten Hof auf einmal oder für jedes Feld einzeln machen?"):
    st.markdown("""
    Du musst die DBE für jeden Schlag bzw. jede Bewirtschaftungseinheit einzeln erstellen. Jedes Feld hat eine eigene Flächengröße, andere Vorjahreskulturen, spezifische Bodenanalysen und unterschiedliche Ertragsdurchschnitte.
    """)

with st.expander("Welche Daten brauche ich konkret, um eine DBE für einen Schlag auszufüllen?"):
    st.markdown("""
    Viele dieser Informationen liegen auf deinem Betrieb bereits vor, zum Beispiel in Form von Bodenanalysen. Für eine vollständige Stickstoff-Düngebedarfsermittlung (wie nach den Vorgaben der Landwirtschaftskammer Nordrhein-Westfalen) benötigst du folgende Angaben:

    - **Flächendaten:** Den Namen des Schlags bzw. der Bewirtschaftungseinheit, die Feldblocknummer sowie die Schlaggröße in Hektar.
    - **Kultur & Fruchtfolge:** Die geplante Hauptkultur (z. B. Winterweizen), die Vorjahreskultur sowie eventuelle Zwischenfrüchte.
    - **Ertragsniveau:** Deinen durchschnittlichen Betriebsertrag der letzten fünf Jahre im Vergleich zum Ertrag laut Düngeverordnung (DüV), um Zu- oder Abschläge bei der Ertragsdifferenz zu berechnen.
    - **Bodenwerte:** Ergebnisse deiner Bodenanalysen sowie Angaben zu Standort und Humus für die entsprechenden Abschläge.
    - **Nachlieferung aus dem Vorjahr:** Angaben zur organischen Düngung aus dem Vorjahr, da hierfür ein Abschlag angerechnet wird.
    """)

with st.expander("Was ist der Unterschied zwischen der Düngebedarfsermittlung (DBE) und der Düngedokumentation?"):
    st.markdown("""
    - **Vor der Düngung (Bedarfsermittlung):** Hier berechnest du über den Stickstoff-Bedarfswert sowie die gesetzlichen Zu- und Abschläge deinen maximal zulässigen Stickstoff-Düngebedarf in Kilogramm pro Hektar.
    - **Nach der Düngung (Dokumentation):** Sobald du gedüngt hast, trägst du in die Dokumentation der Stickstoffdüngung das genaue Datum, das verwendete Düngemittel (z. B. Milchviehgülle), die ausgebrachte Menge sowie die aufgebrachte Stickstoffmenge pro Hektar und Fläche ein.
    """)

# 2. Arbeiten mit dem SMK DBE-Rechner

st.header("2. Arbeiten mit dem SMK DBE-Rechner im Hofalltag")

with st.expander("Warum sollte ich von Zettel und Stift oder einer Excel-Tabelle auf SMK wechseln?"):
    st.markdown("""
    Aktuell nutzen bei der Dokumentation noch 51 % der Betriebe Papier und 57 % greifen auf Tabellenkalkulationen (Spreadsheets) oder gescannte Dokumente zurück. Das führt zu manuellen Prozessen, doppelten Formularen und verlorener Zeit, die für die eigentliche Landwirtschaft fehlt. Mit SMK hast du einen durchgehenden Workflow: Du erfasst deine Hofdaten nur ein einziges Mal, kannst sie wiederverwenden und dir das Dokument ausgeben lassen.
    """)

with st.expander("Ich bin kein IT-Profi – ist das Programm kompliziert zu bedienen?"):
    st.markdown("""
    Nein. Viele Landwirte wünschen sich eine unkomplizierte Anwendung ohne hohe Einstiegshürden. Unsere Plattform bündelt deine gesamte Dünge-Dokumentation auf einem einzigen, intuitiven Dashboard. So sparst du dir das Geld für teure externe Beratungsdienste, auf die derzeit 78 % der Betriebe zurückgreifen.
    """)

with st.expander("Kann ich meine bestehenden Hofdaten weiterverwenden?"):
    st.markdown("""
    Ja. Viele Höfe leiden heute unter getrennten Systemen, die nicht miteinander kommunizieren. Unser Ansatz setzt auf eine gemeinsame Plattform für all deine Daten sowie auf Interoperabilität mit bestehenden Open-Source-Plattformen, damit vorhandene Informationen wie Bodenanalysen direkt genutzt werden können.
    """)

# 3. Kosten, Datenschutz & Open Source

st.header("3. Kosten, Datenschutz & Open Source")

with st.expander("Was kostet mich der DBE-Rechner von SMK? Gibt es versteckte Abo-Fallen?"):
    st.markdown("""
    Die Software ist komplett kostenlos und frei von teuren Lizenzgebühren. Wir sind überzeugt, dass die Digitalisierung in der Landwirtschaft kein hohes Preisschild haben darf und dich nicht in die Abhängigkeit eines einzelnen Anbieters („Vendor Lock-in“) treiben sollte. Um das Werkzeug für Landwirte dauerhaft kostenfrei zu halten, setzen wir zur Finanzierung auf Förderprogramme (wie NOSTRADAMUS oder das BMDS-Förderprogramm) sowie auf begleitende Schulungen und Workshops.
    """)

with st.expander("Was bedeutet „Open Source“ für mich als Landwirt?"):
    st.markdown("""
    Open Source bedeutet, dass der Quellcode unserer Software öffentlich einsehbar ist. Das bietet dir zwei zentrale Vorteile:

    - **Anpassbarkeit:** Der öffentliche Quellcode lässt sich flexibel an individuelle Bedürfnisse anpassen.
    - **Unabhängigkeit:** Du erhältst ein wirkungsvolles Werkzeug ohne hohe Softwarekosten oder Herstellerbindung.
    """)

with st.expander("Was passiert mit meinen sensiblen Hof- und Bodendaten?"):
    st.markdown("""
    Uns ist bewusst, dass viele Landwirte große Bedenken hinsichtlich der Datensicherheit haben und ihre Betriebsdaten privat halten möchten. Unsere Lösung richtet sich nach den Zielen der EU und stellt deine digitale Souveränität in den Mittelpunkt. Dank des offenen Quellcodes ist jederzeit transparent nachvollziehbar, wie deine Daten verarbeitet werden.
    """)