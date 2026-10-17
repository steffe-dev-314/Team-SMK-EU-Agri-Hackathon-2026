import streamlit as st 
import streamlit as st

st.set_page_config(page_title="FAQ - Easy", layout="wide")

st.logo('.streamlit/logo.png' , size = 'large')

st.title("Wichtige Fragen und Antworten zum SMK-Rechner für Dünger (DBE)")

# 1. Regeln und Praxis für die Dünger-Berechnung

st.header("1. Regeln und Praxis für die Dünger-Berechnung")

with st.expander("Was ist die Düngebedarfsermittlung (DBE) überhaupt und warum muss ich sie machen?"):
    st.markdown("""
    Das Gesetz schreibt vor, dass du vorab genau berechnen musst, wie viel Dünger deine Pflanzen wirklich brauchen. Das nennt man Düngebedarfsermittlung (kurz: DBE). Du musst das ausrechnen und aufschreiben, bevor du auf den Acker fährst. So hältst du dich an die gesetzlichen Regeln und vermeidest Strafen.
    """)

with st.expander("Muss ich die Berechnung für den ganzen Hof auf einmal machen oder für jedes Feld einzeln?"):
    st.markdown("""
    Du musst das für jedes einzelne Feld (den sogenannten Schlag) ausrechnen. Denn jedes Feld ist anders: Es hat eine andere Größe, einen anderen Boden und letztes Jahr wuchsen dort vielleicht andere Pflanzen.
    """)

with st.expander("Welche Daten brauche ich, um die DBE für ein Feld auszufüllen?"):
    st.markdown("""
    Viele Daten hast du wahrscheinlich schon, zum Beispiel von alten Bodenproben. Für die Berechnung brauchst du diese Angaben:

    - **Infos zum Feld:** Wie heißt das Feld, welche Nummer hat es und wie groß ist es?
    - **Pflanzen:** Was möchtest du dort anbauen (zum Beispiel Weizen)? Und was wuchs dort im letzten Jahr?
    - **Ertrag:** Wie hoch war deine Ernte auf diesem Feld im Durchschnitt der letzten fünf Jahre?
    - **Bodenwerte:** Was steht in deinen Bodenanalysen? Wie viel Humus gibt es dort?
    - **Alter Dünger:** Hast du letztes Jahr organischen Dünger (wie Gülle) auf das Feld gefahren? Das muss man bei der neuen Berechnung abziehen.
    """)

with st.expander("Was ist der Unterschied zwischen der Berechnung (DBE) und der Dokumentation?"):
    st.markdown("""
    - **Vor dem Düngen (Berechnung):** Du rechnest aus, wie viel Dünger du höchstens auf das Feld fahren darfst.
    - **Nach dem Düngen (Dokumentation):** Du schreibst genau auf, was du getan hast. Du notierst das Datum, den Namen des Düngers, die Menge und wie viel Stickstoff am Ende auf dem Acker gelandet ist.
    """)

# 2. Arbeiten mit dem SMK-Programm im Alltag

st.header("2. Arbeiten mit dem SMK-Programm im Alltag")

with st.expander("Warum sollte ich von Zettel und Stift oder Excel auf SMK wechseln?"):
    st.markdown("""
    Zurzeit nutzen viele Betriebe für diese Aufgaben noch Papier oder einfache Tabellenkalkulationen. Das macht viel Arbeit. Du musst Dinge doppelt aufschreiben und verlierst Zeit. Mit dem Programm SMK geht das leichter: Du gibst deine Daten nur einmal ein. Das Programm merkt sich die Daten, rechnet alles aus und erstellt das fertige Dokument für dich ganz automatisch.
    """)

with st.expander("Ich kenne mich am Computer nicht gut aus – ist das Programm kompliziert?"):
    st.markdown("""
    Nein, es ist sehr einfach. Wir wissen, dass viele Landwirte unkomplizierte Lösungen ohne viel Schnickschnack suchen. Wir haben alles Wichtige auf einer einzigen, sehr übersichtlichen Seite gesammelt. Du brauchst kein Vorwissen. So sparst du dir das Geld für teure externe Berater, auf die derzeit noch ein Großteil der Betriebe zurückgreifen muss.
    """)

with st.expander("Kann ich Daten, die ich schon habe, einfach weiterverwenden?"):
    st.markdown("""
    Ja. Oft arbeiten verschiedene Programme auf Höfen nicht gut zusammen. SMK ist anders. Wenn du Daten (wie eine Bodenanalyse) schon in einem anderen Programm hast, kann SMK diese Daten einfach übernehmen. Du musst nichts doppelt abtippen.
    """)

# 3. Kosten, Daten-Schutz und offene Technik

st.header("3. Kosten, Daten-Schutz und offene Technik (Open Source)")

with st.expander("Was kostet das SMK-Programm? Gibt es versteckte Kosten?"):
    st.markdown("""
    Das Programm kostet dich gar nichts. Es gibt keine teuren Lizenzen oder Verträge. Wir finden: Gute Technik für Landwirte muss kostenlos sein und du sollst dich nicht von einer einzigen großen Software-Firma abhängig machen. Wir bezahlen unsere Arbeit durch staatliche Fördergelder und durch freiwillige Schulungen, die wir anbieten.
    """)

with st.expander("Was bedeutet „Open Source“ für mich als Bauer?"):
    st.markdown("""
    „Open Source“ heißt übersetzt „offene Quelle“. Das bedeutet, dass jeder Fachmann sehen kann, wie unser Programm im Hintergrund geschrieben ist. Das hat zwei Vorteile für dich:

    - **Leicht anzupassen:** Man kann das Programm gut verändern, falls dein Hof besondere Anforderungen hat.
    - **Du bleibst unabhängig:** Du bekommst ein starkes Werkzeug für deinen Hof, ohne dass du viel Geld an Firmen zahlen musst.
    """)

with st.expander("Was passiert mit meinen privaten Daten vom Hof?"):
    st.markdown("""
    Wir wissen, dass deine Daten wertvoll sind und niemanden etwas angehen. Deine Daten gehören nur dir. Weil unser Programm komplett offen ist (Open Source), gibt es keine Geheimnisse oder versteckten Hintertüren. Jeder kann jederzeit überprüfen, dass wir deine Daten sicher behandeln und nicht heimlich ins Internet weiterleiten.
    """)