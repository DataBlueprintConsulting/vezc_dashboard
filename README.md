## ✈️ VEZC Urenadministratie

Een handige Streamlit-applicatie voor leden van de **Venlo Eindhoven ZweefvliegClub** om vlieguren en starts eenvoudig te analyseren en visualiseren op basis van hun Startadministratie.

<img width="1512" alt="image" src="https://github.com/user-attachments/assets/6c05874a-bdb1-420f-847d-65fbeafec699" />

---

### 🔍 Features

- 📥 Upload je Excel-bestand vanuit Startadministratie
- 📊 Filter op vliegtuigtype, veld, datum, registratie en startmethode
- 📈 Grafieken: aantal starts, vlieguren, taartdiagrammen
- 🗺️ Kaart met starts per veld
- 🕒 Laatste vluchtinformatie per vliegtuigtype
- ⬇️ Download gefilterde gegevens als Excel

---

### 🛠️ Installatie

Zorg dat je Python en pip geïnstalleerd hebt. Daarna:

```bash
git clone https://github.com/DataBlueprintConsulting/vezc_dashboard.git
cd vezc_dashboard
pip install -r requirements.txt
```

---

### 🚀 Start de app

```bash
streamlit run home.py
```

De app draait dan op `http://localhost:8501`.

---

### 📁 Bestandsstructuur

```bash
vezc-dashboard/
├── home.py                 # Hoofd Streamlit app
├── vezc.jpg               # Logo afbeelding
├── requirements.txt       # Benodigde Python libraries
└── README.md              # Deze uitleg
```

---

### 📄 Vereiste Excel-kolommen

Zorg dat je Excel-bestand minimaal de volgende kolommen bevat:

- `Datum`
- `Veld`
- `Type`
- `Registratie`
- `Startmethode`
- `Vluchtduur`

---

### 📍 Kaartfunctionaliteit

De applicatie toont een kaart met het aantal starts per veld. Deze functie werkt op basis van een handmatig gekoppelde lijst van vliegvelden en hun coördinaten. Uitbreiding met extra velden is mogelijk in `veld_coords`.

---

### 💡 Mogelijke uitbreidingen

- Inloggen per lid
- Interactieve grafieken met filters in de grafiek
- Live koppeling met Startadmin API
- Mobiele versie

---

### 📸 Screenshots

<img width="1512" alt="image" src="https://github.com/user-attachments/assets/83349da5-017c-432f-a823-95203bec08fb" />
<img width="1512" alt="image" src="https://github.com/user-attachments/assets/543bf444-7f75-4898-8fd7-11e7544827cb" />
<img width="1512" alt="image" src="https://github.com/user-attachments/assets/3e3affcd-3fa8-4fcc-86ff-5e411932bd3f" />
<img width="1512" alt="image" src="https://github.com/user-attachments/assets/53ae9afc-cb9b-4d5b-8acc-5e9394908f2f" />

---

### 🧑‍💻 Ontwikkelaar

Gemaakt door Adam Asbai Halifa voor de Venlo Eindhoven ZweefvliegClub.

---

### 📜 Licentie

MIT License

---

## ✅ requirements.txt

Als je dit bestand nog niet hebt, voeg dit toe:

```txt
streamlit
pandas
numpy
openpyxl
plotly
```
